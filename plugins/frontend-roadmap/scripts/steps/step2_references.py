"""Step 2: Collect visual references and inspiration."""

import os
import urllib.parse

BASE_SEARCH_URLS = {
    "SaaS": {
        "dribbble": ["saas dashboard", "saas landing page", "saas website ui"],
        "awwwards": "saas",
        "extra": [
            ("Mobbin — Web App Patterns", "https://mobbin.com/browse/web/apps"),
            ("Godly — Curated Design Inspiration", "https://godly.website"),
        ],
    },
    "Portfolio": {
        "dribbble": ["portfolio website", "creative portfolio", "developer portfolio"],
        "awwwards": "portfolio",
        "extra": [
            (
                "Bestfolios — Portfolio Inspiration",
                "https://www.bestfolios.com/portfolios",
            ),
            ("Godly — Curated Design Inspiration", "https://godly.website"),
        ],
    },
    "Web App": {
        "dribbble": ["web application ui", "dashboard design", "web app interface"],
        "awwwards": "web-interactive",
        "extra": [
            ("Mobbin — Web App Patterns", "https://mobbin.com/browse/web/apps"),
            ("Godly — Curated Design Inspiration", "https://godly.website"),
        ],
    },
    "E-commerce": {
        "dribbble": ["ecommerce website", "online store design", "product page ui"],
        "awwwards": "e-commerce",
        "extra": [
            ("Mobbin — E-commerce Patterns", "https://mobbin.com/browse/web/apps"),
            ("Godly — Curated Design Inspiration", "https://godly.website"),
        ],
    },
    "Landing Page": {
        "dribbble": ["landing page design", "hero section", "marketing page"],
        "awwwards": "landing-page",
        "extra": [
            ("Lapa Ninja — Landing Page Inspiration", "https://www.lapa.ninja"),
            ("Godly — Curated Design Inspiration", "https://godly.website"),
        ],
    },
}


def build_search_urls(project_type, project_name="", project_description=""):
    config = BASE_SEARCH_URLS.get(project_type, BASE_SEARCH_URLS["Web App"])
    urls = []

    for query in config["dribbble"]:
        encoded = urllib.parse.quote(query)
        urls.append(
            {
                "label": f"Dribbble — {query}",
                "url": f"https://dribbble.com/search/{encoded}",
            }
        )

    if project_name:
        custom_query = f"{project_type.lower()} {project_name.lower()}"
        encoded = urllib.parse.quote(custom_query)
        urls.append(
            {
                "label": f"Dribbble — {custom_query}",
                "url": f"https://dribbble.com/search/{encoded}",
            }
        )

    awwwards_cat = config["awwwards"]
    urls.append(
        {
            "label": f"Awwwards — {awwwards_cat} websites",
            "url": f"https://www.awwwards.com/websites/{awwwards_cat}/",
        }
    )

    for label, url in config["extra"]:
        urls.append({"label": label, "url": url})

    return urls


class Step2References:
    number = 2
    name = "Collect References"
    description = "Browse design inspiration sites and save reference screenshots."

    @staticmethod
    def get_search_urls(project_type, project_name="", project_description=""):
        return build_search_urls(project_type, project_name, project_description)

    @staticmethod
    def questions():
        return [
            {
                "key": "_references_done",
                "question": "Have you saved reference images/screenshots into the references/ folder?",
                "header": "References",
                "options": [
                    {
                        "label": "Yes, done",
                        "description": "I've collected all the references I need",
                    },
                    {
                        "label": "Skip",
                        "description": "Skip reference collection for now",
                    },
                ],
            },
        ]

    @staticmethod
    def apply(state, answers):
        state["references_collected"] = answers.get("_references_done") == "Yes, done"
        state["completed_steps"].append(2)
        state["current_step"] = 3
        return state

    @staticmethod
    def count_references(workspace_dir):
        ref_dir = os.path.join(workspace_dir, "references")
        if not os.path.isdir(ref_dir):
            return 0
        exts = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".pdf"}
        count = 0
        for f in os.listdir(ref_dir):
            if os.path.splitext(f)[1].lower() in exts:
                count += 1
        return count

    @staticmethod
    def summary(state):
        if state.get("references_collected"):
            return "References collected."
        return "References skipped or not yet collected."
