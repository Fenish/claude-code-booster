"""Step 1: Gather project requirements and branding."""

import os

COLOR_PALETTES = {
    "SaaS": [
        {
            "name": "Trust Blue",
            "description": "Professional, trustworthy — great for B2B tools",
            "primary": "#2563EB",
            "secondary": "#1E40AF",
            "accent": "#3B82F6",
            "background": "#F8FAFC",
            "foreground": "#0F172A",
        },
        {
            "name": "Growth Green",
            "description": "Fresh, productive — great for productivity/finance tools",
            "primary": "#059669",
            "secondary": "#047857",
            "accent": "#10B981",
            "background": "#F0FDF4",
            "foreground": "#022C22",
        },
        {
            "name": "Modern Violet",
            "description": "Innovative, premium — great for AI/tech products",
            "primary": "#7C3AED",
            "secondary": "#6D28D9",
            "accent": "#8B5CF6",
            "background": "#FAF5FF",
            "foreground": "#1E1B4B",
        },
        {
            "name": "Warm Coral",
            "description": "Friendly, approachable — great for team/social tools",
            "primary": "#F43F5E",
            "secondary": "#E11D48",
            "accent": "#FB7185",
            "background": "#FFF1F2",
            "foreground": "#1C1917",
        },
    ],
    "Portfolio": [
        {
            "name": "Minimal Mono",
            "description": "Clean, elegant — lets the work speak for itself",
            "primary": "#18181B",
            "secondary": "#27272A",
            "accent": "#A1A1AA",
            "background": "#FAFAFA",
            "foreground": "#09090B",
        },
        {
            "name": "Creative Orange",
            "description": "Bold, energetic — stands out and shows personality",
            "primary": "#EA580C",
            "secondary": "#C2410C",
            "accent": "#FB923C",
            "background": "#FFFBEB",
            "foreground": "#1C1917",
        },
        {
            "name": "Studio Indigo",
            "description": "Sophisticated, artistic — great for design/creative portfolios",
            "primary": "#4F46E5",
            "secondary": "#4338CA",
            "accent": "#818CF8",
            "background": "#F5F3FF",
            "foreground": "#1E1B4B",
        },
        {
            "name": "Dark Luxe",
            "description": "Premium, high-contrast — dark-first with gold accents",
            "primary": "#F5F5F4",
            "secondary": "#D4A574",
            "accent": "#C2956B",
            "background": "#0C0A09",
            "foreground": "#FAFAF9",
        },
    ],
    "Web App": [
        {
            "name": "Ocean Blue",
            "description": "Calm, focused — great for dashboards and data apps",
            "primary": "#0284C7",
            "secondary": "#0369A1",
            "accent": "#38BDF8",
            "background": "#F0F9FF",
            "foreground": "#0C4A6E",
        },
        {
            "name": "Slate Pro",
            "description": "Neutral, professional — works for any business app",
            "primary": "#475569",
            "secondary": "#334155",
            "accent": "#6366F1",
            "background": "#F8FAFC",
            "foreground": "#0F172A",
        },
        {
            "name": "Emerald Dash",
            "description": "Clean, actionable — great for task/project management",
            "primary": "#059669",
            "secondary": "#047857",
            "accent": "#34D399",
            "background": "#ECFDF5",
            "foreground": "#064E3B",
        },
        {
            "name": "Neon Dark",
            "description": "Developer-focused, modern — dark theme with vibrant accents",
            "primary": "#22D3EE",
            "secondary": "#06B6D4",
            "accent": "#A78BFA",
            "background": "#0F172A",
            "foreground": "#F1F5F9",
        },
    ],
    "E-commerce": [
        {
            "name": "Luxury Black",
            "description": "Premium, high-end — great for fashion/luxury brands",
            "primary": "#18181B",
            "secondary": "#27272A",
            "accent": "#D4AF37",
            "background": "#FAFAFA",
            "foreground": "#09090B",
        },
        {
            "name": "Fresh Teal",
            "description": "Modern, trustworthy — great for general retail",
            "primary": "#0D9488",
            "secondary": "#0F766E",
            "accent": "#2DD4BF",
            "background": "#F0FDFA",
            "foreground": "#134E4A",
        },
        {
            "name": "Warm Commerce",
            "description": "Inviting, conversion-focused — great for food/lifestyle",
            "primary": "#DC2626",
            "secondary": "#B91C1C",
            "accent": "#F97316",
            "background": "#FFFBEB",
            "foreground": "#1C1917",
        },
        {
            "name": "Clean Blue",
            "description": "Reliable, professional — great for electronics/tech stores",
            "primary": "#2563EB",
            "secondary": "#1D4ED8",
            "accent": "#60A5FA",
            "background": "#F8FAFC",
            "foreground": "#0F172A",
        },
    ],
    "Landing Page": [
        {
            "name": "Bold Gradient",
            "description": "Eye-catching, modern — purple to blue gradient feel",
            "primary": "#7C3AED",
            "secondary": "#2563EB",
            "accent": "#EC4899",
            "background": "#FAFAFA",
            "foreground": "#18181B",
        },
        {
            "name": "Startup Green",
            "description": "Fresh, optimistic — great for tech/startup launches",
            "primary": "#16A34A",
            "secondary": "#15803D",
            "accent": "#4ADE80",
            "background": "#F0FDF4",
            "foreground": "#14532D",
        },
        {
            "name": "Midnight Launch",
            "description": "Dark, dramatic — great for product reveals and launches",
            "primary": "#E2E8F0",
            "secondary": "#3B82F6",
            "accent": "#F472B6",
            "background": "#020617",
            "foreground": "#F1F5F9",
        },
        {
            "name": "Warm Sunset",
            "description": "Energetic, warm — great for creative/lifestyle products",
            "primary": "#EA580C",
            "secondary": "#DC2626",
            "accent": "#FBBF24",
            "background": "#FFFBEB",
            "foreground": "#1C1917",
        },
    ],
}


def get_palettes_for_type(project_type):
    return COLOR_PALETTES.get(project_type, COLOR_PALETTES["Web App"])


class Step1Requirements:
    number = 1
    name = "Project Requirements"
    description = (
        "Gather project type, description, audience, features, pages, and brand colors."
    )

    @staticmethod
    def questions():
        return [
            {
                "key": "project.type",
                "question": "What type of project is this?",
                "header": "Project type",
                "options": [
                    {
                        "label": "SaaS",
                        "description": "Software as a Service web application",
                    },
                    {
                        "label": "Portfolio",
                        "description": "Personal or agency portfolio site",
                    },
                    {"label": "Web App", "description": "Interactive web application"},
                    {
                        "label": "E-commerce",
                        "description": "Online store or marketplace",
                    },
                    {
                        "label": "Landing Page",
                        "description": "Single-page marketing or product page",
                    },
                ],
            },
            {
                "key": "project.description",
                "question": "Describe the project in detail — what is it about, what problem does it solve?",
                "header": "Description",
                "free_text": True,
            },
            {
                "key": "project.name",
                "question": "What's the project name?",
                "header": "Name",
                "free_text": True,
            },
            {
                "key": "project.target_audience",
                "question": "Who is the target audience?",
                "header": "Audience",
                "free_text": True,
            },
            {
                "key": "project.key_features",
                "question": "What are the key features? (comma-separated list)",
                "header": "Features",
                "free_text": True,
                "parse": "comma_list",
            },
            {
                "key": "project.pages",
                "question": "What pages do you need? (comma-separated list, e.g. Home, About, Pricing, Dashboard)",
                "header": "Pages",
                "free_text": True,
                "parse": "comma_list",
            },
        ]

    @staticmethod
    def color_questions(project_type):
        palettes = get_palettes_for_type(project_type)
        options = []
        for p in palettes:
            preview = (
                f"Primary:    {p['primary']}\n"
                f"Secondary:  {p['secondary']}\n"
                f"Accent:     {p['accent']}\n"
                f"Background: {p['background']}\n"
                f"Foreground: {p['foreground']}"
            )
            options.append(
                {
                    "label": p["name"],
                    "description": p["description"],
                    "preview": preview,
                }
            )
        return {
            "key": "branding.palette",
            "question": "Which color palette fits your project? Pick one or describe your own colors.",
            "header": "Colors",
            "options": options,
            "palettes": palettes,
        }

    @staticmethod
    def apply(state, answers):
        for key, value in answers.items():
            if key == "branding.palette":
                if "branding" not in state:
                    state["branding"] = {"palette_name": "", "colors": {}}
                project_type = state.get("project", {}).get("type", "Web App")
                palettes = get_palettes_for_type(project_type)
                matched = next((p for p in palettes if p["name"] == value), None)
                if matched:
                    state["branding"]["palette_name"] = matched["name"]
                    state["branding"]["colors"] = {
                        "primary": matched["primary"],
                        "secondary": matched["secondary"],
                        "accent": matched["accent"],
                        "background": matched["background"],
                        "foreground": matched["foreground"],
                    }
                else:
                    state["branding"]["palette_name"] = "Custom"
                    state["branding"]["colors"] = {"custom": value}
                continue
            if key == "branding.colors":
                if "branding" not in state:
                    state["branding"] = {"palette_name": "Custom", "colors": {}}
                if isinstance(value, dict):
                    state["branding"]["colors"] = value
                else:
                    state["branding"]["colors"] = {"custom": value}
                continue
            parts = key.split(".")
            obj = state
            for p in parts[:-1]:
                if p not in obj:
                    obj[p] = {}
                obj = obj[p]
            obj[parts[-1]] = value
        state["completed_steps"].append(1)
        state["current_step"] = 2
        return state

    @staticmethod
    def save_requirements(state, workspace_dir):
        p = state.get("project", {})
        b = state.get("branding", {})
        colors = b.get("colors", {})

        features = "\n".join(f"- {f}" for f in p.get("key_features", [])) or "- TBD"
        pages = "\n".join(f"- {pg}" for pg in p.get("pages", [])) or "- Home"

        lines = [
            f"# Project Requirements: {p.get('name', 'Untitled')}",
            f"\n**Type:** {p.get('type', 'Web App')}",
            f"**Description:** {p.get('description', 'No description.')}",
            f"**Target Audience:** {p.get('target_audience', 'General users')}",
            f"\n## Key Features\n{features}",
            f"\n## Pages\n{pages}",
        ]

        if colors.get("primary"):
            lines.extend(
                [
                    f"\n## Brand Colors — {b.get('palette_name', 'Custom')}",
                    f"\n| Token      | Value |",
                    f"|------------|-------|",
                    f"| Primary    | `{colors['primary']}` |",
                    f"| Secondary  | `{colors.get('secondary', '-')}` |",
                    f"| Accent     | `{colors.get('accent', '-')}` |",
                    f"| Background | `{colors.get('background', '-')}` |",
                    f"| Foreground | `{colors.get('foreground', '-')}` |",
                ]
            )
        elif colors.get("custom"):
            lines.append(f"\n## Brand Colors\n\nCustom: {colors['custom']}")

        content = "\n".join(lines) + "\n"
        prep_dir = os.path.join(workspace_dir, "preparation")
        os.makedirs(prep_dir, exist_ok=True)
        path = os.path.join(prep_dir, "requirements.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    @staticmethod
    def summary(state):
        p = state.get("project", {})
        b = state.get("branding", {})
        lines = []
        if p.get("name"):
            lines.append(f"Project: {p['name']}")
        if p.get("type"):
            lines.append(f"Type: {p['type']}")
        if p.get("description"):
            desc = p["description"]
            if len(desc) > 80:
                desc = desc[:77] + "..."
            lines.append(f"Description: {desc}")
        if p.get("target_audience"):
            lines.append(f"Audience: {p['target_audience']}")
        if p.get("key_features"):
            lines.append(f"Features: {', '.join(p['key_features'])}")
        if p.get("pages"):
            lines.append(f"Pages: {', '.join(p['pages'])}")
        if b.get("palette_name"):
            colors = b.get("colors", {})
            if colors.get("primary"):
                lines.append(
                    f"Colors: {b['palette_name']} — "
                    f"{colors['primary']} / {colors['accent']} / {colors['background']}"
                )
            elif colors.get("custom"):
                lines.append(f"Colors: Custom — {colors['custom']}")
        return "\n".join(lines) if lines else "No requirements collected yet."
