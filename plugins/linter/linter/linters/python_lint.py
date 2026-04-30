from .base import BaseLinter


class PythonLinter(BaseLinter):
    extensions = [".py"]
    tools = [
        {"cmd": "ruff", "name": "ruff", "install": "pip install ruff"},
        {"cmd": "black", "name": "black", "install": "pip install black"},
        {"cmd": "autopep8", "name": "autopep8", "install": "pip install autopep8"},
    ]

    def format_cmd(self, file_path, indent):
        tool = self.detect_tool() or self.install_tool()
        if not tool:
            return []

        if tool["name"] == "ruff":
            return [
                f'ruff format "{file_path}"',
                f'ruff check --fix --select I "{file_path}"',
            ]
        elif tool["name"] == "black":
            return [f'black "{file_path}"']
        elif tool["name"] == "autopep8":
            return [f'autopep8 --in-place "{file_path}"']
        return []
