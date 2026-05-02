---
name: frontend-roadmap
description: Start the frontend roadmap preparation workflow
allowed-tools: Bash, Read
---

# /frontend-roadmap

Initialize and manage the frontend roadmap workflow.

## Usage

When the user runs `/frontend-roadmap`:

1. Run init to create the workspace:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/roadmap.py" init
```

2. Run status to show current progress:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/roadmap.py" status
```

3. Then begin the skill workflow — the `frontend-roadmap` skill handles the
   step-by-step process from here.

## Workspace

Creates `frontend-roadmap/` in the current directory with:

- `preparation/` — auto-generated docs (requirements.md, platform-prompt.md,
  tech-stack.md)
- `references/` — user saves inspiration screenshots here
- `exports/` — user places platform-exported code (HTML/React/Vue) here
- `roadmap.md` — final output after all steps complete
