---
name: edit
description: |
  Edit existing images using Codex CLI's imagegen skill.
  Trigger when the user asks to: edit image, modify image, change image,
  update image, alter image, transform image, replace background,
  remove background, recolor, resize image, crop image, add text to image.
allowed-tools: Bash, Read
version: 1.2.0
---

# Image Editing

Edit existing images using Codex CLI's built-in imagegen skill.

## Usage

Always run the edit script as a background job so it doesn't block the
conversation:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/image_gen.py" edit <input-path> "<enhanced prompt>"
```

On Windows, use `python` instead of `python3`.

Use `run_in_background: true` when calling the Bash tool.

## Prompt Enhancement (mandatory)

Before passing the prompt to codex, you MUST enhance it using the structured
approach below. Never pass the user's raw edit instructions directly.

### Specificity policy

- If the user's instructions are already specific and detailed, normalize into a
  clean spec without adding creative requirements.
- If the instructions are generic, add tasteful augmentation that materially
  improves output quality.

### Edit prompt structure

For edits, always explicitly state what to change AND what to preserve:

```
Use case: <edit taxonomy slug>
Primary request: <user's edit instruction, clarified>
Constraints: change only <X>; keep <Y> unchanged
Avoid: <things to not do>
```

### Edit taxonomy

Classify each edit into one of these:

- text-localization: translate/replace in-image text, preserve layout
- identity-preserve: try-on, person-in-scene; lock face/body/pose
- precise-object-edit: remove/replace a specific element
- lighting-weather: time-of-day/season/atmosphere changes only
- background-extraction: transparent background / clean cutout
- style-transfer: apply reference style while changing subject/scene
- compositing: multi-image insert/merge with matched lighting/perspective
- sketch-to-render: drawing/line art to photoreal render

### Best practices

- State invariants explicitly: "change only X; keep Y unchanged"
- Repeat invariants on every iteration to reduce drift
- Preserve camera angle, lighting, and surrounding objects unless told otherwise
- For text changes, require verbatim rendering and specify typography
- Always add: no watermark (unless requested)
- Match lighting and shadows when replacing elements

### Example enhancement

User says: "replace the background with white"

Enhanced prompt:

```
Use case: precise-object-edit
Primary request: replace only the background with a clean plain white backdrop
Constraints: change only the background; keep the subject, its edges, lighting, and shadows unchanged; no text; no watermark
Avoid: altering the subject in any way; adding new elements; changing the subject's color or lighting
```

## Workflow

1. Confirm the input image path exists
2. Take the user's edit instructions
3. **Enhance the prompt** using the schema and guidelines above
4. If the user specifies an output path, include it in the prompt
5. Run the edit command as a **background job** (`run_in_background: true`)
6. Tell the user that image editing has been kicked off in the background
7. When the background job completes, check the output for `SAVED: <path>` lines
8. Report the saved path to the user
9. If the user wants to see the result, use the Read tool on the saved path

## Important

Codex image editing takes time (30-120 seconds). Always spawn it in the
background so the user can continue working. You will be notified when it
finishes.

## Transparent background requests

For transparent/background removal, include "transparent background" in the
enhanced prompt. The plugin automatically:

1. Tells codex to generate on a chroma-key background
2. After generation, auto-detects the chroma color and removes it
3. Saves the final image with a transparent alpha channel

No manual steps needed — just mention "transparent" in the prompt.

## Prerequisites

Requires Codex CLI installed and authenticated. Run status to check:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/image_gen.py" status
```

If codex is not found, tell the user to install it with
`npm install -g @openai/codex` and run `codex login`.
