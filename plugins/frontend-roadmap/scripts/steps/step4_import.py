"""Step 4: Import exported design files from the chosen platform."""

import os


class Step4Import:
    number = 4
    name = "Import Exports"
    description = "Import the exported design files from your chosen platform into the exports/ folder."

    @staticmethod
    def questions():
        return [
            {
                "key": "_import_done",
                "question": "Have you exported and placed the design files into the exports/ folder?",
                "header": "Import",
                "options": [
                    {
                        "label": "Yes, imported",
                        "description": "Design files are in the exports/ folder",
                    },
                    {
                        "label": "Not yet",
                        "description": "I still need to export from the platform",
                    },
                    {
                        "label": "Skip",
                        "description": "Skip importing — I'll provide exports later",
                    },
                ],
            },
        ]

    @staticmethod
    def apply(state, answers):
        choice = answers.get("_import_done", "Skip")
        state["exports_imported"] = choice == "Yes, imported"
        state["completed_steps"].append(4)
        state["current_step"] = 5
        return state

    @staticmethod
    def count_files(workspace_dir):
        exports_dir = os.path.join(workspace_dir, "exports")
        if not os.path.isdir(exports_dir):
            return 0
        count = 0
        for root, dirs, files in os.walk(exports_dir):
            count += len(files)
        return count

    @staticmethod
    def summary(state):
        if state.get("exports_imported"):
            return "Design exports imported."
        return "Design exports not yet imported."
