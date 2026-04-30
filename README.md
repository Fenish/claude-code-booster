<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Fenish/claude-code-booster/main/.github/assets/banner-dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Fenish/claude-code-booster/main/.github/assets/banner-light.svg" />
    <img src="https://raw.githubusercontent.com/Fenish/claude-code-booster/main/.github/assets/banner-dark.svg" alt="Claude Code Booster" width="800" />
  </picture>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/plugins-5-7C3AED?style=flat-square" alt="Plugins" />
  <img src="https://img.shields.io/github/license/Fenish/claude-code-booster?style=flat-square&color=orange" alt="License" />
</p>

<p align="center">
  A plugin marketplace for <a href="https://claude.ai/code">Claude Code</a> that boost your claude code performance 10x.
</p>

---

## Quick Start

```sh
/plugin marketplace add Fenish/claude-code-booster
```

Then pick what you need from `/plugin > Discover`.

---

## Plugin Categories

<!-- TOC:START -->
[![Productivity (3)](https://img.shields.io/badge/Productivity%20%283%29-7C3AED?style=flat-square&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBvbHlnb24gcG9pbnRzPSIxMyAyIDMgMTQgMTIgMTQgMTEgMjIgMjEgMTAgMTIgMTAgMTMgMiIvPjwvc3ZnPg==&logoColor=white)](#productivity) [![Security (2)](https://img.shields.io/badge/Security%20%282%29-DC2626?style=flat-square&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHJlY3QgeD0iMyIgeT0iMTEiIHdpZHRoPSIxOCIgaGVpZ2h0PSIxMSIgcng9IjIiIHJ5PSIyIi8+PHBhdGggZD0iTTcgMTFWN2E1IDUgMCAwIDEgMTAgMHY0Ii8+PC9zdmc+&logoColor=white)](#security)
<!-- TOC:END -->

---

## Plugins

<!-- PLUGINS:START -->
### ![Productivity](https://img.shields.io/badge/Productivity-7C3AED?style=flat-square&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBvbHlnb24gcG9pbnRzPSIxMyAyIDMgMTQgMTIgMTQgMTEgMjIgMjEgMTAgMTIgMTAgMTMgMiIvPjwvc3ZnPg==&logoColor=white)

- **[skill-finder](./plugins/skill-finder)** — Search and discover agent skills from skills.sh and skillfish registries. Interactive selection and one-click install.
- **[linter](./plugins/linter)** — Auto-formats files after every edit using the right linter for each language.
- **[codex-image](https://github.com/KingGyuSuh/codex-image-in-cc)** — Generate and edit images via Codex CLI's built-in imagegen skill. Slash commands for image creation and editing.

### ![Security](https://img.shields.io/badge/Security-DC2626?style=flat-square&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHJlY3QgeD0iMyIgeT0iMTEiIHdpZHRoPSIxOCIgaGVpZ2h0PSIxMSIgcng9IjIiIHJ5PSIyIi8+PHBhdGggZD0iTTcgMTFWN2E1IDUgMCAwIDEgMTAgMHY0Ii8+PC9zdmc+&logoColor=white)

- **[penetration-tester](./plugins/penetration-tester)** — Automated penetration testing for web applications. Identifies OWASP Top 10 vulnerabilities and suggests remediation.
- **[reverse-engineer](./plugins/reverse-engineer)** — General-purpose reverse engineering toolkit. Decompiles, disassembles, and maps binaries, scripts, and applications across all languages.
<!-- PLUGINS:END -->

---

## Contributing

Contributions are welcome. Fork the repo, create a branch, and open a PR. Each
plugin lives in its own directory under `plugins/` — check existing ones for the
structure.

---

## Contributors

<a href="https://github.com/Fenish/claude-code-booster/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Fenish/claude-code-booster" />
</a>
