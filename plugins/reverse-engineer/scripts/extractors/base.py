import re
import subprocess


def run_tool(cmd, timeout=60):
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return proc.stdout, proc.stderr, proc.returncode
    except FileNotFoundError:
        return "", f"{cmd[0]} not found", -1
    except subprocess.TimeoutExpired:
        return "", f"{cmd[0]} timed out after {timeout}s", -2


_ANSI_RE = re.compile(r"\x1b\[[^a-zA-Z]*[a-zA-Z]")


def clean_json(stdout):
    cleaned = _ANSI_RE.sub("", stdout)
    for start_char in ("[", "{"):
        idx = cleaned.find(start_char)
        if idx != -1:
            return cleaned[idx:]
    return cleaned.strip()
