---
name: generate
description: |
  Generate images from natural-language prompts using Codex CLI.
  Trigger when the user asks to: generate image, create image, make image,
  draw, illustration, render image, picture of, design a logo, create art,
  generate artwork, make a graphic, create a visual.
allowed-tools: Bash, Read
version: 1.2.0
---

# Image Generation

Generate images using Codex CLI's built-in imagegen skill.

## Usage

Always run the generation script as a background job so it doesn't block the
conversation:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/image_gen.py" generate "<enhanced prompt>"
```

On Windows, use `python` instead of `python3`.

Use `run_in_background: true` when calling the Bash tool.

## Prompt Enhancement (mandatory)

Before passing the prompt to codex, you MUST enhance it using the structured
schema below. Never pass the user's raw prompt directly.

### Specificity policy

- If the user's prompt is already specific and detailed, normalize it into a
  clean structured spec without adding creative requirements.
- If the user's prompt is generic, add tasteful augmentation that materially
  improves output quality.

### Allowed augmentations

- Composition or framing hints
- Polish level or intended-use hints
- Practical layout guidance
- Reasonable scene concreteness that supports the stated request

### Not allowed

- Extra characters or objects not implied by the request
- Brand names, slogans, palettes, or narrative beats not implied
- Arbitrary side-specific placement unless the layout supports it

### Prompt structure

Structure the enhanced prompt as: scene/backdrop -> subject -> details ->
constraints. Use this schema, including only the lines that help:

```
Use case: <taxonomy slug>
Asset type: <where the asset will be used>
Primary request: <user's main prompt, clarified>
Scene/backdrop: <environment>
Subject: <main subject>
Style/medium: <photo/illustration/3D/etc>
Composition/framing: <wide/close/top-down; placement>
Lighting/mood: <lighting + mood>
Color palette: <palette notes>
Materials/textures: <surface details>
Text (verbatim): "<exact text>"
Constraints: <must keep/must avoid>
Avoid: <negative constraints>
```

### Use-case taxonomy

Classify each request into one of these:

- photorealistic-natural: candid/editorial scenes with real texture and natural
  lighting
- product-mockup: product/packaging shots, catalog imagery
- ui-mockup: app/web interface mockups and wireframes
- infographic-diagram: diagrams/infographics with structured layout and text
- scientific-educational: classroom explainers, scientific diagrams
- ads-marketing: campaign concepts and ad creatives
- productivity-visual: slides, charts, workflow, data-heavy visuals
- logo-brand: logo/mark exploration, vector-friendly
- illustration-story: comics, children's book art, narrative scenes
- stylized-concept: style-driven concept art, 3D/stylized renders
- historical-scene: period-accurate/world-knowledge scenes

### Best practices

- For photorealism, include "photorealistic" and concrete real-world texture
  (pores, wrinkles, fabric wear, material grain)
- Use camera/composition language for photorealism (lens, lighting, framing)
- Quote exact text and specify typography + placement
- For tricky words, spell them letter-by-letter
- Always add: no watermark, no logos (unless requested)
- Include intended use (ad, UI mock, infographic) to set polish level

### Example enhancement

User says: "create image of quantum computer with plain white background"

Enhanced prompt:

```
Use case: scientific-educational
Primary request: a quantum computer on a plain white background
Scene/backdrop: clean plain white studio background
Subject: a modern quantum computer with visible dilution refrigerator, gold wiring, and cylindrical cryostat housing
Style/medium: photorealistic product-style rendering
Composition/framing: centered, slight three-quarter angle, generous padding
Lighting/mood: clean studio lighting with soft highlights
Materials/textures: polished metal, gold connectors, frosted glass panels, visible qubit chip
Constraints: no text; no logos; no watermark; plain white background only
```

## Workflow

1. Take the user's natural-language image description
2. **Enhance the prompt** using the schema and guidelines above
3. If the user specifies a path or filename, include it (e.g., "save to
   assets/logo.png")
4. If the user specifies dimensions, include them (e.g., "1024x1024")
5. Run the generate command as a **background job** (`run_in_background: true`)
6. Tell the user that image generation has been kicked off in the background
7. When the background job completes, check the output for `SAVED: <path>` lines
8. Report the saved path(s) to the user
9. If the user wants to see the image, use the Read tool on the saved path

## Important

Codex image generation takes time (30-120 seconds). Always spawn it in the
background so the user can continue working. You will be notified when it
finishes.

## Transparent images

For transparent background requests, simply include "transparent background" in
the enhanced prompt. The plugin automatically:

1. Tells codex to generate on a chroma-key green background
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
