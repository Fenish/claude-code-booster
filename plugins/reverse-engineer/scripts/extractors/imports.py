import json

import registry
import storage
from extractors import base


def extract(filepath, target):
    check = registry.require("rizin")
    if check:
        return check

    stdout, stderr, rc = base.run_tool(
        ["rizin", "-qc", "aaa; iij", str(filepath)], timeout=300
    )
    if rc != 0:
        return {"error": f"rizin failed: {stderr.strip()[:200]}"}

    imports = []
    try:
        raw = json.loads(stdout)
        dll_map = {}
        for entry in raw:
            lib = entry.get("lib", "unknown")
            name = entry.get("name", "")
            ordinal = entry.get("ordinal", 0)
            plt = entry.get("plt", 0)
            if lib not in dll_map:
                dll_map[lib] = {"dll": lib, "functions": []}
            dll_map[lib]["functions"].append(
                {
                    "name": name,
                    "ordinal": ordinal,
                    "plt": hex(plt) if plt else None,
                }
            )
        for dll, data in dll_map.items():
            data["count"] = len(data["functions"])
            imports.append(data)
    except (json.JSONDecodeError, TypeError):
        return {"error": "failed to parse rizin import output"}

    storage.update_section(target, "imports", imports)
    total_funcs = sum(i["count"] for i in imports)
    return f"Extracted {total_funcs} imports from {len(imports)} DLLs"


def run(filepath, target):
    return extract(filepath, target)
