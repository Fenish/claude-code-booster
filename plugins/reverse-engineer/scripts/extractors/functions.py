import json

import registry
import storage
from extractors import base


def extract(filepath, target):
    check = registry.require("rizin")
    if check:
        return check

    stdout, stderr, rc = base.run_tool(
        ["rizin", "-qc", "aaa; aflj", str(filepath)], timeout=600
    )
    if rc != 0:
        return {"error": f"rizin failed: {stderr.strip()[:200]}"}

    functions = []
    try:
        raw = json.loads(base.clean_json(stdout))
        for entry in raw:
            functions.append(
                {
                    "name": entry.get("name", ""),
                    "addr": hex(entry.get("offset", 0)),
                    "size": entry.get("size", 0),
                    "nargs": entry.get("nargs", 0),
                    "nbbs": entry.get("nbbs", 0),
                    "cc": entry.get("cc", 0),
                }
            )
    except (json.JSONDecodeError, TypeError):
        return {"error": "failed to parse rizin function output"}

    storage.update_section(target, "functions", functions)
    return f"Extracted {len(functions)} functions"


def run(filepath, target):
    return extract(filepath, target)
