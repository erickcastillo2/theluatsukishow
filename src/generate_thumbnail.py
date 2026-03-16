#!/usr/bin/env python3
"""
Thumbnail Generator for The Lua Tsuki Show.
Creates eye-catching thumbnails for TikTok/Reels/YouTube (1080x1920).
"""

import json
import os
import sys
import textwrap

from PIL import Image, ImageDraw, ImageFont

THUMB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "content", "fotos")

# Colors per narrator
STYLES = {
    "Lua": {
        "bg": (45, 27, 105),
        "accent": (245, 175, 25),
        "text": (255, 255, 255),
        "emoji": "🐕",
    },
    "Tsuki": {
        "bg": (27, 67, 50),
        "accent": (149, 213, 178),
        "text": (255, 255, 255),
        "emoji": "🐕",
    },
}


def generate_thumbnail(script_path):
    """Generate a thumbnail image from a script JSON."""
    with open(script_path, "r", encoding="utf-8") as f:
        script = json.load(f)

    title = script.get("title", "Episodio")
    narrator = script.get("narrator", "Lua")
    thumb_text = script.get("thumbnail_text", title)
    style = STYLES.get(narrator, STYLES["Lua"])

    # Create image (vertical format 1080x1920)
    img = Image.new("RGB", (1080, 1920), style["bg"])
    draw = ImageDraw.Draw(img)

    # Try to use a system font, fallback to default
    def get_font(size):
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/SFCompact.ttf",
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        ]
        for fp in font_paths:
            if os.path.exists(fp):
                try:
                    return ImageFont.truetype(fp, size)
                except (IOError, OSError):
                    continue
        return ImageFont.load_default()

    font_big = get_font(80)
    font_medium = get_font(48)
    font_small = get_font(32)

    # Draw accent bar at top
    draw.rectangle([(0, 0), (1080, 8)], fill=style["accent"])

    # Draw show name
    draw.text((540, 120), "THE LUA TSUKI SHOW", font=font_small,
              fill=(*style["accent"], 180), anchor="mm")

    # Draw large emoji/dog icons in center area
    emoji_font = get_font(200)
    draw.text((540, 700), "🌭🐕", font=emoji_font, fill=style["text"], anchor="mm")

    # Draw thumbnail text (main hook)
    wrapped = textwrap.fill(thumb_text.upper(), width=12)
    draw.text((540, 1050), wrapped, font=font_big,
              fill=style["accent"], anchor="mm", align="center")

    # Draw narrator tag
    draw.text((540, 1350), f"Narrado por {narrator}", font=font_medium,
              fill=(*style["text"], 200), anchor="mm")

    # Draw bottom accent bar
    draw.rectangle([(0, 1912), (1080, 1920)], fill=style["accent"])

    # Draw side accents
    draw.rectangle([(0, 0), (4, 1920)], fill=style["accent"])
    draw.rectangle([(1076, 0), (1080, 1920)], fill=style["accent"])

    # Save
    os.makedirs(THUMB_DIR, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(script_path))[0]
    thumb_path = os.path.join(THUMB_DIR, f"{base_name}_thumb.png")
    img.save(thumb_path, "PNG")

    print(f"Thumbnail saved: {thumb_path}")
    print(f"Text: {thumb_text}")
    return thumb_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate_thumbnail.py <script.json>")
        sys.exit(1)

    generate_thumbnail(sys.argv[1])
