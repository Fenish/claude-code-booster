from .base import BaseLinter


class MarkdownLinter(BaseLinter):
    extensions = [".md"]
    tools = [
        {"cmd": "npx", "name": "prettier", "install": "npm install -g prettier"},
    ]

    def format_cmd(self, file_path, indent):
        size = indent.get("size", 2)
        style = indent.get("style", "space")
        tab_flag = "--use-tabs" if style == "tab" else ""
        return [
            f'npx prettier --write --prose-wrap always --tab-width {size} {tab_flag} "{file_path}"'
        ]
