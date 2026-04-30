# reverse-engineer

Part of [cc-booster](https://github.com/Fenish/claude-code-booster) by fenish.

General-purpose reverse engineering toolkit for Claude Code. Analyzes binaries,
games, apps, and scripts across all platforms and languages.

## Features

- Auto-detects file type and picks the right decompilation toolchain
- Supports PE, ELF, .NET, Python, JavaScript, Java, Go, Rust, firmware, Android
- Persists findings to `.claude/re-maps/` so analysis survives across sessions
- Asks before installing any tools
- Deep analysis agent for complex multi-step targets

## Usage

Just ask naturally:

- "Reverse engineer this binary"
- "Decompile game.exe and find the player struct"
- "Analyze this .pyc file"
- "Find entity list offsets in this game"
- "Deobfuscate this JavaScript"

After analysis, ask follow-up questions — the map file keeps all the intel:

- "Build me an ESP using the offsets you found"
- "What functions handle damage calculation?"
- "Generate a signature pattern for the entity list"

## Memory Maps

All findings are saved to `.claude/re-maps/<target>.md`. This file contains
structures, offsets, patterns, functions, and notes. It's read automatically on
future analysis of the same target.

## Supported Toolchains

| Target         | Tools                                     |
| -------------- | ----------------------------------------- |
| C/C++ (PE/ELF) | rizin, objdump, strings, readelf, nm, xxd |
| .NET           | ilspycmd, monodis                         |
| Python         | uncompyle6, pycdc, pyinstxtractor         |
| JavaScript     | js-beautify, AST analysis                 |
| Java           | jadx, cfr, javap                          |
| Go / Rust      | rizin, strings, symbol demangling         |
| Firmware       | binwalk, strings, xxd                     |
| Android        | jadx, apktool                             |

## Important

> _This is an educational and research tool. Use at your own risk. Only use on
> software you own or have explicit authorization to analyze. Respect
> intellectual property and applicable laws._
