"""
generate_dataset.py
────────────────────
Crops each hieroglyph from the chart image, then applies heavy data
augmentation to produce IMAGES_PER_GLYPH training images per symbol.

Run:
    python scripts/generate_dataset.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import random
import shutil
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import cv2

from config import (
    CHART_IMAGE, TRAIN_DIR, VAL_DIR, GLYPH_BOXES, GLYPHS,
    IMAGES_PER_GLYPH, VAL_SPLIT, IMAGE_SIZE
)

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


# ── Augmentation helpers ─────────────────────────────────────────────────────

def random_rotation(img, max_deg=25):
    angle = random.uniform(-max_deg, max_deg)
    return img.rotate(angle, resample=Image.BICUBIC, expand=False, fillcolor=255)

def random_scale(img, lo=0.75, hi=1.25):
    w, h = img.size
    scale = random.uniform(lo, hi)
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    img = img.resize((nw, nh), Image.BICUBIC)
    # pad or crop back to original size
    canvas = Image.new("L", (w, h), 255)
    ox = (w - nw) // 2
    oy = (h - nh) // 2
    canvas.paste(img, (ox, oy))
    return canvas

def random_translate(img, max_frac=0.15):
    w, h = img.size
    dx = int(random.uniform(-max_frac, max_frac) * w)
    dy = int(random.uniform(-max_frac, max_frac) * h)
    return img.transform(img.size, Image.AFFINE, (1, 0, -dx, 0, 1, -dy), fillcolor=255)

def random_perspective(img):
    w, h = img.size
    arr = np.array(img, dtype=np.float32)
    d = 0.12
    src = np.float32([[0,0],[w,0],[0,h],[w,h]])
    def p(): return random.uniform(-d, d)
    dst = np.float32([
        [w*p(), h*p()],
        [w*(1+p()), h*p()],
        [w*p(), h*(1+p())],
        [w*(1+p()), h*(1+p())]
    ])
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(arr, M, (w, h), borderValue=255)
    return Image.fromarray(warped.astype(np.uint8))

def random_brightness(img):
    factor = random.uniform(0.6, 1.4)
    return ImageEnhance.Brightness(img).enhance(factor)

def random_contrast(img):
    factor = random.uniform(0.6, 1.5)
    return ImageEnhance.Contrast(img).enhance(factor)

def random_blur(img):
    if random.random() < 0.4:
        radius = random.uniform(0.5, 2.0)
        img = img.filter(ImageFilter.GaussianBlur(radius))
    return img

def random_noise(img):
    if random.random() < 0.5:
        arr = np.array(img, dtype=np.int16)
        noise = np.random.normal(0, random.uniform(5, 20), arr.shape).astype(np.int16)
        arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(arr)
    return img

def random_flip(img):
    if random.random() < 0.3:
        img = ImageOps.mirror(img)
    return img

def random_elastic(img):
    """Elastic distortion — simulates hand-drawn variation."""
    if random.random() < 0.5:
        arr = np.array(img, dtype=np.float32)
        h, w = arr.shape
        alpha = random.uniform(8, 20)
        sigma = random.uniform(3, 6)
        dx = cv2.GaussianBlur(
            (np.random.rand(h, w) * 2 - 1).astype(np.float32),
            (0, 0), sigma) * alpha
        dy = cv2.GaussianBlur(
            (np.random.rand(h, w) * 2 - 1).astype(np.float32),
            (0, 0), sigma) * alpha
        x, y = np.meshgrid(np.arange(w), np.arange(h))
        map_x = np.clip(x + dx, 0, w - 1).astype(np.float32)
        map_y = np.clip(y + dy, 0, h - 1).astype(np.float32)
        distorted = cv2.remap(arr, map_x, map_y,
                              interpolation=cv2.INTER_LINEAR,
                              borderValue=255)
        img = Image.fromarray(distorted.astype(np.uint8))
    return img

def random_ink_thickness(img):
    """Randomly erode or dilate to simulate thin/thick ink strokes."""
    arr = np.array(img)
    kernel = np.ones((2, 2), np.uint8)
    if random.random() < 0.4:
        arr = cv2.erode(arr, kernel, iterations=1)   # thicker stroke
    elif random.random() < 0.4:
        arr = cv2.dilate(arr, kernel, iterations=1)  # thinner stroke
    return Image.fromarray(arr)

def augment(img):
    """Apply a random chain of augmentations."""
    img = random_rotation(img)
    img = random_scale(img)
    img = random_translate(img)
    if random.random() < 0.6:
        img = random_perspective(img)
    img = random_brightness(img)
    img = random_contrast(img)
    img = random_blur(img)
    img = random_noise(img)
    img = random_flip(img)
    if random.random() < 0.5:
        img = random_elastic(img)
    img = random_ink_thickness(img)
    return img


# ── Main generation logic ────────────────────────────────────────────────────

def crop_glyph(chart: Image.Image, label: str) -> Image.Image:
    box = GLYPH_BOXES.get(label)
    if box is None:
        raise ValueError(f"No bounding box defined for glyph '{label}'. "
                         f"Run calibrate_boxes.py to set it.")
    crop = chart.crop(box).convert("L")   # grayscale
    # Binarise and invert if background is dark
    arr = np.array(crop)
    if arr.mean() < 128:
        arr = 255 - arr
    crop = Image.fromarray(arr)
    crop = crop.resize((IMAGE_SIZE, IMAGE_SIZE), Image.LANCZOS)
    return crop


def generate():
    if not os.path.exists(CHART_IMAGE):
        print(f"\n[ERROR] Chart image not found at: {CHART_IMAGE}")
        print("Please copy your chart image there and rename it 'chart.png'.")
        print("Then run this script again.\n")
        sys.exit(1)

    # Clean and recreate output dirs
    for d in [TRAIN_DIR, VAL_DIR]:
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d)

    chart = Image.open(CHART_IMAGE)
    print(f"Chart size: {chart.size[0]}x{chart.size[1]} px")
    print(f"Generating {IMAGES_PER_GLYPH} images × {len(GLYPHS)} glyphs "
          f"= {IMAGES_PER_GLYPH * len(GLYPHS):,} total images\n")

    label_list = [g[0] for g in GLYPHS]
    iterator = tqdm(label_list, desc="Glyphs") if HAS_TQDM else label_list

    for label in iterator:
        base_crop = crop_glyph(chart, label)

        n_val   = max(1, int(IMAGES_PER_GLYPH * VAL_SPLIT))
        n_train = IMAGES_PER_GLYPH - n_val

        for split, n in [("train", n_train), ("val", n_val)]:
            out_dir = os.path.join(TRAIN_DIR if split == "train" else VAL_DIR, label)
            os.makedirs(out_dir, exist_ok=True)

            inner = tqdm(range(n), desc=f"  {label}/{split}", leave=False) \
                    if HAS_TQDM else range(n)
            for i in inner:
                aug = augment(base_crop.copy())
                aug.save(os.path.join(out_dir, f"{label}_{split}_{i:04d}.png"))

        if not HAS_TQDM:
            print(f"  ✓ {label}  ({IMAGES_PER_GLYPH} images)")

    total = IMAGES_PER_GLYPH * len(GLYPHS)
    print(f"\nDone! {total:,} images saved to: {DATASET_DIR}")
    print(f"  Train: {int(total * (1 - VAL_SPLIT)):,} images")
    print(f"  Val:   {int(total * VAL_SPLIT):,} images")
    print("\nNext step: python scripts/train.py")


if __name__ == "__main__":
    generate()
