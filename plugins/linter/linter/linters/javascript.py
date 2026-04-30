from .base import BaseLinter


class JavaScriptLinter(BaseLinter):
    extensions = [".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"]
    tools = [
        {
            "cmd": "npx",
            "name": "eslint+prettier",
            "install": "npm install -g eslint prettier",
        },
    ]

    def format_cmd(self, file_path, indent):
        cmds = []
        size = indent.get("size", 2)
        style = indent.get("style", "space")
        tab_flag = "--use-tabs" if style == "tab" else ""
        cmds.append(
            f'npx prettier --write --tab-width {size} {tab_flag} "{file_path}"'
        )
        cmds.append(f'npx eslint --fix --no-error-on-unmatched-pattern "{file_path}"')
        return cmds
