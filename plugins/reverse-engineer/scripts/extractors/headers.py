import json

import registry
import storage
from extractors import base


def extract(filepath, target):
    check = registry.require("rizin")
    if check:
        return check

    stdout, stderr, rc = base.run_tool(
        ["rizin", "-qc", "iSj", str(filepath)], timeout=120
    )
    if rc != 0:
        return {"error": f"rizin failed: {stderr.strip()[:200]}"}

    sections = []
    try:
        raw = json.loads(base.clean_json(stdout))
        for s in raw:
            sections.append(
                {
                    "name": s.get("name", ""),
                    "size": s.get("size", 0),
                    "vsize": s.get("vsize", 0),
                    "vaddr": hex(s.get("vaddr", 0)),
                    "paddr": hex(s.get("paddr", 0)),
                    "perm": s.get("perm", ""),
                }
            )
    except (json.JSONDecodeError, TypeError):
        return {"error": "failed to parse rizin section output"}

    stdout2, _, rc2 = base.run_tool(["rizin", "-qc", "iIj", str(filepath)], timeout=30)
    info = {}
    if rc2 == 0:
        try:
            raw2 = json.loads(stdout2)
            info = {
                "arch": raw2.get("arch", ""),
                "bits": raw2.get("bits", 0),
                "os": raw2.get("os", ""),
                "machine": raw2.get("machine", ""),
                "format": raw2.get("bintype", ""),
                "endian": raw2.get("endian", ""),
                "canary": raw2.get("canary", False),
                "nx": raw2.get("nx", False),
                "pic": raw2.get("pic", False),
                "stripped": raw2.get("stripped", False),
            }
        except (json.JSONDecodeError, TypeError):
            pass

    headers = {"info": info, "sections": sections}
    storage.update_section(target, "headers", headers)
    return {"ok": True, "sections": len(sections), "info": info}


def run(filepath, target):
    result = extract(filepath, target)
    if "error" in result:
        return result
    info = result.get("info", {})
    arch = info.get("arch", "?")
    bits = info.get("bits", "?")
    return f"Extracted {result['sections']} sections ({arch}/{bits}bit)"
