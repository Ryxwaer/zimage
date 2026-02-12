"""
Image Generator: handles image generation requests using the loaded pipeline.
Saves images with UUID filenames and JSON metadata sidecars.
"""

import json
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

import torch
from termcolor import colored

from config import SETTINGS
from services.model_manager import MODEL_MANAGER


def generate_image(
    prompt: str,
    width: int = 0,
    height: int = 0,
    steps: int = 0,
    seed: int = -1,
) -> dict:
    """
    Generate an image from a text prompt.

    Args:
        prompt: Text description of the image to generate.
        width: Image width in pixels (0 = use default).
        height: Image height in pixels (0 = use default).
        steps: Number of inference steps (0 = use default).
        seed: Random seed (-1 = random).

    Returns:
        Dictionary with image filename, URL, metadata, and generation time.
    """
    # Apply defaults
    WIDTH = width if width > 0 else SETTINGS.DEFAULT_WIDTH
    HEIGHT = height if height > 0 else SETTINGS.DEFAULT_HEIGHT
    STEPS = steps if steps > 0 else SETTINGS.DEFAULT_STEPS
    SEED = seed if seed >= 0 else int.from_bytes(os.urandom(4), "big") % (2**31)

    print(colored(
        f"[Generator] Generating: {WIDTH}x{HEIGHT}, {STEPS} steps, seed={SEED}",
        "yellow",
    ))
    print(colored(f"[Generator] Prompt: {prompt[:100]}...", "yellow"))

    START_TIME = time.time()

    PIPELINE = MODEL_MANAGER.pipeline
    GENERATOR = torch.Generator("cpu").manual_seed(SEED)

    # Run inference
    RESULT = PIPELINE(
        prompt=prompt,
        height=HEIGHT,
        width=WIDTH,
        num_inference_steps=STEPS,
        guidance_scale=SETTINGS.DEFAULT_GUIDANCE_SCALE,
        generator=GENERATOR,
    )

    IMAGE = RESULT.images[0]
    ELAPSED = round(time.time() - START_TIME, 2)

    # Save image
    IMAGE_ID = str(uuid.uuid4())[:12]
    TIMESTAMP = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    FILENAME = f"{TIMESTAMP}_{IMAGE_ID}.png"
    FILEPATH = os.path.join(SETTINGS.OUTPUT_DIR, FILENAME)

    os.makedirs(SETTINGS.OUTPUT_DIR, exist_ok=True)
    IMAGE.save(FILEPATH)

    # Save metadata sidecar
    METADATA = {
        "filename": FILENAME,
        "prompt": prompt,
        "width": WIDTH,
        "height": HEIGHT,
        "steps": STEPS,
        "seed": SEED,
        "guidance_scale": SETTINGS.DEFAULT_GUIDANCE_SCALE,
        "generation_time_seconds": ELAPSED,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": SETTINGS.MODEL_REPO_ID,
    }

    META_PATH = os.path.join(SETTINGS.OUTPUT_DIR, f"{FILENAME}.json")
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(METADATA, f, indent=2, ensure_ascii=False)

    print(colored(
        f"[Generator] Done in {ELAPSED}s -> {FILENAME}",
        "green", attrs=["bold"],
    ))

    return METADATA


def list_images(limit: Optional[int] = None) -> list[dict]:
    """
    List recently generated images, sorted newest first.

    Args:
        limit: Max number of images to return (None = use MAX_HISTORY).

    Returns:
        List of metadata dictionaries.
    """
    LIMIT = limit or SETTINGS.MAX_HISTORY
    OUTPUT_DIR = SETTINGS.OUTPUT_DIR

    if not os.path.isdir(OUTPUT_DIR):
        return []

    # Find all JSON sidecar files
    META_FILES = sorted(
        [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".png.json")],
        reverse=True,
    )[:LIMIT]

    IMAGES = []
    for META_FILE in META_FILES:
        META_PATH = os.path.join(OUTPUT_DIR, META_FILE)
        try:
            with open(META_PATH, "r", encoding="utf-8") as f:
                DATA = json.load(f)
            # Verify image file still exists
            IMG_PATH = os.path.join(OUTPUT_DIR, DATA.get("filename", ""))
            if os.path.isfile(IMG_PATH):
                DATA["url"] = f"/api/images/{DATA['filename']}"
                IMAGES.append(DATA)
        except (json.JSONDecodeError, IOError):
            continue

    return IMAGES
