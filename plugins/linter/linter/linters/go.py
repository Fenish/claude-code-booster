from .base import BaseLinter


class GoLinter(BaseLinter):
    extensions = [".go"]
    tools = [
        {"cmd": "gofmt", "name": "gofmt"},
    ]

    def format_cmd(self, file_path, indent):
        return [f'gofmt -w "{file_path}"']
