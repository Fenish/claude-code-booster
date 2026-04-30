---
name: find-skills
description: Search for agent skills across skills.sh and skillfish registries
argument-hint: "<search query>"
allowed-tools: ["Bash"]
---

# Find Skills Command

When the user runs `/find-skills <query>`:

## 1. Get the query

If no query is provided, use AskUserQuestion to ask what they're looking for.

## 2. Search both registries in the background

Run both commands with `run_in_background: true` to keep the chat clean:

```bash
npx skills find "<query>" || true
```

```bash
npx skillfish search "<query>" --json --limit 10 || true
```

The `|| true` ensures exit code 0 so background tasks report as completed (npx sometimes exits with 127 even on success). You'll be notified when each completes. If one CLI produces no results, silently use results from the other.

## 3. Parse results

The skillfish `--json` output:

```json
{
  "success": true,
  "results": [
    {
      "name": "Skill Name",
      "slug": "skill-slug",
      "description": "What it does",
      "url": "https://www.skill.fish/skill/skill-slug",
      "stars": 0
    }
  ],
  "total_count": 123
}
```

The `npx skills find` output is plain text — parse skill names, sources, and install counts from it.

## 4. Rank and present results

Merge results from both registries into a single list sorted by popularity descending:

- skills.sh: sort by install count (higher = better)
- skillfish: sort by stars (higher = better)
- When comparing across registries, skills.sh install counts take priority over skillfish stars since skillfish stars are often 0

Use AskUserQuestion to let the user pick which skill(s) to install.

- header: "Install skill"
- question: "Which skill(s) would you like to install?"
- multiSelect: true
- options: top 3 results + "Load more" as the 4th option
  - label: skill name
  - description: registry label + source/description + install count or stars. Use "skills.sh" or "skillfish" as the registry label (never say "mcpmarket").
  - The 4th option MUST always be: label: "Load more", description: "Show more results from both registries"

Example:

```sh
options:
  - label: "markdownlint-integration"
    description: "skills.sh — thebushidocollective/han (45 installs)"
  - label: "markdownlint-custom-rules"
    description: "skills.sh — thebushidocollective/han (33 installs)"
  - label: "markdown-formatting"
    description: "skills.sh — denolfe/dotfiles (31 installs)"
  - label: "Load more"
    description: "Show more results from both registries"
```

## 5. Handle "Load more"

If the user picks "Load more":

1. Show the NEXT batch of 3 results (skip ones already shown) + another "Load more" option if there are still more.
2. If you've exhausted the initial results, run both searches again with higher limits (`--limit 30` for skillfish) to get more.
3. Keep paginating until the user picks a skill or there are no more results.

## 6. Handle "Other" (new search)

If the user picks "Other" and types text, treat that text as a new search query. Go back to step 2 and run both searches with the new query. Reset pagination (start fresh with the new results).

## 7. Install selected skills

For each skill the user selected, run the appropriate install command:

```bash
# For skills.sh results
npx skills add <owner/repo@skill> -g -y

# For skillfish results
npx skillfish add <slug>
```

Run installs sequentially and report success/failure for each.

## 8. No results

If both registries return nothing, tell the user and suggest alternative search terms or offer to help directly.
