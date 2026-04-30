#!/usr/bin/env python3
"""RE memory map manager — JSON storage with CLI tool extraction.

Usage:
    python re_map.py triage <filepath>
    python re_map.py analyze <filepath> [--target NAME]
    python re_map.py extract-headers <filepath> <target>
    python re_map.py extract-strings <filepath> <target>
    python re_map.py extract-imports <filepath> <target>
    python re_map.py extract-exports <filepath> <target>
    python re_map.py extract-functions <filepath> <target>
    python re_map.py query <target> <section> [--filter TEXT] [--limit N] [--offset N] [--count]
    python re_map.py search <target> <query>
    python re_map.py summary <target>
    python re_map.py list
    python re_map.py delete <target>
    python re_map.py set <target> <section> <content>
    python re_map.py append <target> <section> <content>
    python re_map.py tools
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import registry
import storage
import triage
from extractors import exports, functions, headers, imports, strings


def cmd_triage(args):
    result = triage.run(args.filepath)
    print(json.dumps(result, indent=2))


def cmd_analyze(args):
    filepath = args.filepath
    target = args.target or os.path.splitext(os.path.basename(filepath))[0]

    tri = triage.run(filepath)
    if "error" in tri:
        print(json.dumps(tri, indent=2))
        sys.exit(1)

    storage.init(
        target=target,
        filepath=filepath,
        file_type=tri["type"],
        arch=tri["arch"],
        size=tri["size"],
        size_human=tri["size_human"],
        md5=tri["md5"],
        packing=tri["packing"],
        framework=tri["framework"],
    )

    results = {"target": target, "type": tri["type"], "arch": tri["arch"]}
    errors = []

    str_result = strings.run(filepath, target)
    if isinstance(str_result, dict) and "error" in str_result:
        errors.append(f"strings: {str_result['error']}")
    else:
        results["strings"] = str_result

    for name, extractor in [
        ("headers", headers),
        ("imports", imports),
        ("exports", exports),
        ("functions", functions),
    ]:
        ext_result = extractor.run(filepath, target)
        if isinstance(ext_result, dict) and "error" in ext_result:
            errors.append(f"{name}: {ext_result['error']}")
        else:
            results[name] = ext_result

    if errors:
        results["errors"] = errors

    print(json.dumps(results, indent=2))


def cmd_extract(args, extractor):
    if not storage.exists(args.target):
        print(
            json.dumps({"error": f"map not found: {args.target}. Run 'analyze' first."})
        )
        sys.exit(1)
    result = extractor.run(args.filepath, args.target)
    if isinstance(result, dict):
        print(json.dumps(result, indent=2))
    else:
        print(result)


def cmd_query(args):
    if not storage.exists(args.target):
        print(json.dumps({"error": f"map not found: {args.target}"}))
        sys.exit(1)
    result = storage.query(
        args.target,
        args.section,
        filter_text=args.filter,
        limit=args.limit,
        offset=args.offset,
        count_only=args.count,
    )
    if result is None:
        print(json.dumps({"error": f"map not found: {args.target}"}))
    else:
        print(json.dumps(result, indent=2))


def cmd_search(args):
    results = storage.search(args.target, args.query)
    if results is None:
        print(json.dumps({"error": f"map not found: {args.target}"}))
        sys.exit(1)
    print(json.dumps({"matches": len(results), "results": results[:30]}, indent=2))


def cmd_summary(args):
    result = storage.summary(args.target)
    if result is None:
        print(json.dumps({"error": f"map not found: {args.target}"}))
        sys.exit(1)
    print(json.dumps(result, indent=2))


def cmd_list(args):
    maps = storage.list_maps()
    if not maps:
        print("No maps.")
        return
    for m in maps:
        filled = sum(1 for v in m["sections"].values() if v > 0)
        total = len(m["sections"])
        print(f"  {m['target']} | {m['type']}/{m['arch']} | {filled}/{total} sections")


def cmd_delete(args):
    if storage.delete(args.target):
        print(f"DELETED: {args.target}")
    else:
        print(f"NOT_FOUND: {args.target}")
        sys.exit(1)


def cmd_set(args):
    if not storage.exists(args.target):
        print(json.dumps({"error": f"map not found: {args.target}"}))
        sys.exit(1)
    content = args.content
    if content == "-":
        content = sys.stdin.read()
    storage.update_section(args.target, args.section, content.strip())
    print(f"OK: [{args.section}]")


def cmd_append(args):
    if not storage.exists(args.target):
        print(json.dumps({"error": f"map not found: {args.target}"}))
        sys.exit(1)
    content = args.content
    if content == "-":
        content = sys.stdin.read()
    storage.append_section(args.target, args.section, content.strip())
    print(f"OK: [{args.section}] appended")


def cmd_tools(args):
    result = registry.check_all()
    print(f"Installed ({len(result['available'])}):")
    for t in result["available"]:
        print(f"  + {t['name']} — {t['path']}")
    print(f"\nMissing ({len(result['missing'])}):")
    for t in result["missing"]:
        print(f"  - {t['name']} — {t['install']}")


def main():
    parser = argparse.ArgumentParser(description="RE memory map manager")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("triage").add_argument("filepath")

    p = sub.add_parser("analyze")
    p.add_argument("filepath")
    p.add_argument("--target", default="")

    for name in (
        "extract-headers",
        "extract-strings",
        "extract-imports",
        "extract-exports",
        "extract-functions",
    ):
        p = sub.add_parser(name)
        p.add_argument("filepath")
        p.add_argument("target")

    p = sub.add_parser("query")
    p.add_argument("target")
    p.add_argument("section")
    p.add_argument("--filter", default=None)
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--count", action="store_true")

    p = sub.add_parser("search")
    p.add_argument("target")
    p.add_argument("query")

    sub.add_parser("summary").add_argument("target")
    sub.add_parser("list")
    sub.add_parser("delete").add_argument("target")

    p = sub.add_parser("set")
    p.add_argument("target")
    p.add_argument("section")
    p.add_argument("content")

    p = sub.add_parser("append")
    p.add_argument("target")
    p.add_argument("section")
    p.add_argument("content")

    sub.add_parser("tools")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    extractors_map = {
        "extract-headers": headers,
        "extract-strings": strings,
        "extract-imports": imports,
        "extract-exports": exports,
        "extract-functions": functions,
    }

    if args.command == "triage":
        cmd_triage(args)
    elif args.command == "analyze":
        cmd_analyze(args)
    elif args.command in extractors_map:
        cmd_extract(args, extractors_map[args.command])
    elif args.command == "query":
        cmd_query(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "summary":
        cmd_summary(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "delete":
        cmd_delete(args)
    elif args.command == "set":
        cmd_set(args)
    elif args.command == "append":
        cmd_append(args)
    elif args.command == "tools":
        cmd_tools(args)


if __name__ == "__main__":
    main()
