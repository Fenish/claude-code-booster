from .base import BaseLinter


class ShellLinter(BaseLinter):
    extensions = [".sh", ".bash", ".zsh"]
    tools = [
        {"cmd": "shfmt", "name": "shfmt", "install": "go install mvdan.cc/sh/v3/cmd/shfmt@latest"},
    ]

    def format_cmd(self, file_path, indent):
        indent_flag = "-i 0" if indent.get("style") == "tab" else f"-i {indent.get('size', 2)}"
        return [f'shfmt -w {indent_flag} "{file_path}"']
