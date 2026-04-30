#!/usr/bin/env python3
import json
import os
import sys

PLUGIN_ROOT = os.environ.get(
    "CLAUDE_PLUGIN_ROOT", os.path.dirname(os.path.abspath(__file__))
)
LINTER_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, LINTER_DIR)

from linters import detect_indent, get_linter


def main():
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        print(json.dumps({}))
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path or not os.path.isfile(file_path):
        print(json.dumps({}))
        sys.exit(0)

    linter = get_linter(file_path)
    if not linter:
        print(json.dumps({}))
        sys.exit(0)

    tool = linter.detect_tool()
    if not tool:
        tool = linter.install_tool()
    if not tool:
        print(json.dumps({}))
        sys.exit(0)

    indent = detect_indent(file_path)
    cmds = linter.format_cmd(file_path, indent)
    if not cmds:
        print(json.dumps({}))
        sys.exit(0)

    ran_tools = []
    for cmd in cmds:
        success, _, _ = linter.run(cmd, timeout=10)
        if success:
            ran_tools.append(tool["name"])

    if ran_tools:
        name = os.path.basename(file_path)
        tools_used = ", ".join(sorted(set(ran_tools)))
        print(json.dumps({"systemMessage": f"Auto-formatted {name} with {tools_used}"}))
    else:
        print(json.dumps({}))

    sys.exit(0)


if __name__ == "__main__":
    main()
