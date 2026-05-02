---
name: frontend-roadmap
description: |
  Guided frontend project preparation. Collects requirements, references,
  design platform output, and tech stack choices into a roadmap.md plan.
  Trigger when the user asks to: build website, create frontend, frontend roadmap,
  web project, design website, start web project, build landing page, scaffold frontend,
  plan frontend, prepare frontend, frontend brief, website plan.
allowed-tools: Bash, Read, WebFetch, WebSearch
version: 2.0.0
---

# Frontend Roadmap

Guided preparation for frontend projects. This skill does NOT generate code — it
produces a comprehensive `roadmap.md` plan file that a frontend developer agent
will use to build the site.

## Overview

Walk the user through 5 steps to gather everything needed before building:

1. **Project Requirements** — type, description, audience, features, pages,
   brand colors
2. **Collect References** — browse inspiration sites, save screenshots
3. **Design Platform** — choose a platform (Stitch recommended), get an advanced
   prompt
4. **Import Exports** — export platform output into workspace
5. **Tech Stack** — choose framework and UI library

Final output: `frontend-roadmap/roadmap.md`

## Workspace Structure

```
frontend-roadmap/
├── state.json              # Progress tracker
├── preparation/            # Auto-generated docs per step
│   ├── requirements.md     # Step 1 → project brief + colors
│   ├── platform-prompt.md  # Step 3 → prompt for design platform
│   └── tech-stack.md       # Step 5 → tech decisions + rationale
├── references/             # User saves inspiration screenshots here
├── exports/                # User places platform-exported code here
└── roadmap.md              # FINAL OUTPUT — handoff for frontend dev agent
```

## CLI Reference

All commands use this base:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/roadmap.py" <command>
```

On Windows, use `python` instead of `python3`.

### Commands

#### init — Create workspace

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/roadmap.py" init
```

Creates `frontend-roadmap/` with `preparation/`, `references/`, `exports/`, and
`state.json`.

#### status — Show progress

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/roadmap.py" status
```

#### next — Get current step questions as JSON

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/roadmap.py" next
```

Returns JSON with `questions`, `color_question` (step 1), `search_urls` (step
2), or `platform_instructions` (step 3).

#### complete-step N --answers 'JSON' — Complete a step

**This is the main command. The subcommand is `complete-step` (with a hyphen),
not `complete step` (two words). Both `complete-step` and `complete` work as
aliases.**

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/roadmap.py" complete-step <N> --answers '<JSON>'
python "${CLAUDE_PLUGIN_ROOT}/scripts/roadmap.py" complete <N> --answers '<JSON>'
```

The `--answers` flag takes a JSON object. Keys must match the question keys from
`next`.

**Step 1 example:**

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/roadmap.py" complete-step 1 --answers '{"project.name": "MyApp", "project.type": "SaaS", "project.description": "A project management tool for remote teams", "project.target_audience": "Small engineering teams", "project.key_features": ["Task boards", "Time tracking", "Team chat"], "project.pages": ["Home", "Dashboard", "Pricing", "About"], "branding.palette": "Trust Blue"}'
```

Writes `preparation/requirements.md`.

**Step 2 example:**

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/roadmap.py" complete-step 2 --answers '{"_references_done": "Yes, done"}'
```

**Step 3 example:**

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/roadmap.py" complete-step 3 --answers '{"platform": "Google Stitch"}'
```

Writes `preparation/platform-prompt.md`.

**Step 4 example:**

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/roadmap.py" complete-step 4 --answers '{"_import_done": "Yes, imported"}'
```

**Step 5 example:**

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/roadmap.py" complete-step 5 --answers '{"tech_stack.framework": "Next.js + Tailwind", "tech_stack.ui_library": "shadcn/ui"}'
```

Writes `preparation/tech-stack.md`.

#### prompt — Show and save the design platform prompt

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/roadmap.py" prompt
```

Prints the prompt and saves it to `preparation/platform-prompt.md`.

#### finalize — Generate roadmap.md

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/roadmap.py" finalize
```

## Step-by-Step Workflow

### Step 1: Initialize + Requirements

1. Run `init` to create the workspace
2. Run `next` to get step 1 questions
3. Use AskUserQuestion for each question:
   - Project type (SaaS / Portfolio / Web App / E-commerce / Landing Page)
   - Project description (free text)
   - Project name (free text)
   - Target audience (free text)
   - Key features (comma-separated → parse to array)
   - Pages needed (comma-separated → parse to array)
4. After getting the project type, use the `color_question` from `next` output
   to present color palette options with previews
5. User picks a preset palette or types custom colors
6. Run `complete-step 1` with all answers including `branding.palette`

### Step 2: Collect References

**CRITICAL: You MUST run `next` first and show the search links. Do NOT skip
this.**

1. Run `next` to get step 2 JSON — it contains a `search_urls` array
2. Parse the `search_urls` array from the JSON output
3. **MANDATORY: Show EVERY link as a clickable markdown link to the user:**

   For each item in `search_urls`, output: `- [item.label](item.url)`

   Example output you must produce:

   ```
   Browse these design galleries for inspiration:

   - [Dribbble — saas dashboard](https://dribbble.com/search/saas%20dashboard)
   - [Dribbble — saas landing page](https://dribbble.com/search/saas%20landing%20page)
   - [Awwwards — saas websites](https://www.awwwards.com/websites/saas/)
   - [Mobbin — Web App Patterns](https://mobbin.com/browse/web/apps)
   - [Godly — Curated Design Inspiration](https://godly.website)

   Open these links, find designs you like, take screenshots, and save them
   into `frontend-roadmap/references/`.
   ```

4. Do NOT suggest real product websites (stripe.com, linear.app, notion.so) —
   ONLY show the search_urls from the `next` output. These are designer
   galleries where users find design inspiration, not real products.
5. After showing links, use AskUserQuestion: "Done collecting references?"
6. Run `complete-step 2`

### Step 3: Design Platform

1. Run `next` to get platform options
2. Use AskUserQuestion — Google Stitch is first and recommended
3. Run `complete-step 3` — this auto-generates `preparation/platform-prompt.md`
4. Run `prompt` to show the full prompt to the user
5. Tell the user:
   - Open the chosen platform
   - Upload reference images from `frontend-roadmap/references/`
   - Paste the prompt from `preparation/platform-prompt.md`
   - Generate the design
6. Show platform-specific export instructions from the output

### Step 4: Import Exports

1. Tell the user to export from their platform into `frontend-roadmap/exports/`
2. Use AskUserQuestion: "Have you placed the exported files?"
3. Run `complete-step 4`

### Step 5: Tech Stack + Finalize

1. Run `next` to get tech stack options
2. Use AskUserQuestion for framework and UI library
3. Run `complete-step 5` — writes `preparation/tech-stack.md`
4. Run `finalize` to generate the final `roadmap.md`
5. Tell the user the roadmap is ready at `frontend-roadmap/roadmap.md`

## Important

- This skill is PREPARATION ONLY — it does NOT generate any frontend code
- The output is a `roadmap.md` file meant for a separate frontend developer
  agent/skill
- Ask questions one step at a time, don't rush through all 5 at once
- Use AskUserQuestion for interactive choices
- Let the user take their time on reference collection and design generation
- Always run `status` after completing a step so the user sees their progress
- Google Stitch is the recommended platform — it supports image uploads and
  generates full HTML/CSS designs
- The `preparation/` folder contains auto-generated docs — the user can review
  and edit them before finalizing

## Transparent Background Requests

For transparent/background removal, include "transparent background" in the
enhanced prompt. The plugin automatically handles chroma removal.
