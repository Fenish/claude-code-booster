# find-skills

Part of [cc-booster](https://github.com/Fenish/claude-code-booster) by fenish.

A Claude Code plugin for discovering and installing agent skills from multiple registries.

## Features

- Searches both skills.sh and skillfish in parallel
- Slash command (`/find-skills`) for quick searches
- Skill scout agent for project-aware recommendations
- No dependencies — uses `npx skills` and `npx skillfish` CLIs directly

## Usage

### Slash Command

```sh
/find-skills react testing
/find-skills deployment ci-cd
```

### Skill (Auto-triggers)

Just ask naturally:

- "Is there a skill for writing tests?"
- "Find me a skill for Docker deployment"
- "How do I do X?" (if X might have a skill)

### Skill Scout Agent

Ask for a project scan:

- "What skills should I install for this project?"
- "Recommend skills based on my codebase"

## Registries

| Registry  | CLI                                    | Browse                    |
|-----------|----------------------------------------|---------------------------|
| skills.sh | `npx skills find <query>`              | <https://skills.sh/>      |
| skillfish | `npx skillfish search <query> --json`  | <https://www.skill.fish/> |
