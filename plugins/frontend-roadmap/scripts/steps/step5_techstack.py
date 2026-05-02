"""Step 5: Choose the tech stack for the final build."""

import os


class Step5TechStack:
    number = 5
    name = "Tech Stack"
    description = "Choose framework, styling, and UI library for the build."

    @staticmethod
    def questions():
        return [
            {
                "key": "tech_stack.framework",
                "question": "Which framework + styling combo?",
                "header": "Framework",
                "options": [
                    {
                        "label": "Next.js + Tailwind",
                        "description": "React meta-framework with SSR/SSG and Tailwind CSS",
                    },
                    {
                        "label": "React + Vite + Tailwind",
                        "description": "Fast React SPA with Vite bundler and Tailwind CSS",
                    },
                    {
                        "label": "Vue + Nuxt + Tailwind",
                        "description": "Vue meta-framework with SSR/SSG and Tailwind CSS",
                    },
                    {
                        "label": "Astro + Tailwind",
                        "description": "Content-focused static site builder with Tailwind CSS",
                    },
                ],
            },
            {
                "key": "tech_stack.ui_library",
                "question": "Which UI component library?",
                "header": "UI Library",
                "options": [
                    {
                        "label": "shadcn/ui",
                        "description": "Copy-paste Radix-based components — full control, great DX",
                    },
                    {
                        "label": "Radix UI",
                        "description": "Unstyled accessible primitives — style from scratch",
                    },
                    {
                        "label": "Headless UI",
                        "description": "Tailwind Labs' unstyled components for React/Vue",
                    },
                    {
                        "label": "None",
                        "description": "Build all components from scratch",
                    },
                ],
            },
        ]

    @staticmethod
    def apply(state, answers):
        for key, value in answers.items():
            parts = key.split(".")
            obj = state
            for p in parts[:-1]:
                obj = obj[p]
            obj[parts[-1]] = value
        state["completed_steps"].append(5)
        state["current_step"] = 6
        return state

    @staticmethod
    def save_tech_stack(state, workspace_dir):
        ts = state.get("tech_stack", {})
        framework = ts.get("framework", "Not selected")
        ui_lib = ts.get("ui_library", "None")

        lines = [
            "# Tech Stack Decisions",
            f"\n| Choice     | Selection |",
            f"|------------|-----------|",
            f"| Framework  | {framework} |",
            f"| Styling    | {ts.get('styling', 'Tailwind CSS')} |",
            f"| UI Library | {ui_lib} |",
        ]

        framework_name = (
            framework.split("+")[0].strip() if "+" in framework else framework
        )

        lines.append("\n## Rationale")
        if "Next" in framework_name:
            lines.append(
                "- Next.js provides SSR/SSG, file-based routing, and Image optimization out of the box"
            )
        elif "Vite" in framework:
            lines.append(
                "- Vite offers fast HMR and lean builds for single-page applications"
            )
        elif "Nuxt" in framework:
            lines.append(
                "- Nuxt provides auto-imports, file-based routing, and SSR for Vue"
            )
        elif "Astro" in framework_name:
            lines.append(
                "- Astro ships zero JS by default — ideal for content-heavy sites"
            )

        if ui_lib == "shadcn/ui":
            lines.append(
                "- shadcn/ui gives full ownership of components with Radix primitives underneath"
            )
        elif ui_lib == "Radix UI":
            lines.append(
                "- Radix UI provides accessible unstyled primitives for maximum styling control"
            )
        elif ui_lib == "Headless UI":
            lines.append(
                "- Headless UI integrates well with Tailwind for accessible components"
            )

        content = "\n".join(lines) + "\n"
        prep_dir = os.path.join(workspace_dir, "preparation")
        os.makedirs(prep_dir, exist_ok=True)
        path = os.path.join(prep_dir, "tech-stack.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    @staticmethod
    def summary(state):
        ts = state.get("tech_stack", {})
        parts = []
        if ts.get("framework"):
            parts.append(f"Framework: {ts['framework']}")
        if ts.get("ui_library"):
            parts.append(f"UI Library: {ts['ui_library']}")
        return "\n".join(parts) if parts else "No tech stack selected yet."
