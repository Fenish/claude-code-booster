---
name: find-skills
description: Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. Use this skill whenever the user is looking for functionality that might exist as an installable skill, mentions wanting to search for tools or workflows, or asks about extending agent capabilities. Even if they don't say "skill" explicitly, trigger when they describe a task that sounds like it could be handled by a specialized skill.
---

# Find Skills

Search for agent skills across multiple registries and present the best options to the user.

## Registries

There are two skill registries to search. Always query both to get the widest coverage.

### skills.sh (via `npx skills`)

```bash
npx skills find "<query>"
```

Browse: https://skills.sh/

Install: `npx skills add <owner/repo@skill> -g -y`

### skillfish (via `npx skillfish`)

```bash
npx skillfish search "<query>" --json --limit 10
```

Browse: https://www.skill.fish/

Install: `npx skillfish add <slug>`

## Process

### 1. Understand What the User Needs

Identify the domain (React, testing, deployment, etc.) and the specific task. Pick 1-3 search terms.

### 2. Search Both Registries in the Background

Run both CLI commands with `run_in_background: true` to keep the chat clean:

```bash
npx skills find "<query>" || true
```

```bash
npx skillfish search "<query>" --json --limit 10 || true
```

The `|| true` ensures exit code 0 so background tasks report as completed. You'll be notified when each completes. If one fails, use results from the other.

### 3. Verify Quality

Do not recommend blindly. Check:

- **Install count** — prefer 1K+ installs on skills.sh. Be cautious under 100.
- **Source reputation** — `vercel-labs`, `anthropics`, `microsoft` are trustworthy.
- **Relevance** — higher relevance scores from skillfish mean better matches.

### 4. Present Results as Interactive Selection

Merge results from both registries into a single list sorted by popularity descending:

- skills.sh: sort by install count (higher = better)
- skillfish: sort by stars (higher = better)
- When comparing across registries, skills.sh install counts take priority over skillfish stars since skillfish stars are often 0

Use AskUserQuestion to let the user pick which skill(s) to install.

- Set multiSelect: true so they can pick multiple
- Use the skill name as the label
- Use the registry label + source/description + install count or stars as the option description
- Label results as "skills.sh" or "skillfish" (NEVER say "mcpmarket")
- Show top 3 results + always include a "Load more" option as the 4th choice

Example:

- header: "Install skill"
- question: "Which skill(s) would you like to install?"
- options:
  - label: "markdownlint-integration", description: "skills.sh — thebushidocollective/han (45 installs)"
  - label: "markdownlint-custom-rules", description: "skills.sh — thebushidocollective/han (33 installs)"
  - label: "markdown-formatting", description: "skills.sh — denolfe/dotfiles (31 installs)"
  - label: "Load more", description: "Show more results from both registries"

### 5. Handle "Load more"

If the user picks "Load more":

1. Show the next batch of 3 unseen results + another "Load more" if more exist
2. If you've exhausted the initial results, search again with higher limits (`--limit 30` for skillfish) to get more
3. Keep paginating until the user picks a skill or results run out

### 6. Handle "Other" (new search)

If the user picks "Other" and types text, treat that text as a new search query. Go back to step 2 and run both searches with the new query. Reset pagination (start fresh with the new results).

### 7. Install Selected Skills

For each skill the user selected, run the install command:

```bash
npx skills add <owner/repo@skill> -g -y
npx skillfish add <slug>
```

Run installs sequentially and report success/failure for each.

## When No Skills Are Found

1. Acknowledge no results
2. Offer to help directly
3. Suggest creating a custom skill: `npx skills init` or `npx skillfish init`
