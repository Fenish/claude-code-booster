import hashlib
import re
import struct
import subprocess
from pathlib import Path

import registry

INTERESTING_PATTERNS = {
    "urls": re.compile(r"https?://\S+"),
    "ips": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
    "paths": [
        re.compile(r"[A-Za-z]:\\[\w\\]+"),
        re.compile(r"/(?:usr|etc|var|tmp|home|opt)/[\w/]+"),
    ],
    "secrets": re.compile(
        r"(?:password|passwd|secret|token|key|api[_-]?key|auth)", re.I
    ),
    "crypto": re.compile(r"(?:AES|RSA|SHA|MD5|DES|RC4|HMAC)", re.I),
    "network": re.compile(r"(?:socket|connect|send|recv|bind|listen|accept)", re.I),
    "winapi": re.compile(
        r"(?:CreateProcess|LoadLibrary|GetProcAddress|VirtualAlloc|WriteProcessMemory)",
        re.I,
    ),
    "posix": re.compile(r"(?:dlopen|dlsym|mmap|mprotect|ptrace|fork|exec)", re.I),
    "game_engine": re.compile(
        r"(?:UnityEngine|UObject|APlayerController|ACharacter|APawn)", re.I
    ),
}


def _human_size(size):
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def _file_description(filepath, detected):
    try:
        result = subprocess.run(
            ["file", str(filepath)], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    parts = [str(filepath.name) + ":"]
    parts.append(f"{detected['type']} executable")
    if detected["arch"] != "Unknown":
        parts.append(f"for {detected['arch']}")
    if detected["packing"]:
        parts.append(f"(packed: {detected['packing']})")
    if detected["framework"]:
        parts.append(f"[{detected['framework']}]")
    return " ".join(parts)


def _detect_type(header, filepath):
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
        if ext == ".apk":
            result["type"] = "APK"
            result["framework"] = "Android"
        elif ext == ".jar":
            result["type"] = "JAR"
            result["framework"] = "JVM"
        else:
            result["type"] = "ZIP"
    elif header[:4] in (b"dex\n", b"dey\n"):
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
    elif ext == ".py":
        result["type"] = "Python-source"
        result["framework"] = "Python"
    elif ext in (".dll", ".exe", ".sys"):
        result["type"] = "PE"
    elif ext == ".so":
        result["type"] = "ELF"
    elif ext == ".dylib":
        result["type"] = "MachO"

    return result


def run(filepath):
    filepath = Path(filepath)
    if not filepath.exists():
        return {"error": f"not found: {filepath}"}

    stat = filepath.stat()
    with open(str(filepath), "rb") as f:
        header = f.read(512)

    md5 = (
        hashlib.md5(filepath.read_bytes()).hexdigest()
        if stat.st_size < 100_000_000
        else "skipped (>100MB)"
    )

    detected = _detect_type(header, filepath)

    file_output = _file_description(filepath, detected)

    tools = registry.suggest_tools(detected["type"])
    available = [t for t in tools if registry.is_available(t)]
    missing = [t for t in tools if not registry.is_available(t)]

    return {
        "file": str(filepath),
        "name": filepath.name,
        "size": stat.st_size,
        "size_human": _human_size(stat.st_size),
        "md5": md5,
        "magic_hex": header[:16].hex(),
        "type": detected["type"],
        "arch": detected["arch"],
        "packing": detected["packing"],
        "framework": detected["framework"],
        "file_output": file_output,
        "tools_available": available,
        "tools_missing": missing,
        "install_hints": {t: registry.install_hint(t) for t in missing},
    }
