#!/usr/bin/env python3
"""Memory map manager for the reverse-engineer plugin.

Usage:
    python re_map.py init <target> --type PE64 --arch x64
    python re_map.py get <target> [section]
    python re_map.py summary <target>
    python re_map.py set <target> <section> <content>
    python re_map.py append <target> <section> <content>
    python re_map.py search <target> <query>
    python re_map.py list
    python re_map.py delete <target>
    python re_map.py triage <filepath>
    python re_map.py tools
    python re_map.py export <target> --format json

Sections: modules, structures, entities, functions, patterns, strings, imports, notes
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
from datetime import date
from pathlib import Path

MAPS_DIR = Path(".claude/re-maps")

SECTIONS = [
    "modules",
    "structures",
    "entities",
    "functions",
    "patterns",
    "strings",
    "imports",
    "notes",
]

SECTION_HEADERS = {
    "modules": "## Modules",
    "structures": "## Structures",
    "entities": "## Entity/Object Lists",
    "functions": "## Functions",
    "patterns": "## Patterns",
    "strings": "## Strings",
    "imports": "## Imports/Exports",
    "notes": "## Notes",
}

TOOL_DB = {
    "rizin": {
        "install": {
            "pip": None,
            "npm": None,
            "choco": "rizin",
            "brew": "rizin",
            "apt": "rizin",
        },
        "url": "https://rizin.re",
    },
    "objdump": {
        "install": {"apt": "binutils", "brew": "binutils"},
        "url": "bundled with binutils",
    },
    "readelf": {
        "install": {"apt": "binutils", "brew": "binutils"},
        "url": "bundled with binutils",
    },
    "nm": {
        "install": {"apt": "binutils", "brew": "binutils"},
        "url": "bundled with binutils",
    },
    "strings": {
        "install": {"apt": "binutils", "brew": "binutils"},
        "url": "bundled with binutils",
    },
    "ilspycmd": {
        "install": {"dotnet": "dotnet tool install -g ilspycmd"},
        "url": "https://github.com/icsharpcode/ILSpy",
    },
    "monodis": {
        "install": {"apt": "mono-utils", "brew": "mono"},
        "url": "https://www.mono-project.com",
    },
    "jadx": {
        "install": {"brew": "jadx", "choco": "jadx"},
        "url": "https://github.com/skylot/jadx",
    },
    "cfr": {"install": {}, "url": "https://github.com/leibnitz27/cfr"},
    "javap": {"install": {}, "url": "bundled with JDK"},
    "js-beautify": {
        "install": {"npm": "npm install -g js-beautify"},
        "url": "https://github.com/beautifier/js-beautify",
    },
    "binwalk": {
        "install": {"pip": "pip install binwalk", "apt": "binwalk", "brew": "binwalk"},
        "url": "https://github.com/ReFirmLabs/binwalk",
    },
    "uncompyle6": {
        "install": {"pip": "pip install uncompyle6"},
        "url": "https://github.com/rocky/python-uncompyle6",
    },
    "pycdc": {"install": {}, "url": "https://github.com/zrax/pycdc"},
    "pyinstxtractor": {
        "install": {"pip": "pip install pyinstxtractor"},
        "url": "https://github.com/extremecoders-re/pyinstxtractor",
    },
    "apktool": {
        "install": {"brew": "apktool", "choco": "apktool"},
        "url": "https://apktool.org",
    },
    "upx": {
        "install": {"apt": "upx-ucl", "brew": "upx", "choco": "upx"},
        "url": "https://upx.github.io",
    },
    "dumpbin": {"install": {}, "url": "bundled with Visual Studio"},
    "otool": {"install": {}, "url": "bundled with Xcode"},
    "wasm-decompile": {
        "install": {"apt": "wabt", "brew": "wabt"},
        "url": "https://github.com/WebAssembly/wabt",
    },
}

INTERESTING_PATTERNS = [
    re.compile(r"https?://\S+"),
    re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"),
    re.compile(r"[A-Za-z]:\\[\w\\]+"),
    re.compile(r"/(?:usr|etc|var|tmp|home|opt)/[\w/]+"),
    re.compile(r"(?:password|passwd|secret|token|key|api[_-]?key|auth)", re.I),
    re.compile(r"(?:AES|RSA|SHA|MD5|DES|RC4|HMAC)", re.I),
    re.compile(r"(?:socket|connect|send|recv|bind|listen|accept)", re.I),
    re.compile(
        r"(?:CreateProcess|LoadLibrary|GetProcAddress|VirtualAlloc|WriteProcessMemory)",
        re.I,
    ),
    re.compile(r"(?:dlopen|dlsym|mmap|mprotect|ptrace|fork|exec)", re.I),
    re.compile(r"(?:UnityEngine|UObject|APlayerController|ACharacter|APawn)", re.I),
]


def map_path(target: str) -> Path:
    safe = re.sub(r"[^\w\-.]", "_", target)
    return MAPS_DIR / f"{safe}.md"


def parse_map(text: str) -> dict:
    result = {"frontmatter": "", "sections": {}}
    fm_match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if fm_match:
        result["frontmatter"] = fm_match.group(1)
        text = text[fm_match.end() :]

    for key, header in SECTION_HEADERS.items():
        pattern = re.escape(header) + r"\n(.*?)(?=\n## |\Z)"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            result["sections"][key] = match.group(1).strip()
        else:
            result["sections"][key] = ""
    return result


def build_map(data: dict) -> str:
    lines = [f"---\n{data['frontmatter']}\n---\n"]
    for key in SECTIONS:
        header = SECTION_HEADERS[key]
        content = data["sections"].get(key, "")
        lines.append(f"{header}\n{content}\n")
    return "\n".join(lines)


def tool_available(name: str) -> bool:
    return shutil.which(name) is not None


def cmd_init(args):
    MAPS_DIR.mkdir(parents=True, exist_ok=True)
    path = map_path(args.target)
    if path.exists() and not args.force:
        print(f"EXISTS: {path}")
        print("Use --force to overwrite.")
        sys.exit(1)

    fm = f"target: {args.target}\ntype: {args.type}\narch: {args.arch}\nanalyzed: {date.today()}\ntools_used: []"
    data = {"frontmatter": fm, "sections": {s: "" for s in SECTIONS}}
    path.write_text(build_map(data), encoding="utf-8")
    print(f"OK: {path}")


def cmd_get(args):
    path = map_path(args.target)
    if not path.exists():
        print(f"NOT_FOUND: {args.target}")
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    if not args.section:
        print(text)
        return

    data = parse_map(text)
    section = args.section.lower()
    if section == "frontmatter":
        print(data["frontmatter"])
    elif section in data["sections"]:
        content = data["sections"][section]
        print(content if content else "(empty)")
    else:
        print(f"BAD_SECTION: {section}")
        print(f"Available: frontmatter, {', '.join(SECTIONS)}")
        sys.exit(1)


def cmd_summary(args):
    path = map_path(args.target)
    if not path.exists():
        print(f"NOT_FOUND: {args.target}")
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    data = parse_map(text)

    out = {"target": args.target}
    for line in data["frontmatter"].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()

    sections = {}
    for key in SECTIONS:
        content = data["sections"].get(key, "")
        if content:
            lines = [l for l in content.splitlines() if l.strip()]
            sections[key] = len(lines)
    out["sections"] = sections
    out["total_lines"] = sum(sections.values())
    print(json.dumps(out, indent=2))


def cmd_set(args):
    path = map_path(args.target)
    if not path.exists():
        print(f"NOT_FOUND: {args.target}")
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    data = parse_map(text)
    section = args.section.lower()

    if section not in SECTIONS:
        print(f"BAD_SECTION: {section}")
        sys.exit(1)

    content = args.content
    if content == "-":
        content = sys.stdin.read()

    data["sections"][section] = content.strip()
    path.write_text(build_map(data), encoding="utf-8")
    print(f"OK: [{section}]")


def cmd_append(args):
    path = map_path(args.target)
    if not path.exists():
        print(f"NOT_FOUND: {args.target}")
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    data = parse_map(text)
    section = args.section.lower()

    if section not in SECTIONS:
        print(f"BAD_SECTION: {section}")
        sys.exit(1)

    content = args.content
    if content == "-":
        content = sys.stdin.read()

    existing = data["sections"].get(section, "")
    if existing:
        data["sections"][section] = existing + "\n" + content.strip()
    else:
        data["sections"][section] = content.strip()

    path.write_text(build_map(data), encoding="utf-8")
    print(f"OK: [{section}] +{len(content.strip().splitlines())} lines")


def cmd_search(args):
    path = map_path(args.target)
    if not path.exists():
        print(f"NOT_FOUND: {args.target}")
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    data = parse_map(text)
    query = args.query.lower()
    results = []

    for key in SECTIONS:
        content = data["sections"].get(key, "")
        for i, line in enumerate(content.splitlines(), 1):
            if query in line.lower():
                results.append(f"[{key}:{i}] {line.strip()}")

    if results:
        print(f"Found {len(results)} matches:")
        for r in results:
            print(r)
    else:
        print("No matches.")


def cmd_delete(args):
    path = map_path(args.target)
    if not path.exists():
        print(f"NOT_FOUND: {args.target}")
        sys.exit(1)
    path.unlink()
    print(f"DELETED: {args.target}")


def cmd_list(args):
    if not MAPS_DIR.exists():
        print("No maps.")
        return
    maps = sorted(MAPS_DIR.glob("*.md"))
    if not maps:
        print("No maps.")
        return
    for m in maps:
        text = m.read_text(encoding="utf-8")
        data = parse_map(text)
        target = m.stem
        mtype = "?"
        arch = "?"
        for line in data["frontmatter"].splitlines():
            if line.startswith("target:"):
                target = line.split(":", 1)[1].strip()
            elif line.startswith("type:"):
                mtype = line.split(":", 1)[1].strip()
            elif line.startswith("arch:"):
                arch = line.split(":", 1)[1].strip()
        filled = sum(1 for s in SECTIONS if data["sections"].get(s, "").strip())
        print(f"  {target} | {mtype}/{arch} | {filled}/{len(SECTIONS)} sections | {m}")


def cmd_triage(args):
    filepath = Path(args.filepath)
    if not filepath.exists():
        print(f"NOT_FOUND: {filepath}")
        sys.exit(1)

    stat = filepath.stat()
    info = {
        "file": str(filepath),
        "name": filepath.name,
        "size": stat.st_size,
        "size_human": _human_size(stat.st_size),
    }

    with open(str(filepath), "rb") as f:
        header = f.read(512)

    info["md5"] = (
        hashlib.md5(Path(filepath).read_bytes()).hexdigest()
        if stat.st_size < 100_000_000
        else "skipped (>100MB)"
    )
    info["magic_hex"] = header[:16].hex()

    detected = _detect_type(header, filepath)
    info.update(detected)

    try:
        result = subprocess.run(
            ["file", str(filepath)], capture_output=True, text=True, timeout=10
        )
        info["file_output"] = result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        info["file_output"] = "unavailable"

    strings_result = _extract_strings(filepath)
    info.update(strings_result)

    tools = _suggest_tools(info["type"])
    available = [t for t in tools if tool_available(t)]
    missing = [t for t in tools if not tool_available(t)]
    info["tools_available"] = available
    info["tools_missing"] = missing
    info["install_hints"] = {t: _install_hint(t) for t in missing}

    print(json.dumps(info, indent=2))


def cmd_tools(args):
    all_tools = sorted(TOOL_DB.keys())
    available = []
    missing = []
    for t in all_tools:
        if tool_available(t):
            available.append(t)
        else:
            missing.append(t)

    print(f"Installed ({len(available)}):")
    for t in available:
        path = shutil.which(t)
        print(f"  + {t} — {path}")

    print(f"\nMissing ({len(missing)}):")
    for t in missing:
        hint = _install_hint(t)
        print(f"  - {t} — {hint}")


def cmd_export(args):
    path = map_path(args.target)
    if not path.exists():
        print(f"NOT_FOUND: {args.target}")
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    data = parse_map(text)

    out = {}
    for line in data["frontmatter"].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    out["sections"] = data["sections"]
    print(json.dumps(out, indent=2))


def _human_size(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def _detect_type(header: bytes, filepath: Path) -> dict:
    ext = filepath.suffix.lower()
    result = {"type": "Unknown", "arch": "Unknown", "packing": None, "framework": None}

    if header[:2] == b"MZ":
        result["type"] = "PE"
        if len(header) >= 64:
            pe_offset = (
                struct.unpack_from("<I", header, 0x3C)[0]
                if len(header) > 0x3C + 4
                else 0
            )
            if pe_offset and pe_offset + 6 <= len(header):
                try:
                    machine = struct.unpack_from("<H", header, pe_offset + 4)[0]
                    result["arch"] = {0x14C: "x86", 0x8664: "x64", 0xAA64: "ARM64"}.get(
                        machine, f"0x{machine:x}"
                    )
                except struct.error:
                    pass
        if b"UPX" in header:
            result["packing"] = "UPX"
        if b".text\x00" not in header and b"Themida" in header:
            result["packing"] = "Themida"
        if b"_CorExeMain" in header or b"mscoree.dll" in header:
            result["framework"] = ".NET"
            result["type"] = "PE/.NET"

    elif header[:4] == b"\x7fELF":
        result["type"] = "ELF"
        if len(header) >= 19:
            ei_class = header[4]
            e_machine = struct.unpack_from("<H", header, 18)[0]
            result["arch"] = {
                (1, 3): "x86",
                (2, 0x3E): "x64",
                (1, 40): "ARM",
                (2, 183): "ARM64",
                (1, 8): "MIPS",
                (2, 8): "MIPS64",
            }.get((ei_class, e_machine), f"class={ei_class} machine=0x{e_machine:x}")
        if b"UPX" in header:
            result["packing"] = "UPX"
        if b"Go build" in header or b"go.buildid" in header:
            result["framework"] = "Go"
        if b"rustc" in header:
            result["framework"] = "Rust"

    elif header[:4] in (b"\xfe\xed\xfa\xce", b"\xce\xfa\xed\xfe"):
        result["type"] = "MachO"
        result["arch"] = "x86" if header[:4] == b"\xce\xfa\xed\xfe" else "PPC"
    elif header[:4] in (b"\xfe\xed\xfa\xcf", b"\xcf\xfa\xed\xfe"):
        result["type"] = "MachO"
        result["arch"] = "x64" if header[:4] == b"\xcf\xfa\xed\xfe" else "PPC64"
    elif header[:4] == b"\xca\xfe\xba\xbe":
        if len(header) >= 8 and struct.unpack_from(">I", header, 4)[0] < 30:
            result["type"] = "MachO-Universal"
        else:
            result["type"] = "Java-class"
            result["framework"] = "JVM"
    elif header[:4] == b"PK\x03\x04":
        if ext in (".apk",):
            result["type"] = "APK"
            result["framework"] = "Android"
        elif ext in (".jar",):
            result["type"] = "JAR"
            result["framework"] = "JVM"
        else:
            result["type"] = "ZIP"
    elif header[:4] == b"dex\n" or header[:4] == b"dey\n":
        result["type"] = "DEX"
        result["framework"] = "Android"
    elif header[:2] == b"\x42\x5a":
        result["type"] = "BZ2"
    elif header[:3] == b"\x1f\x8b\x08":
        result["type"] = "GZIP"
    elif header[:4] == b"\x00asm":
        result["type"] = "WASM"
        result["framework"] = "WebAssembly"
    elif header[:2] in (
        b"\xe3\x00",
        b"\x55\x0d",
        b"\x42\x0d",
        b"\x33\x0d",
        b"\x16\x0d",
        b"\xa7\x0d",
    ):
        result["type"] = "Python-bytecode"
        result["framework"] = "Python"
    elif header[:2] == b"#!":
        shebang = header.split(b"\n")[0].decode("utf-8", errors="ignore")
        result["type"] = "Script"
        if "python" in shebang.lower():
            result["framework"] = "Python"
        elif "node" in shebang.lower():
            result["framework"] = "Node.js"
        elif "bash" in shebang.lower() or "sh" in shebang.lower():
            result["framework"] = "Shell"
    elif ext in (".js", ".mjs", ".cjs"):
        result["type"] = "JavaScript"
        result["framework"] = "JavaScript"
    elif ext in (".py",):
        result["type"] = "Python-source"
        result["framework"] = "Python"
    elif ext in (".dll", ".exe", ".sys"):
        result["type"] = "PE"
    elif ext in (".so",):
        result["type"] = "ELF"
    elif ext in (".dylib",):
        result["type"] = "MachO"

    return result


def _extract_strings(filepath: Path) -> dict:
    result = {"string_count": 0, "interesting_strings": [], "categories": {}}

    if not tool_available("strings"):
        result["error"] = "strings not installed"
        return result

    try:
        proc = subprocess.run(
            ["strings", "-n", "6", str(filepath)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        all_strings = proc.stdout.strip().splitlines()
    except subprocess.TimeoutExpired:
        result["error"] = "strings timed out"
        return result

    result["string_count"] = len(all_strings)

    categories = {
        "urls": [],
        "ips": [],
        "paths": [],
        "crypto": [],
        "network": [],
        "winapi": [],
        "posix": [],
        "game_engine": [],
        "secrets": [],
    }

    cat_patterns = {
        "urls": INTERESTING_PATTERNS[0],
        "ips": INTERESTING_PATTERNS[1],
        "paths": [INTERESTING_PATTERNS[2], INTERESTING_PATTERNS[3]],
        "secrets": INTERESTING_PATTERNS[4],
        "crypto": INTERESTING_PATTERNS[5],
        "network": INTERESTING_PATTERNS[6],
        "winapi": INTERESTING_PATTERNS[7],
        "posix": INTERESTING_PATTERNS[8],
        "game_engine": INTERESTING_PATTERNS[9],
    }

    for s in all_strings:
        for cat, pat in cat_patterns.items():
            if isinstance(pat, list):
                if any(p.search(s) for p in pat):
                    if len(categories[cat]) < 20:
                        categories[cat].append(s.strip())
            else:
                if pat.search(s):
                    if len(categories[cat]) < 20:
                        categories[cat].append(s.strip())

    result["categories"] = {k: v for k, v in categories.items() if v}

    interesting = []
    for v in categories.values():
        interesting.extend(v)
    result["interesting_strings"] = interesting[:50]

    return result


def _suggest_tools(file_type: str) -> list:
    mapping = {
        "PE": ["rizin", "objdump", "strings", "dumpbin"],
        "PE/.NET": ["ilspycmd", "monodis", "strings"],
        "ELF": ["rizin", "objdump", "readelf", "nm", "strings"],
        "MachO": ["rizin", "otool", "strings"],
        "MachO-Universal": ["rizin", "otool", "strings"],
        "Java-class": ["jadx", "cfr", "javap"],
        "JAR": ["jadx", "cfr", "javap"],
        "APK": ["jadx", "apktool"],
        "DEX": ["jadx"],
        "ZIP": ["unzip"],
        "Python-bytecode": ["uncompyle6", "pycdc"],
        "Python-source": [],
        "JavaScript": ["js-beautify"],
        "Script": [],
        "WASM": ["wasm-decompile"],
        "BZ2": ["strings"],
        "GZIP": ["strings"],
    }
    return mapping.get(file_type, ["strings", "xxd", "rizin"])


def _install_hint(tool: str) -> str:
    info = TOOL_DB.get(tool, {})
    installs = info.get("install", {})
    if installs:
        first = next(iter(installs.values()))
        if first:
            return first
    url = info.get("url", "")
    return url if url else "manual install"


def main():
    parser = argparse.ArgumentParser(description="RE memory map manager")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("init")
    p.add_argument("target")
    p.add_argument("--type", default="Unknown")
    p.add_argument("--arch", default="Unknown")
    p.add_argument("--force", action="store_true")

    p = sub.add_parser("get")
    p.add_argument("target")
    p.add_argument("section", nargs="?")

    p = sub.add_parser("summary")
    p.add_argument("target")

    p = sub.add_parser("set")
    p.add_argument("target")
    p.add_argument("section")
    p.add_argument("content")

    p = sub.add_parser("append")
    p.add_argument("target")
    p.add_argument("section")
    p.add_argument("content")

    p = sub.add_parser("search")
    p.add_argument("target")
    p.add_argument("query")

    p = sub.add_parser("list")

    p = sub.add_parser("delete")
    p.add_argument("target")

    p = sub.add_parser("triage")
    p.add_argument("filepath")

    p = sub.add_parser("tools")

    p = sub.add_parser("export")
    p.add_argument("target")
    p.add_argument("--format", default="json", choices=["json"])

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        "init": cmd_init,
        "get": cmd_get,
        "summary": cmd_summary,
        "set": cmd_set,
        "append": cmd_append,
        "search": cmd_search,
        "list": cmd_list,
        "delete": cmd_delete,
        "triage": cmd_triage,
        "tools": cmd_tools,
        "export": cmd_export,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
