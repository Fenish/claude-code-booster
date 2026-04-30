#!/usr/bin/env python3
"""Reads marketplace.json + plugin dirs, generates categorized plugin list in README.md."""

import base64
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
README = ROOT / "README.md"
ICONS_DIR = ROOT / ".github" / "assets" / "icons"

PLUGINS_START = "<!-- PLUGINS:START -->"
PLUGINS_END = "<!-- PLUGINS:END -->"
TOC_START = "<!-- TOC:START -->"
TOC_END = "<!-- TOC:END -->"

CATEGORY_LABELS = {
    "productivity": "Productivity",
    "security": "Security",
    "testing": "Testing",
    "devops": "DevOps",
    "utilities": "Utilities",
}

CATEGORY_COLORS = {
    "productivity": "7C3AED",
    "security": "DC2626",
    "testing": "0EA5E9",
    "devops": "F59E0B",
    "utilities": "10B981",
}


def icon_badge(cat_key: str, label: str, count: int = 0) -> str:
    color = CATEGORY_COLORS.get(cat_key, "7C3AED")
    svg_path = ICONS_DIR / f"{cat_key}.svg"
    text = f"{label} ({count})" if count else label
    if not svg_path.exists():
        return f"![{text}](https://img.shields.io/badge/-{quote(text)}-{color}?style=flat-square)"
    svg = svg_path.read_text(encoding="utf-8").strip()
    svg = svg.replace('stroke="#7C3AED"', 'stroke="white"')
    b64 = base64.b64encode(svg.encode()).decode()
    return f"![{text}](https://img.shields.io/badge/{quote(text)}-{color}?style=flat-square&logo=data:image/svg%2bxml;base64,{b64}&logoColor=white)"


def scan_plugin(source_dir: Path, category: str, source_rel: str) -> dict | None:
    plugin_json = source_dir / ".claude-plugin" / "plugin.json"
    if not plugin_json.exists():
        return None
    meta = json.loads(plugin_json.read_text(encoding="utf-8"))
    return {
        "name": meta.get("name", source_dir.name),
        "description": meta.get("description", ""),
        "category": category,
        "path": source_rel,
    }


def build_toc(categories: dict[str, list[dict]]) -> str:
    parts = []
    for cat_key in sorted(categories.keys()):
        label = CATEGORY_LABELS.get(cat_key, cat_key.title())
        count = len(categories[cat_key])
        badge = icon_badge(cat_key, label, count)
        parts.append(f"[{badge}](#{cat_key})")
    return " ".join(parts)


def build_plugins(categories: dict[str, list[dict]]) -> str:
    lines = []
    for cat_key in sorted(categories.keys()):
        label = CATEGORY_LABELS.get(cat_key, cat_key.title())
        badge = icon_badge(cat_key, label)
        lines.append(f"### {badge}")
        lines.append("")
        for p in categories[cat_key]:
            lines.append(f"- **[{p['name']}]({p['path']})** — {p['description']}")
        lines.append("")
    return "\n".join(lines).rstrip()


def inject(text: str, start: str, end: str, content: str) -> str:
    pattern = re.compile(rf"{re.escape(start)}.*?{re.escape(end)}", re.DOTALL)
    block = f"{start}\n{content}\n{end}"
    if pattern.search(text):
        return pattern.sub(block, text)
    return text


def main():
    marketplace = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    categories = defaultdict(list)

    for entry in marketplace.get("plugins", []):
        source = entry["source"]
        category = entry.get("category", "utilities")

        if source.startswith("github:") or source.startswith("http"):
            categories[category].append(
                {
                    "name": entry["name"],
                    "description": entry.get("description", ""),
                    "category": category,
                    "path": entry.get("homepage", source),
                }
            )
        else:
            source_dir = ROOT / source
            source_rel = source
            info = scan_plugin(source_dir, category, source_rel)
            if info:
                categories[category].append(info)

    toc = build_toc(categories)
    plugins = build_plugins(categories)

    readme_text = README.read_text(encoding="utf-8")
    readme_text = inject(readme_text, TOC_START, TOC_END, toc)
    readme_text = inject(readme_text, PLUGINS_START, PLUGINS_END, plugins)

    plugin_count = sum(len(v) for v in categories.values())
    hook_count = sum(
        1
        for cat in categories.values()
        for p in cat
        if (ROOT / p["path"] / "hooks" / "hooks.json").exists()
    )
    readme_text = re.sub(r"plugins-\d+-", f"plugins-{plugin_count}-", readme_text)
    readme_text = re.sub(r"hooks-\d+-", f"hooks-{hook_count}-", readme_text)

    README.write_text(readme_text, encoding="utf-8")
    print(f"Updated README: {plugin_count} plugins, {len(categories)} categories")


if __name__ == "__main__":
    main()
