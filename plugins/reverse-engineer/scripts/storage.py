import json
from datetime import date
from pathlib import Path

MAPS_DIR = Path(".claude/re-maps")

SECTIONS = [
    "headers",
    "imports",
    "exports",
    "strings",
    "functions",
    "structures",
    "patterns",
    "notes",
]


def _map_path(target):
    return MAPS_DIR / f"{target}.json"


def _load(target):
    path = _map_path(target)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _save(target, data):
    MAPS_DIR.mkdir(parents=True, exist_ok=True)
    path = _map_path(target)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def init(
    target,
    filepath,
    file_type,
    arch,
    size,
    size_human,
    md5,
    packing=None,
    framework=None,
):
    data = {
        "meta": {
            "target": target,
            "path": str(filepath),
            "type": file_type,
            "arch": arch,
            "size": size,
            "size_human": size_human,
            "md5": md5,
            "analyzed": str(date.today()),
            "packing": packing,
            "framework": framework,
        },
        "headers": {},
        "imports": [],
        "exports": [],
        "strings": {"total": 0, "categories": {}},
        "functions": [],
        "structures": [],
        "patterns": [],
        "notes": [],
    }
    _save(target, data)
    return data


def exists(target):
    return _map_path(target).exists()


def load(target):
    return _load(target)


def save(target, data):
    _save(target, data)


def delete(target):
    path = _map_path(target)
    if path.exists():
        path.unlink()
        return True
    return False


def list_maps():
    if not MAPS_DIR.exists():
        return []
    results = []
    for f in sorted(MAPS_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            meta = data.get("meta", {})
            counts = {}
            for s in SECTIONS:
                val = data.get(s)
                if isinstance(val, list):
                    counts[s] = len(val)
                elif isinstance(val, dict):
                    if s == "strings":
                        counts[s] = val.get("total", 0)
                    elif s == "headers":
                        counts[s] = len(val.get("sections", []))
                    else:
                        counts[s] = len(val)
            results.append(
                {
                    "target": meta.get("target", f.stem),
                    "path": meta.get("path", ""),
                    "type": meta.get("type", "?"),
                    "arch": meta.get("arch", "?"),
                    "sections": counts,
                }
            )
        except (json.JSONDecodeError, KeyError):
            continue
    return results


def summary(target):
    data = _load(target)
    if not data:
        return None
    out = dict(data["meta"])
    counts = {}
    for s in SECTIONS:
        val = data.get(s)
        if isinstance(val, list):
            counts[s] = len(val)
        elif isinstance(val, dict):
            if s == "strings":
                counts[s] = val.get("total", 0)
            elif s == "headers":
                counts[s] = len(val.get("sections", []))
            else:
                counts[s] = len(val)
    out["sections"] = counts
    return out


def update_section(target, section, data_update):
    data = _load(target)
    if not data:
        return False
    data[section] = data_update
    _save(target, data)
    return True


def append_section(target, section, items):
    data = _load(target)
    if not data:
        return False
    existing = data.get(section, [])
    if isinstance(existing, list):
        existing.extend(items if isinstance(items, list) else [items])
        data[section] = existing
    _save(target, data)
    return True


def query(target, section, filter_text=None, limit=20, offset=0, count_only=False):
    data = _load(target)
    if not data:
        return None

    section_data = data.get(section)
    if section_data is None:
        return {"error": f"unknown section: {section}"}

    if section == "strings":
        items = []
        cats = section_data.get("categories", {})
        if filter_text:
            fl = filter_text.lower()
            for cat, strings in cats.items():
                for s in strings:
                    if fl in s.lower():
                        items.append({"category": cat, "value": s})
        else:
            for cat, strings in cats.items():
                for s in strings:
                    items.append({"category": cat, "value": s})
        total = section_data.get("total", len(items))
    elif isinstance(section_data, list):
        if filter_text:
            fl = filter_text.lower()
            items = [i for i in section_data if fl in json.dumps(i).lower()]
        else:
            items = section_data
        total = len(items)
    elif isinstance(section_data, dict):
        items = [section_data]
        total = 1
    else:
        items = []
        total = 0

    if count_only:
        return {"section": section, "total": total}

    page = items[offset : offset + limit]
    return {
        "section": section,
        "total": total,
        "offset": offset,
        "limit": limit,
        "showing": len(page),
        "items": page,
    }


def search(target, query_text):
    data = _load(target)
    if not data:
        return None
    ql = query_text.lower()
    results = []
    for section in SECTIONS:
        val = data.get(section)
        if isinstance(val, list):
            for i, item in enumerate(val):
                dumped = json.dumps(item).lower()
                if ql in dumped:
                    results.append({"section": section, "index": i, "item": item})
        elif isinstance(val, dict):
            if section == "strings":
                for cat, strings in val.get("categories", {}).items():
                    for s in strings:
                        if ql in s.lower():
                            results.append(
                                {"section": "strings", "category": cat, "value": s}
                            )
            else:
                dumped = json.dumps(val).lower()
                if ql in dumped:
                    results.append({"section": section, "item": val})
    return results
