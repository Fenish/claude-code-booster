#!/usr/bin/env python3
"""Remove background using AI segmentation + color despill for chroma cleanup."""

import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS = os.path.join(SCRIPT_DIR, "requirements.txt")


def ensure_deps():
    """Auto-install dependencies on first run."""
    try:
        import cv2  # noqa: F401
        import numpy  # noqa: F401
        import rembg  # noqa: F401

        return True
    except ImportError:
        pass

    print("Installing dependencies (first run only)...")
    req_file = REQUIREMENTS if os.path.isfile(REQUIREMENTS) else None
    cmd = [sys.executable, "-m", "pip", "install", "-q"]
    if req_file:
        cmd += ["-r", req_file]
    else:
        cmd += ["rembg[cpu]", "opencv-python-headless", "numpy"]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Failed to install dependencies:\n{result.stderr}", file=sys.stderr)
        return False
    return True


def detect_chroma_color(img_bgr, sample_size=30):
    """Detect dominant background color from corners via HSV bucketing."""
    import cv2
    import numpy as np

    h, w = img_bgr.shape[:2]
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    corners = [
        hsv[0:sample_size, 0:sample_size],
        hsv[0:sample_size, max(0, w - sample_size) : w],
        hsv[max(0, h - sample_size) : h, 0:sample_size],
        hsv[max(0, h - sample_size) : h, max(0, w - sample_size) : w],
    ]

    pixels = np.vstack([c.reshape(-1, 3) for c in corners])
    if len(pixels) == 0:
        return None

    median_h = float(np.median(pixels[:, 0]))
    median_s = float(np.median(pixels[:, 1]))

    if median_s < 40:
        return None

    bgr_corners = []
    for x1, y1, x2, y2 in [
        (0, 0, sample_size, sample_size),
        (max(0, w - sample_size), 0, w, sample_size),
        (0, max(0, h - sample_size), sample_size, h),
        (max(0, w - sample_size), max(0, h - sample_size), w, h),
    ]:
        bgr_corners.append(img_bgr[y1:y2, x1:x2].reshape(-1, 3))

    bgr_all = np.vstack(bgr_corners)
    avg_b = int(np.mean(bgr_all[:, 0]))
    avg_g = int(np.mean(bgr_all[:, 1]))
    avg_r = int(np.mean(bgr_all[:, 2]))

    return (avg_b, avg_g, avg_r)


def despill(img_bgr, alpha, chroma_bgr, strength=0.9):
    """Remove color spill from the chroma key on edge/semi-transparent pixels."""
    import cv2
    import numpy as np

    cb, cg, cr = chroma_bgr
    dominant = max(range(3), key=lambda i: chroma_bgr[i])

    alpha_f = alpha.astype(np.float32) / 255.0
    edge_mask = (alpha_f > 0.01) & (alpha_f < 0.95)

    dist_from_edge = cv2.distanceTransform(
        (alpha > 200).astype(np.uint8), cv2.DIST_L2, 5
    )
    near_edge = dist_from_edge < 6
    spill_mask = edge_mask | (near_edge & (alpha_f > 0))

    img_f = img_bgr.astype(np.float32)
    channels = [img_f[:, :, 0], img_f[:, :, 1], img_f[:, :, 2]]

    dom_ch = channels[dominant]
    other_chs = [channels[i] for i in range(3) if i != dominant]
    avg_other = (other_chs[0] + other_chs[1]) / 2.0

    spill_amount = np.clip(dom_ch - avg_other, 0, None) * strength
    channels[dominant] = np.where(spill_mask, dom_ch - spill_amount, dom_ch)
    channels[dominant] = np.clip(channels[dominant], 0, 255)

    img_f[:, :, 0] = channels[0]
    img_f[:, :, 1] = channels[1]
    img_f[:, :, 2] = channels[2]

    return np.clip(img_f, 0, 255).astype(np.uint8)


def remove_background(input_path, output_path):
    import cv2
    import numpy as np
    from PIL import Image
    from rembg import remove

    img_pil = Image.open(input_path)
    result_pil = remove(img_pil)

    result_np = np.array(result_pil)
    ai_alpha = result_np[:, :, 3]

    img_bgr = cv2.imread(input_path, cv2.IMREAD_COLOR)
    chroma = detect_chroma_color(img_bgr)

    if chroma is not None:
        cb, cg, cr = chroma
        print(f"Detected chroma color: RGB({cr}, {cg}, {cb})")

        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        median_h = (
            float(np.median(hsv[ai_alpha == 0, 0])) if np.any(ai_alpha == 0) else 60
        )
        h_range = 20
        lower = np.array([max(0, median_h - h_range), 80, 40], dtype=np.uint8)
        upper = np.array([min(179, median_h + h_range), 255, 255], dtype=np.uint8)
        color_mask = cv2.inRange(hsv, lower, upper)

        combined_bg = (ai_alpha == 0) | (color_mask > 0)
        alpha = np.where(combined_bg, 0, ai_alpha).astype(np.uint8)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        alpha = cv2.morphologyEx(alpha, cv2.MORPH_OPEN, kernel)

        alpha_f = alpha.astype(np.float32)
        alpha = cv2.GaussianBlur(alpha_f, (3, 3), 0.8).astype(np.uint8)

        img_despilled = despill(img_bgr, alpha, chroma)
    else:
        print("No chroma color detected, skipping despill")
        alpha = ai_alpha
        img_despilled = img_bgr

    img_rgb = cv2.cvtColor(img_despilled, cv2.COLOR_BGR2RGB)
    rgba = np.dstack([img_rgb, alpha])

    transparent = alpha == 0
    rgba[transparent, 0:3] = 0

    result = Image.fromarray(rgba, "RGBA")
    result.save(output_path, "PNG")

    total = alpha.shape[0] * alpha.shape[1]
    removed = int(np.sum(transparent))
    pct = (removed / total) * 100
    print(f"Background removal: {removed}/{total} pixels ({pct:.1f}%)")

    return removed, total


def remove_chroma(input_path, output_path, threshold=None):
    return remove_background(input_path, output_path)


if __name__ == "__main__":
    import argparse

    if not ensure_deps():
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="Remove background using AI segmentation + despill"
    )
    parser.add_argument("input", help="Input image path")
    parser.add_argument("-o", "--output", help="Output path")
    args = parser.parse_args()

    output = args.output or args.input.replace(".png", "-transparent.png")
    remove_background(args.input, output)
    print(f"Saved: {output}")
