# linter

Part of [cc-booster](https://github.com/Fenish/claude-code-booster) by fenish.

Auto-formats files after every edit using the right linter for each language. No
commands, no skills — just a PostToolUse hook that runs automatically.

## How It Works

Runs after every Edit/Write. Detects the file type and formats it with the right
tool:

| Language      | Extensions                  | Formatter                |
| ------------- | --------------------------- | ------------------------ |
| JavaScript/TS | .js .jsx .ts .tsx .mjs .cjs | prettier + eslint        |
| Python        | .py                         | ruff, black, or autopep8 |
| Rust          | .rs                         | rustfmt                  |
| Go            | .go                         | gofmt                    |
| Markdown      | .md                         | prettier                 |
| JSON          | .json                       | prettier                 |
| YAML          | .yaml .yml                  | prettier                 |
| CSS           | .css .scss .less            | prettier                 |
| HTML          | .html .htm                  | prettier                 |
| Shell         | .sh .bash .zsh              | shfmt                    |

- Reads `.editorconfig` for indent style, falls back to file content detection
- Auto-installs missing formatters on first use
- Never blocks — if a formatter fails or is unavailable, it skips silently
