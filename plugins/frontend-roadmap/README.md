# frontend-roadmap

Part of [cc-booster](https://github.com/Fenish/claude-code-booster) by fenish.

A Claude Code plugin that guides you through preparing everything needed before
building a frontend project. No code generation — produces a comprehensive
`roadmap.md` handoff document for a frontend developer agent.

## Features

- 5-step guided workflow: requirements → references → design platform → imports
  → tech stack
- Smart color palette recommendations based on project type (20 presets)
- Advanced per-platform prompts (Google Stitch, v0.dev, Bolt.new, Lovable)
- Reference image analysis directives baked into prompts
- Auto-generates preparation docs (requirements.md, platform-prompt.md,
  tech-stack.md)
- Final `roadmap.md` with build instructions, file structure, and best practices
- No dependencies — pure Python

## Usage

### Slash Command

```sh
/frontend-roadmap
```

### Skill (Auto-triggers)

Just ask naturally:

- "I want to build a website"
- "Help me plan a frontend project"
- "Create a frontend roadmap"
- "Design a landing page"

## Workflow

```txt
Step 1: Project Requirements + Brand Colors
     ↓
Step 2: Collect Visual References (Dribbble, Awwwards, etc.)
     ↓
Step 3: Choose Design Platform → Get Advanced Prompt
     ↓
Step 4: Import Platform Exports (HTML/React/Vue)
     ↓
Step 5: Choose Tech Stack (Framework + UI Library)
     ↓
  finalize → roadmap.md
```

## Workspace Structure

```txt
frontend-roadmap/
├── preparation/            # Auto-generated docs
│   ├── requirements.md     # Project brief + colors
│   ├── platform-prompt.md  # Prompt for design platform
│   └── tech-stack.md       # Tech decisions + rationale
├── references/             # Inspiration screenshots
├── exports/                # Platform-exported code (HTML/React/Vue)
├── state.json              # Progress tracker
└── roadmap.md              # Final output
```

## Supported Platforms

| Platform      | Best For                            |
| ------------- | ----------------------------------- |
| Google Stitch | Full HTML/CSS designs (recommended) |
| v0.dev        | React/Next.js components            |
| Bolt.new      | Full-stack apps with live preview   |
| Lovable       | Design-first web apps               |

## CLI

```sh
python scripts/roadmap.py init              # Create workspace
python scripts/roadmap.py status            # Show progress
python scripts/roadmap.py next              # Get current step questions
python scripts/roadmap.py complete <N> --answers '{...}'  # Complete a step
python scripts/roadmap.py prompt            # Show/save platform prompt
python scripts/roadmap.py finalize          # Generate roadmap.md
```
