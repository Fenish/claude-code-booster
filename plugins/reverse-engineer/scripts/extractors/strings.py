import json
import re

import registry
import storage
from extractors import base

CATEGORIES = {
    "urls": re.compile(r"https?://\S+"),
    "ips": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
    "win_paths": re.compile(r"[A-Za-z]:\\[\w\\]+"),
    "unix_paths": re.compile(r"/(?:usr|etc|var|tmp|home|opt)/[\w/]+"),
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
        r"(?:UnityEngine|UObject|APlayerController|ACharacter|APawn|CEntity|CBaseEntity)",
        re.I,
    ),
}

MAX_PER_CATEGORY = 50


def _extract_gnu_strings(filepath):
    stdout, stderr, rc = base.run_tool(
        ["strings", "-n", "6", str(filepath)], timeout=60
    )
    if rc != 0:
        return None, f"strings failed: {stderr.strip()[:200]}"
    return stdout.strip().splitlines(), None


def _extract_rizin_strings(filepath):
    stdout, stderr, rc = base.run_tool(
        ["rizin", "-q", "-c", "izj", str(filepath)], timeout=120
    )
    if rc != 0:
        return None, f"rizin izj failed: {stderr.strip()[:200]}"
    try:
        entries = json.loads(base.clean_json(stdout))
    except (json.JSONDecodeError, ValueError) as e:
        return None, f"rizin izj parse error: {e}"
    return [e.get("string", "") for e in entries if e.get("string")], None


def _categorize(all_strings):
    cats = {k: [] for k in CATEGORIES}
    for s in all_strings:
        for cat, pat in CATEGORIES.items():
            if len(cats[cat]) >= MAX_PER_CATEGORY:
                continue
            if pat.search(s):
                cats[cat].append(s.strip())
    return {k: v for k, v in cats.items() if v}


def extract(filepath, target):
    all_strings = None
    error = None

    if registry.is_available("strings"):
        all_strings, error = _extract_gnu_strings(filepath)

    if all_strings is None and registry.is_available("rizin"):
        all_strings, error = _extract_rizin_strings(filepath)

    if all_strings is None:
        if error:
            return {"error": error}
        return {
            "error": "no string extraction tool available (install rizin or strings)"
        }

    total = len(all_strings)
    cats = _categorize(all_strings)

    strings_data = {"total": total, "categories": cats}
    storage.update_section(target, "strings", strings_data)

    cat_summary = ", ".join(f"{len(v)} {k}" for k, v in cats.items())
    return f"Extracted {total} strings ({cat_summary})"


def run(filepath, target):
    return extract(filepath, target)
