"""Step 3: Choose design platform and generate a prompt for it."""

import os

PLATFORM_INSTRUCTIONS = {
    "Google Stitch": (
        "In Google Stitch:\n"
        "1. Upload your reference images from the references/ folder\n"
        "2. Paste the prompt from preparation/platform-prompt.md\n"
        "3. Generate the design\n"
        "4. Export as HTML/CSS and download the full project\n"
        "5. Place all exported files into the exports/ folder"
    ),
    "v0.dev": (
        "In v0.dev:\n"
        "1. Upload your reference images from the references/ folder\n"
        "2. Paste the prompt from preparation/platform-prompt.md\n"
        "3. Generate the design\n"
        "4. Copy each generated component\n"
        "5. Save each component as a separate file in the exports/ folder"
    ),
    "Bolt.new": (
        "In Bolt.new:\n"
        "1. Upload your reference images from the references/ folder\n"
        "2. Paste the prompt from preparation/platform-prompt.md\n"
        "3. Generate the project\n"
        "4. Export or download the generated project\n"
        "5. Place all files into the exports/ folder"
    ),
    "Lovable": (
        "In Lovable:\n"
        "1. Upload your reference images from the references/ folder\n"
        "2. Paste the prompt from preparation/platform-prompt.md\n"
        "3. Generate the design\n"
        "4. Export the generated code\n"
        "5. Place all files into the exports/ folder"
    ),
}


def _build_base_context(state):
    p = state.get("project", {})
    pages = ", ".join(p.get("pages", [])) or "Home"
    features = ", ".join(p.get("key_features", [])) or "core functionality"

    context = (
        f"Project: {p.get('name', 'Untitled')}\n"
        f"Type: {p.get('type', 'web')} website\n"
        f"Description: {p.get('description', p.get('name', 'my project'))}\n"
        f"Target audience: {p.get('target_audience', 'general users')}\n"
        f"Pages: {pages}\n"
        f"Features: {features}\n"
    )

    b = state.get("branding", {})
    colors = b.get("colors", {})
    if colors.get("primary"):
        context += (
            f"\nColor palette ({b.get('palette_name', 'Custom')}):\n"
            f"- Primary: {colors['primary']}\n"
            f"- Secondary: {colors.get('secondary', '-')}\n"
            f"- Accent: {colors.get('accent', '-')}\n"
            f"- Background: {colors.get('background', '-')}\n"
            f"- Foreground: {colors.get('foreground', '-')}\n"
        )
    elif colors.get("custom"):
        context += f"\nColors: {colors['custom']}\n"

    return context


def _ref_block(state):
    if not state.get("references_collected"):
        return ""
    return (
        "I've uploaded reference images showing the visual direction I want. "
        "Before generating anything, carefully analyze each reference image for:\n"
        "- Layout structure and grid patterns\n"
        "- Typography choices (font sizes, weights, hierarchy)\n"
        "- Spacing and whitespace patterns\n"
        "- Color usage and contrast ratios\n"
        "- Component patterns (cards, navbars, CTAs, hero sections)\n"
        "- Visual style (minimal, bold, playful, corporate, etc.)\n\n"
        "Use these patterns as the design foundation. "
        "The final result should feel like it belongs in the same design system as the references.\n\n"
    )


def generate_stitch_prompt(state):
    ctx = _build_base_context(state)
    ref = _ref_block(state)
    return (
        f"{ref}"
        f"Create a complete, production-ready website design.\n\n"
        f"--- PROJECT ---\n{ctx}\n"
        f"--- DESIGN REQUIREMENTS ---\n"
        f"- Modern, clean, professional layout\n"
        f"- Responsive design (mobile-first)\n"
        f"- Clear visual hierarchy with consistent spacing\n"
        f"- Smooth hover states and micro-interactions\n"
        f"- Accessible contrast ratios (WCAG 2.1 AA)\n"
        f"- Consistent component styling across all pages\n\n"
        f"--- OUTPUT ---\n"
        f"Generate all pages listed above as complete, styled HTML with inline or scoped CSS. "
        f"Each page should be fully designed — no placeholder boxes or wireframe-style output. "
        f"Include realistic content structure (headings, paragraphs, buttons, navigation)."
    )


def generate_v0_prompt(state):
    ctx = _build_base_context(state)
    ref = _ref_block(state)
    return (
        f"{ref}"
        f"Build a complete website with the following specs.\n\n"
        f"--- PROJECT ---\n{ctx}\n"
        f"--- REQUIREMENTS ---\n"
        f"- Use React with Tailwind CSS\n"
        f"- Responsive (mobile-first)\n"
        f"- Clean, modern design with smooth animations\n"
        f"- Accessible (WCAG 2.1 AA)\n"
        f"- Consistent typography and spacing scale\n"
        f"- Dark/light mode support\n\n"
        f"Generate each page as a separate component. "
        f"Include a shared layout with navigation and footer. "
        f"Use realistic content — no lorem ipsum."
    )


def generate_bolt_prompt(state):
    ctx = _build_base_context(state)
    ref = _ref_block(state)
    return (
        f"{ref}"
        f"Build a complete full-stack website.\n\n"
        f"--- PROJECT ---\n{ctx}\n"
        f"--- REQUIREMENTS ---\n"
        f"- Modern React/Next.js with Tailwind CSS\n"
        f"- Responsive (mobile-first)\n"
        f"- Professional design with animations and transitions\n"
        f"- Accessible (WCAG 2.1 AA)\n"
        f"- Proper routing between all pages\n"
        f"- Shared layout with navigation and footer\n"
        f"- Dark/light mode toggle\n\n"
        f"Build all pages with realistic content and proper component structure. "
        f"Focus on visual polish — this is a design reference, not a prototype."
    )


def generate_lovable_prompt(state):
    ctx = _build_base_context(state)
    ref = _ref_block(state)
    return (
        f"{ref}"
        f"Design and build a beautiful website.\n\n"
        f"--- PROJECT ---\n{ctx}\n"
        f"--- DESIGN DIRECTION ---\n"
        f"- Prioritize visual design quality over functionality\n"
        f"- Modern, polished, production-ready look\n"
        f"- Responsive layout (mobile-first)\n"
        f"- Smooth animations and micro-interactions\n"
        f"- Consistent design tokens (colors, spacing, typography)\n"
        f"- Accessible contrast and focus states\n\n"
        f"Create all pages with full visual design — hero sections, feature grids, "
        f"pricing tables, testimonials, CTAs. Use realistic copy, not placeholders."
    )


PLATFORM_PROMPT_GENERATORS = {
    "Google Stitch": generate_stitch_prompt,
    "v0.dev": generate_v0_prompt,
    "Bolt.new": generate_bolt_prompt,
    "Lovable": generate_lovable_prompt,
}


class Step3Platform:
    number = 3
    name = "Design Platform"
    description = "Choose a design platform and get a tailored prompt."

    @staticmethod
    def questions():
        return [
            {
                "key": "platform",
                "question": "Which design platform will you use to generate the initial design?",
                "header": "Platform",
                "options": [
                    {
                        "label": "Google Stitch (Recommended)",
                        "description": "Google's AI design-to-code tool — supports image uploads and generates full HTML/CSS",
                    },
                    {
                        "label": "v0.dev",
                        "description": "Vercel's AI UI generator — great for React/Next.js components",
                    },
                    {
                        "label": "Bolt.new",
                        "description": "Full-stack AI app generator with live preview",
                    },
                    {
                        "label": "Lovable",
                        "description": "AI web app builder with design-first approach",
                    },
                ],
            },
        ]

    @staticmethod
    def generate_prompt(state):
        platform = state.get("platform", "Google Stitch")
        clean_platform = platform.replace(" (Recommended)", "")
        generator = PLATFORM_PROMPT_GENERATORS.get(
            clean_platform, generate_stitch_prompt
        )
        return generator(state)

    @staticmethod
    def apply(state, answers):
        platform = answers.get("platform", "Google Stitch")
        state["platform"] = platform.replace(" (Recommended)", "")
        state["completed_steps"].append(3)
        state["current_step"] = 4
        return state

    @staticmethod
    def save_prompt(state, workspace_dir):
        prompt = Step3Platform.generate_prompt(state)
        platform = state.get("platform", "Google Stitch")
        instructions = PLATFORM_INSTRUCTIONS.get(platform, "")

        content = (
            f"# Design Platform Prompt\n\n"
            f"**Platform:** {platform}\n\n"
            f"## Prompt\n\n"
            f"Copy and paste this into {platform}:\n\n"
            f"```\n{prompt}\n```\n\n"
            f"## Instructions\n\n{instructions}\n"
        )

        prep_dir = os.path.join(workspace_dir, "preparation")
        os.makedirs(prep_dir, exist_ok=True)
        path = os.path.join(prep_dir, "platform-prompt.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    @staticmethod
    def summary(state):
        platform = state.get("platform")
        if platform:
            return f"Platform: {platform}"
        return "No platform selected yet."
