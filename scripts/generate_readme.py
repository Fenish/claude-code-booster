#!/usr/bin/env python3
"""Reads marketplace.json + plugin dirs, generates categorized plugin list in README.md."""

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
README = ROOT / "README.md"

PLUGINS_START = "<!-- PLUGINS:START -->"
PLUGINS_END = "<!-- PLUGINS:END -->"
TOC_START = "<!-- TOC:START -->"
TOC_END = "<!-- TOC:END -->"

ICON_BASE = "https://raw.githubusercontent.com/Fenish/claude-code-booster/main/.github/assets/icons"

CATEGORY_LABELS = {
    "productivity": "Productivity",
    "security": "Security",
    "testing": "Testing",
    "devops": "DevOps",
    "utilities": "Utilities",
}


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
    lines = []
    for cat_key in sorted(categories.keys()):
        label = CATEGORY_LABELS.get(cat_key, cat_key.title())
        icon = f'<img src="{ICON_BASE}/{cat_key}.svg" width="14" height="14" align="absmiddle" />'
        count = len(categories[cat_key])
        lines.append(f'<a href="#{cat_key}">{icon} {label}</a> ({count})<br>')
    return "\n".join(lines)


def build_plugins(categories: dict[str, list[dict]]) -> str:
    lines = []
    for cat_key in sorted(categories.keys()):
        label = CATEGORY_LABELS.get(cat_key, cat_key.title())
        icon = f'<img src="{ICON_BASE}/{cat_key}.svg" width="16" height="16" align="absmiddle" />'
        lines.append(f'<h3 id="{cat_key}">{icon} {label}</h3>')
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
        source = ROOT / entry["source"]
        category = entry.get("category", "utilities")
        source_rel = entry["source"]
        info = scan_plugin(source, category, source_rel)
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
