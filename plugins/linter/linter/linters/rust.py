from .base import BaseLinter


class RustLinter(BaseLinter):
    extensions = [".rs"]
    tools = [
        {"cmd": "rustfmt", "name": "rustfmt", "install": "rustup component add rustfmt"},
    ]

    def format_cmd(self, file_path, indent):
        return [f'rustfmt "{file_path}"']
