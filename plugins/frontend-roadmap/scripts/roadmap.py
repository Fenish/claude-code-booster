#!/usr/bin/env python3
"""Frontend Roadmap CLI — guided preparation for frontend projects."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from steps import STEPS
from steps.step1_requirements import Step1Requirements, get_palettes_for_type
from steps.step2_references import Step2References
from steps.step3_platform import PLATFORM_INSTRUCTIONS, Step3Platform
from steps.step4_import import Step4Import
from steps.step5_techstack import Step5TechStack

DEFAULT_STATE = {
    "current_step": 1,
    "project": {
        "name": "",
        "description": "",
        "type": "",
        "target_audience": "",
        "key_features": [],
        "pages": [],
    },
    "branding": {
        "palette_name": "",
        "colors": {},
    },
    "references_collected": False,
    "platform": "",
    "tech_stack": {
        "framework": "",
        "styling": "Tailwind CSS",
        "ui_library": "",
    },
    "exports_imported": False,
    "completed_steps": [],
}

WORKSPACE_DIR = os.path.join(os.getcwd(), "frontend-roadmap")
STATE_FILE = os.path.join(WORKSPACE_DIR, "state.json")


def load_state():
    if not os.path.isfile(STATE_FILE):
        return None
    with open(STATE_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def cmd_init(_args):
    if os.path.isfile(STATE_FILE):
        print(f"Workspace already exists: {WORKSPACE_DIR}")
        print(
            "Use 'status' to see current progress or delete the folder to start over."
        )
        return 0

    os.makedirs(os.path.join(WORKSPACE_DIR, "preparation"), exist_ok=True)
    os.makedirs(os.path.join(WORKSPACE_DIR, "references"), exist_ok=True)
    os.makedirs(os.path.join(WORKSPACE_DIR, "exports"), exist_ok=True)
    save_state(DEFAULT_STATE.copy())
    print(f"Created workspace: {WORKSPACE_DIR}")
    print("  preparation/ — auto-generated docs for each step")
    print("  references/  — save inspiration screenshots here")
    print("  exports/     — place platform-exported code here")
    print("  state.json   — tracks your progress")
    print()
    print("Ready to start. Run 'status' to see the first step.")
    return 0


def cmd_status(_args):
    state = load_state()
    if not state:
        print("No workspace found. Run 'init' first.")
        return 1

    current = state.get("current_step", 1)
    completed = state.get("completed_steps", [])

    print("=== Frontend Roadmap Progress ===\n")
    for step_cls in STEPS:
        marker = (
            "done"
            if step_cls.number in completed
            else (">>>" if step_cls.number == current else "   ")
        )
        print(f"  [{marker}] Step {step_cls.number}: {step_cls.name}")
        if step_cls.number in completed:
            summary = step_cls.summary(state)
            for line in summary.split("\n"):
                print(f"         {line}")

    if current > len(STEPS):
        print("\n  All steps complete! Run 'finalize' to generate roadmap.md")
    else:
        step = STEPS[current - 1]
        print(f"\nCurrent step: {step.number} — {step.name}")
        print(f"  {step.description}")

    ref_count = Step2References.count_references(WORKSPACE_DIR)
    exp_count = Step4Import.count_files(WORKSPACE_DIR)
    print(f"\nFiles: {ref_count} references, {exp_count} exports")

    prep_dir = os.path.join(WORKSPACE_DIR, "preparation")
    if os.path.isdir(prep_dir):
        prep_files = [f for f in os.listdir(prep_dir) if f.endswith(".md")]
        if prep_files:
            print(f"Preparation docs: {', '.join(sorted(prep_files))}")
    return 0


def cmd_next(_args):
    state = load_state()
    if not state:
        print("No workspace found. Run 'init' first.")
        return 1

    current = state.get("current_step", 1)
    if current > len(STEPS):
        print("All steps complete. Run 'finalize' to generate roadmap.md")
        return 0

    step = STEPS[current - 1]
    output = {
        "step": step.number,
        "name": step.name,
        "description": step.description,
        "questions": step.questions(),
    }

    if step.number == 1:
        project_type = state.get("project", {}).get("type", "Web App")
        output["color_question"] = Step1Requirements.color_questions(project_type)

    if step.number == 2:
        proj = state.get("project", {})
        output["search_urls"] = Step2References.get_search_urls(
            proj.get("type", "Web App"),
            proj.get("name", ""),
            proj.get("description", ""),
        )

    if step.number == 3:
        output["platform_instructions"] = PLATFORM_INSTRUCTIONS

    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


def cmd_update(args):
    state = load_state()
    if not state:
        print("No workspace found. Run 'init' first.")
        return 1

    key = args.key
    value = args.value

    if value.startswith("[") or value.startswith("{"):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            pass

    parts = key.split(".")
    obj = state
    for p in parts[:-1]:
        if p not in obj:
            obj[p] = {}
        obj = obj[p]
    obj[parts[-1]] = value

    save_state(state)
    print(f"Updated {key}")
    return 0


def cmd_complete_step(args):
    state = load_state()
    if not state:
        print("No workspace found. Run 'init' first.")
        return 1

    step_num = args.step
    if step_num < 1 or step_num > len(STEPS):
        print(f"Invalid step number: {step_num}")
        return 1

    step = STEPS[step_num - 1]

    answers = {}
    if args.answers:
        try:
            answers = json.loads(args.answers)
        except json.JSONDecodeError:
            print("Invalid JSON for answers", file=sys.stderr)
            return 1

    state = step.apply(state, answers)
    save_state(state)

    if step_num == 1:
        path = Step1Requirements.save_requirements(state, WORKSPACE_DIR)
        print(f"  Saved: {path}")
    elif step_num == 3:
        path = Step3Platform.save_prompt(state, WORKSPACE_DIR)
        print(f"  Saved: {path}")
    elif step_num == 5:
        path = Step5TechStack.save_tech_stack(state, WORKSPACE_DIR)
        print(f"  Saved: {path}")

    print(f"Step {step_num} ({step.name}) completed.")
    return 0


def cmd_prompt(_args):
    state = load_state()
    if not state:
        print("No workspace found. Run 'init' first.")
        return 1

    if not state.get("platform"):
        print("Choose a platform first (step 3).")
        return 1

    prompt = Step3Platform.generate_prompt(state)
    platform = state["platform"]

    print(f"=== Prompt for {platform} ===\n")
    print(prompt)
    print(f"\n=== Instructions ===")
    print(
        PLATFORM_INSTRUCTIONS.get(
            platform, "Export the design files into the exports/ folder."
        )
    )

    Step3Platform.save_prompt(state, WORKSPACE_DIR)
    print(f"\nPrompt also saved to: preparation/platform-prompt.md")
    return 0


def list_dir_files(directory, prefix=""):
    files = []
    if not os.path.isdir(directory):
        return files
    for entry in sorted(os.listdir(directory)):
        full = os.path.join(directory, entry)
        rel = os.path.join(prefix, entry) if prefix else entry
        if os.path.isdir(full):
            files.extend(list_dir_files(full, rel))
        else:
            files.append(rel)
    return files


def cmd_finalize(_args):
    state = load_state()
    if not state:
        print("No workspace found. Run 'init' first.")
        return 1

    p = state.get("project", {})
    ts = state.get("tech_stack", {})
    platform = state.get("platform", "Not selected")

    ref_files = list_dir_files(os.path.join(WORKSPACE_DIR, "references"))
    exp_files = list_dir_files(os.path.join(WORKSPACE_DIR, "exports"))

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    pages_list = "\n".join(f"- {pg}" for pg in p.get("pages", [])) or "- Home"
    features_list = (
        "\n".join(f"- {f}" for f in p.get("key_features", [])) or "- Core functionality"
    )
    ref_list = (
        "\n".join(f"- `references/{f}`" for f in ref_files)
        or "- No reference files collected"
    )
    exp_list = (
        "\n".join(f"- `exports/{f}`" for f in exp_files) or "- No exports imported"
    )

    design_prompt = (
        Step3Platform.generate_prompt(state)
        if state.get("platform")
        else "No platform prompt generated."
    )

    framework = ts.get("framework", "Not selected")
    ui_lib = ts.get("ui_library", "None")

    framework_name = framework.split("+")[0].strip() if "+" in framework else framework
    file_structure = generate_file_structure(framework_name, p.get("pages", []))
    best_practices = generate_best_practices(framework_name, ui_lib)

    ref_heading = (
        f"{len(ref_files)} reference file(s) collected:"
        if ref_files
        else "No references collected."
    )
    exp_heading = (
        f"{len(exp_files)} export file(s) imported:"
        if exp_files
        else "No exports imported."
    )

    b = state.get("branding", {})
    colors = b.get("colors", {})

    if colors.get("primary"):
        branding_section = [
            "\n---",
            "\n## 2. Branding & Colors",
            f"\n**Palette:** {b.get('palette_name', 'Custom')}",
            "\n| Token      | Value |",
            "|------------|-------|",
            f"| Primary    | `{colors['primary']}` |",
            f"| Secondary  | `{colors.get('secondary', '-')}` |",
            f"| Accent     | `{colors.get('accent', '-')}` |",
            f"| Background | `{colors.get('background', '-')}` |",
            f"| Foreground | `{colors.get('foreground', '-')}` |",
            "\nUse these as the base design tokens. Map them to CSS variables or Tailwind theme config.",
        ]
    elif colors.get("custom"):
        branding_section = [
            "\n---",
            "\n## 2. Branding & Colors",
            f"\n**Custom palette:** {colors['custom']}",
            "\nInterpret these colors and create appropriate design tokens.",
        ]
    else:
        branding_section = [
            "\n---",
            "\n## 2. Branding & Colors",
            "\nNo color palette selected. Choose appropriate colors based on the project type and audience.",
        ]

    sections = [
        f"# Frontend Roadmap: {p.get('name', 'Untitled Project')}",
        f"\nGenerated: {now}",
        "\n---",
        "\n## 1. Project Overview",
        f"\n**Name:** {p.get('name', 'Untitled')}",
        f"**Type:** {p.get('type', 'Web App')}",
        f"**Description:** {p.get('description', 'No description provided.')}",
        f"**Target Audience:** {p.get('target_audience', 'General users')}",
        f"\n### Key Features\n{features_list}",
        f"\n### Pages\n{pages_list}",
        *branding_section,
        "\n---",
        "\n## 3. Visual References",
        f"\n{ref_heading}",
        f"\n{ref_list}",
        "\nReview these files for visual style, layout patterns, color schemes, and design language to match.",
        "\n---",
        "\n## 4. Design Platform",
        f"\n**Platform:** {platform}",
        f"\n### Prompt Used\n\nSee `preparation/platform-prompt.md` for the full prompt.\n\n```\n{design_prompt}\n```",
        "\n---",
        "\n## 5. Design Exports",
        f"\n{exp_heading}",
        f"\n{exp_list}",
        "\nReview these exported files for code patterns, component structure, and design implementation to adapt.",
        "\n---",
        "\n## 6. Tech Stack",
        "\n| Choice     | Selection |",
        "|------------|-----------|",
        f"| Framework  | {framework} |",
        f"| Styling    | {ts.get('styling', 'Tailwind CSS')} |",
        f"| UI Library | {ui_lib} |",
        "\nSee `preparation/tech-stack.md` for rationale.",
        "\n---",
        "\n## 7. Build Instructions",
        "\nYou are a senior frontend developer. Build the website described in this roadmap.",
        f"\n### Context\n- Project: {p.get('name', 'Untitled')} — {p.get('description', 'a web project')}",
        f"- Type: {p.get('type', 'Web App')}",
        f"- Audience: {p.get('target_audience', 'general users')}",
        "\n### Source Materials",
        "- Reference images in `references/` — match the visual style",
        "- Exported design code in `exports/` — review for patterns and adapt",
        "- Preparation docs in `preparation/` — requirements, prompt, tech decisions",
        "- Adapt and improve the exported code, don't just copy it",
        f"\n### Technical Requirements\n- Framework: {framework}",
        f"- UI Library: {ui_lib}",
        "- Fully responsive (mobile-first)",
        "- Accessible (WCAG 2.1 AA)",
        "- Clean, maintainable code with proper component structure",
        "- Smooth animations and transitions",
        "- Dark/light mode support where applicable",
        "- SEO-friendly markup and meta tags",
        "- Optimized images and assets",
        f"\n### Pages to Build\n{pages_list}",
        f"\n### Key Features to Implement\n{features_list}",
        "\n---",
        f"\n## 8. Recommended File Structure\n\n```\n{file_structure}\n```",
        "\n---",
        f"\n## 9. Best Practices\n\n{best_practices}\n",
    ]

    roadmap = "\n".join(sections)

    roadmap_path = os.path.join(WORKSPACE_DIR, "roadmap.md")
    with open(roadmap_path, "w", encoding="utf-8") as f:
        f.write(roadmap)

    print(f"Roadmap generated: {roadmap_path}")
    print(f"  Project: {p.get('name', 'Untitled')}")
    print(f"  Stack: {framework} + {ui_lib}")
    print(f"  References: {len(ref_files)} files")
    print(f"  Exports: {len(exp_files)} files")
    return 0


def generate_file_structure(framework, pages):
    pages_lower = [p.lower().replace(" ", "-") for p in pages] if pages else ["home"]

    if framework in ("Next.js", "Next"):
        page_lines = "\n".join(f"    {p}/page.tsx" for p in pages_lower)
        return (
            f"src/\n"
            f"  app/\n"
            f"    layout.tsx\n"
            f"    page.tsx\n"
            f"{page_lines}\n"
            f"  components/\n"
            f"    ui/\n"
            f"    layout/\n"
            f"    sections/\n"
            f"  lib/\n"
            f"  styles/\n"
            f"    globals.css\n"
            f"  public/\n"
            f"    images/"
        )
    elif framework in ("Vue", "Nuxt"):
        page_lines = "\n".join(f"    {p}.vue" for p in pages_lower)
        return (
            f"src/\n"
            f"  pages/\n"
            f"{page_lines}\n"
            f"  components/\n"
            f"    ui/\n"
            f"    layout/\n"
            f"    sections/\n"
            f"  composables/\n"
            f"  assets/\n"
            f"    css/\n"
            f"  public/\n"
            f"    images/"
        )
    elif framework == "Astro":
        page_lines = "\n".join(f"    {p}.astro" for p in pages_lower)
        return (
            f"src/\n"
            f"  pages/\n"
            f"{page_lines}\n"
            f"  components/\n"
            f"    ui/\n"
            f"    layout/\n"
            f"    sections/\n"
            f"  layouts/\n"
            f"    Base.astro\n"
            f"  styles/\n"
            f"    global.css\n"
            f"  public/\n"
            f"    images/"
        )
    else:
        page_lines = "\n".join(
            f"    {p.title().replace('-', '')}.tsx" for p in pages_lower
        )
        return (
            f"src/\n"
            f"  pages/\n"
            f"{page_lines}\n"
            f"  components/\n"
            f"    ui/\n"
            f"    layout/\n"
            f"    sections/\n"
            f"  hooks/\n"
            f"  lib/\n"
            f"  styles/\n"
            f"    index.css\n"
            f"  public/\n"
            f"    images/"
        )


def generate_best_practices(framework, ui_lib):
    lines = [
        "- Use semantic HTML elements (`<header>`, `<main>`, `<nav>`, `<section>`, `<footer>`)",
        "- Keep components small and focused — one responsibility per component",
        "- Use CSS variables or Tailwind theme tokens for consistent colors and spacing",
        "- Lazy-load images and heavy components",
        "- Add proper `alt` text to all images",
        "- Use `aria-` attributes where native semantics aren't enough",
        "- Test on mobile, tablet, and desktop breakpoints",
        "- Optimize fonts — use `font-display: swap` and subset where possible",
    ]

    if "Next" in framework:
        lines.extend(
            [
                "- Use Next.js Image component for automatic optimization",
                "- Prefer Server Components where possible, use `'use client'` only when needed",
                "- Use `metadata` exports for SEO on each page",
            ]
        )
    elif "Astro" in framework:
        lines.extend(
            [
                "- Use Astro's built-in image optimization",
                "- Keep interactive islands minimal — use `client:visible` for below-fold components",
            ]
        )
    elif "Vue" in framework or "Nuxt" in framework:
        lines.extend(
            [
                "- Use Nuxt's `useHead()` for SEO meta tags",
                "- Leverage auto-imports for components and composables",
            ]
        )

    if ui_lib and ui_lib != "None":
        lines.append(
            f"- Follow {ui_lib} patterns and conventions for consistent component APIs"
        )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Frontend Roadmap — project preparation CLI"
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init", help="Create workspace and state file")
    sub.add_parser("status", help="Show current progress")
    sub.add_parser("next", help="Get current step questions as JSON")
    sub.add_parser("prompt", help="Generate design platform prompt")
    sub.add_parser("finalize", help="Generate roadmap.md from collected data")

    up = sub.add_parser("update", help="Update a state key")
    up.add_argument("key", help="Dot-separated key (e.g. project.name)")
    up.add_argument("value", help="Value to set (JSON for arrays/objects)")

    for alias in ("complete-step", "complete"):
        cs = sub.add_parser(alias, help="Mark a step as complete")
        cs.add_argument("step", type=int, help="Step number (1-5)")
        cs.add_argument("--answers", help="JSON object of answers", default="{}")

    args = parser.parse_args()

    commands = {
        "init": cmd_init,
        "status": cmd_status,
        "next": cmd_next,
        "update": cmd_update,
        "complete-step": cmd_complete_step,
        "complete": cmd_complete_step,
        "prompt": cmd_prompt,
        "finalize": cmd_finalize,
    }

    if args.command in commands:
        sys.exit(commands[args.command](args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
