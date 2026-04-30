#!/usr/bin/env python3
"""Wraps Codex CLI's imagegen skill for image generation and editing."""

import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from remove_chroma import remove_chroma

_SHELL = sys.platform == "win32"
CODEX_HOME = os.environ.get(
    "CODEX_HOME", os.path.join(os.path.expanduser("~"), ".codex")
)
CODEX_IMAGES_DIR = os.path.join(CODEX_HOME, "generated_images")
IMAGEGEN_SKILL = os.path.join(CODEX_HOME, "skills", ".system", "imagegen", "SKILL.md")


def load_skill_instructions():
    """Load imagegen SKILL.md as context for codex."""
    if not os.path.isfile(IMAGEGEN_SKILL):
        return ""
    with open(IMAGEGEN_SKILL, encoding="utf-8") as f:
        return f.read()


def find_codex():
    found = shutil.which("codex")
    if found:
        return found
    try:
        result = subprocess.run(
            ["codex", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=_SHELL,
        )
        if result.returncode == 0:
            return "codex"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def check_login():
    try:
        result = subprocess.run(
            ["codex", "login", "status"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=_SHELL,
        )
        text = (result.stdout or result.stderr).strip()
        ok = result.returncode == 0 and bool(re.search(r"logged in", text, re.I))
        return ok, text
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)


def run_codex_and_collect(args, cwd, stdin_text, output_path, transparent=False):
    """Run codex, then copy the generated image to output_path."""
    codex_img_pattern = os.path.join(CODEX_IMAGES_DIR, "**", "*.png")
    output_dir = os.path.join(cwd, "generated-images")
    os.makedirs(output_dir, exist_ok=True)
    cwd_pattern = os.path.join(output_dir, "**", "*.png")

    before_codex = set(glob.glob(codex_img_pattern, recursive=True))
    before_cwd = set(glob.glob(cwd_pattern, recursive=True))

    proc = subprocess.run(
        args,
        cwd=cwd,
        shell=_SHELL,
        input=stdin_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    output = proc.stdout or ""
    print(output, end="")

    if proc.returncode != 0:
        return proc.returncode

    after_cwd = set(glob.glob(cwd_pattern, recursive=True))
    new_cwd = after_cwd - before_cwd

    after_codex = set(glob.glob(codex_img_pattern, recursive=True))
    new_codex = after_codex - before_codex

    source = None
    if new_cwd:
        source = max(new_cwd, key=os.path.getmtime)
    elif new_codex:
        source = max(new_codex, key=os.path.getmtime)

    if not source:
        print(
            "Warning: codex finished but no new image found",
            file=sys.stderr,
        )
        return 0

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    shutil.copy2(source, output_path)
    abs_path = os.path.abspath(output_path)

    if transparent:
        try:
            removed, total = remove_chroma(abs_path, abs_path)
            pct = (removed / total) * 100 if total else 0
            if pct < 5:
                print(
                    "Warning: less than 5% chroma pixels found — image may not have a green background",
                    file=sys.stderr,
                )
        except Exception as exc:
            print(f"Warning: chroma removal failed: {exc}", file=sys.stderr)

    print(f"SAVED: {abs_path}")
    return 0


def timestamp():
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace(":", "")
        .replace("-", "")
    )


def build_instruction(mode, prompt):
    """Build the full instruction with skill context."""
    skill = load_skill_instructions()

    parts = []
    if skill:
        parts.append(
            "Follow these imagegen skill instructions. "
            "Do NOT read any skill files from disk — the instructions are provided below.\n\n"
            f"--- IMAGEGEN SKILL ---\n{skill}\n--- END SKILL ---\n"
        )

    if mode == "generate":
        parts.append("Generate an image using the built-in image_gen tool.\n\n")
        parts.append(f"Image request:\n{prompt}")
    elif mode == "edit":
        parts.append(
            "Edit the attached image using the built-in image_gen tool. "
            "Preserve unrelated parts unless told otherwise.\n\n"
        )
        parts.append(f"Edit request:\n{prompt}")

    return "".join(parts)


def cmd_status(_args):
    codex = find_codex()
    if not codex:
        print("FAIL: codex CLI not found on PATH")
        print("Install with: npm install -g @openai/codex")
        return 1

    version = subprocess.run(
        ["codex", "--version"], capture_output=True, text=True, shell=_SHELL
    )
    print(f"OK: codex {version.stdout.strip()}")

    ok, detail = check_login()
    print(f"{'OK' if ok else 'FAIL'}: login — {detail}")

    skill_ok = os.path.isfile(IMAGEGEN_SKILL)
    print(f"{'OK' if skill_ok else 'FAIL'}: imagegen skill — {IMAGEGEN_SKILL}")

    if not ok:
        print("\nRun `codex login` to authenticate.")
        return 1
    if not skill_ok:
        print("\nImagegen skill not found. Reinstall or update Codex CLI.")
        return 1

    print("\nReady to generate images.")
    return 0


def cmd_generate(args):
    prompt = " ".join(args.prompt).strip()
    if not prompt:
        print("Usage: image_gen.py generate <prompt>", file=sys.stderr)
        return 1

    if not find_codex():
        print(
            "Error: codex CLI not found. Install with: npm install -g @openai/codex",
            file=sys.stderr,
        )
        return 1

    cwd = os.getcwd()
    output_path = os.path.join(cwd, "generated-images", f"{timestamp()}.png")

    save_match = re.search(r"[Ss]ave (?:as|to) (\S+)", prompt)
    if save_match:
        output_path = os.path.join(cwd, save_match.group(1))

    transparent = bool(re.search(r"transparent", prompt, re.I))
    instruction = build_instruction("generate", prompt)
    codex_args = [
        "codex",
        "exec",
        "--sandbox",
        "workspace-write",
        "--skip-git-repo-check",
        "-C",
        cwd,
    ]
    return run_codex_and_collect(codex_args, cwd, instruction, output_path, transparent)


def cmd_edit(args):
    input_path = os.path.abspath(args.input)
    if not os.path.isfile(input_path):
        print(f"Error: input image not found: {input_path}", file=sys.stderr)
        return 1

    prompt = " ".join(args.prompt).strip()
    if not prompt:
        print("Usage: image_gen.py edit <input-path> <prompt>", file=sys.stderr)
        return 1

    if not find_codex():
        print(
            "Error: codex CLI not found. Install with: npm install -g @openai/codex",
            file=sys.stderr,
        )
        return 1

    cwd = os.getcwd()
    output_path = os.path.join(cwd, "generated-images", f"{timestamp()}-edit.png")

    save_match = re.search(r"[Ss]ave (?:as|to) (\S+)", prompt)
    if save_match:
        output_path = os.path.join(cwd, save_match.group(1))

    transparent = bool(re.search(r"transparent", prompt, re.I))
    instruction = build_instruction("edit", prompt)
    codex_args = [
        "codex",
        "exec",
        "--sandbox",
        "workspace-write",
        "--skip-git-repo-check",
        "--image",
        input_path,
        "-C",
        cwd,
    ]
    return run_codex_and_collect(codex_args, cwd, instruction, output_path, transparent)


def main():
    parser = argparse.ArgumentParser(description="Image generation via Codex CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Check codex CLI availability and login")

    gen = sub.add_parser("generate", help="Generate an image from a prompt")
    gen.add_argument("prompt", nargs="+", help="Natural-language image description")

    edit = sub.add_parser("edit", help="Edit an existing image")
    edit.add_argument("input", help="Path to the input image")
    edit.add_argument("prompt", nargs="+", help="Edit instructions")

    args = parser.parse_args()

    if args.command == "status":
        sys.exit(cmd_status(args))
    elif args.command == "generate":
        sys.exit(cmd_generate(args))
    elif args.command == "edit":
        sys.exit(cmd_edit(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
