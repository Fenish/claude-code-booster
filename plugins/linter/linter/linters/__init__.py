from .base import BaseLinter, detect_indent
from .javascript import JavaScriptLinter
from .python_lint import PythonLinter
from .rust import RustLinter
from .go import GoLinter
from .markdown import MarkdownLinter
from .json_lint import JsonLinter
from .yaml_lint import YamlLinter
from .css import CssLinter
from .html import HtmlLinter
from .shell import ShellLinter

LINTERS = [
    JavaScriptLinter(),
    PythonLinter(),
    RustLinter(),
    GoLinter(),
    MarkdownLinter(),
    JsonLinter(),
    YamlLinter(),
    CssLinter(),
    HtmlLinter(),
    ShellLinter(),
]

EXTENSION_MAP = {}
for linter in LINTERS:
    for ext in linter.extensions:
        EXTENSION_MAP[ext] = linter


def get_linter(file_path):
    import os
    ext = os.path.splitext(file_path)[1].lower()
    return EXTENSION_MAP.get(ext)
