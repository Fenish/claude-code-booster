import json

import registry
import storage
from extractors import base


def extract(filepath, target):
    check = registry.require("rizin")
    if check:
        return check

    stdout, stderr, rc = base.run_tool(
        ["rizin", "-qc", "iEj", str(filepath)], timeout=120
    )
    if rc != 0:
        return {"error": f"rizin failed: {stderr.strip()[:200]}"}

    exports = []
    try:
        raw = json.loads(base.clean_json(stdout))
        for entry in raw:
            exports.append(
                {
                    "name": entry.get("name", ""),
                    "vaddr": hex(entry.get("vaddr", 0)),
                    "paddr": hex(entry.get("paddr", 0)),
                    "size": entry.get("size", 0),
                    "type": entry.get("type", ""),
                }
            )
    except (json.JSONDecodeError, TypeError):
        return {"error": "failed to parse rizin export output"}

    storage.update_section(target, "exports", exports)
    return f"Extracted {len(exports)} exports"


def run(filepath, target):
    return extract(filepath, target)
