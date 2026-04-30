import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


INSTALL_CACHE_DIR = os.path.join(tempfile.gettempdir(), "cc-booster-linter")


class BaseLinter:
    extensions = []
    tools = []

    def detect_tool(self):
        for tool in self.tools:
            if self._is_installed(tool["cmd"]):
                return tool
        return None

    def install_tool(self):
        os.makedirs(INSTALL_CACHE_DIR, exist_ok=True)
        for tool in self.tools:
            marker = os.path.join(INSTALL_CACHE_DIR, f"{tool['cmd']}.attempted")
            if os.path.exists(marker):
                if self._is_installed(tool["cmd"]):
                    return tool
                continue
            Path(marker).touch()
            if "install" not in tool:
                continue
            try:
                subprocess.run(
                    tool["install"],
                    shell=True,
                    capture_output=True,
                    timeout=60,
                )
            except (subprocess.TimeoutExpired, OSError):
                pass
            if self._is_installed(tool["cmd"]):
                return tool
        return None

    def format_cmd(self, file_path, indent):
        raise NotImplementedError

    @staticmethod
    def _is_installed(cmd):
        name = cmd.split()[0] if " " in cmd else cmd
        if name == "npx":
            return shutil.which("npx") is not None
        return shutil.which(name) is not None

    @staticmethod
    def run(cmd, timeout=10):
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return result.returncode == 0, result.stdout, result.stderr
        except (subprocess.TimeoutExpired, OSError):
            return False, "", "timeout or error"


def detect_indent(file_path):
    editorconfig = _read_editorconfig(file_path)
    if editorconfig:
        return editorconfig

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = []
            for i, line in enumerate(f):
                if i >= 50:
                    break
                lines.append(line)
    except OSError:
        return {"style": "space", "size": 2}

    tabs = 0
    spaces = 0
    space_widths = []

    for line in lines:
        if line.startswith("\t"):
            tabs += 1
        elif line.startswith(" "):
            spaces += 1
            leading = len(line) - len(line.lstrip(" "))
            if leading > 0:
                space_widths.append(leading)

    if tabs > spaces:
        return {"style": "tab", "size": 4}

    if space_widths:
        diffs = []
        sorted_widths = sorted(set(space_widths))
        for i in range(1, len(sorted_widths)):
            d = sorted_widths[i] - sorted_widths[i - 1]
            if d > 0:
                diffs.append(d)
        size = min(diffs) if diffs else (min(space_widths) if space_widths else 2)
        size = max(1, min(size, 8))
        return {"style": "space", "size": size}

    return {"style": "space", "size": 2}


def _read_editorconfig(file_path):
    directory = os.path.dirname(os.path.abspath(file_path))
    while True:
        ec_path = os.path.join(directory, ".editorconfig")
        if os.path.isfile(ec_path):
            return _parse_editorconfig(ec_path, file_path)
        parent = os.path.dirname(directory)
        if parent == directory:
            break
        directory = parent
    return None


def _parse_editorconfig(ec_path, file_path):
    try:
        with open(ec_path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return None

    ext = os.path.splitext(file_path)[1]
    style = None
    size = None

    for line in content.splitlines():
        line = line.strip()
        if line.startswith("indent_style"):
            val = line.split("=", 1)[-1].strip().lower()
            if val in ("tab", "space"):
                style = val
        elif line.startswith("indent_size"):
            val = line.split("=", 1)[-1].strip()
            if val.isdigit():
                size = int(val)

    if style:
        return {"style": style, "size": size or (4 if style == "tab" else 2)}
    return None
