"""
image_generator.py — Generates modern dark-themed blog thumbnails using Pillow.
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from utils import log, log_error, get_image_dir


# ─── Design Constants ────────────────────────────────────────
WIDTH = 1200
HEIGHT = 630

# Dark theme colors
BG_COLOR_TOP = (15, 23, 42)       # #0f172a — slate-900
BG_COLOR_BOTTOM = (30, 41, 59)    # #1e293b — slate-800
ACCENT_COLOR = (99, 102, 241)     # #6366f1 — indigo-500
TEXT_COLOR = (248, 250, 252)       # #f8fafc — slate-50
SUBTITLE_COLOR = (148, 163, 184)  # #94a3b8 — slate-400

SITE_NAME = "joomha.dev"


def _create_gradient(draw: ImageDraw.ImageDraw) -> None:
    """Draw a vertical gradient background."""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(BG_COLOR_TOP[0] + (BG_COLOR_BOTTOM[0] - BG_COLOR_TOP[0]) * ratio)
        g = int(BG_COLOR_TOP[1] + (BG_COLOR_BOTTOM[1] - BG_COLOR_TOP[1]) * ratio)
        b = int(BG_COLOR_TOP[2] + (BG_COLOR_BOTTOM[2] - BG_COLOR_TOP[2]) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def _draw_accent_bar(draw: ImageDraw.ImageDraw) -> None:
    """Draw a decorative accent bar at the top."""
    bar_height = 6
    draw.rectangle([(0, 0), (WIDTH, bar_height)], fill=ACCENT_COLOR)


def _draw_decorative_elements(draw: ImageDraw.ImageDraw) -> None:
    """Draw subtle decorative geometric elements."""
    # Bottom-right circle (subtle)
    circle_color = (99, 102, 241, 30)  # Very transparent indigo
    cx, cy, r = WIDTH - 100, HEIGHT - 80, 120
    for i in range(r, 0, -1):
        alpha = int(30 * (i / r))
        color = (ACCENT_COLOR[0], ACCENT_COLOR[1], ACCENT_COLOR[2])
        # Draw concentric circles with fading opacity simulation
        if i % 3 == 0:
            draw.ellipse(
                [(cx - i, cy - i), (cx + i, cy + i)],
                outline=color,
                width=1,
            )

    # Top-right dots pattern
    for row in range(3):
        for col in range(4):
            x = WIDTH - 200 + col * 20
            y = 30 + row * 20
            draw.ellipse([(x, y), (x + 4, y + 4)], fill=SUBTITLE_COLOR)


def _get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Get a font, falling back to default if system fonts aren't available."""
    font_candidates = [
        # Windows
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        # Linux (GitHub Actions)
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        # macOS
        "/System/Library/Fonts/Helvetica.ttc",
    ]

    if bold:
        # Prefer bold variants
        font_candidates = [f for f in font_candidates if "bold" in f.lower() or "Bold" in f or "bd" in f.lower()] + font_candidates

    for font_path in font_candidates:
        try:
            return ImageFont.truetype(font_path, size)
        except (OSError, IOError):
            continue

    # Fallback to default
    log("IMAGE", "Using default font (no system fonts found)")
    return ImageFont.load_default()


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        try:
            bbox = font.getbbox(test_line)
            text_width = bbox[2] - bbox[0]
        except AttributeError:
            text_width = font.getlength(test_line)

        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines[:4]  # Max 4 lines


def generate_thumbnail(title: str, slug: str) -> Path | None:
    """
    Generate a modern dark-themed thumbnail for a blog post.
    Returns the path to the saved image, or None on failure.
    """
    log("IMAGE", f"Generating thumbnail for: '{title}'")

    try:
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)

        # Background gradient
        _create_gradient(draw)

        # Accent bar
        _draw_accent_bar(draw)

        # Decorative elements
        _draw_decorative_elements(draw)

        # Fonts
        title_font = _get_font(48, bold=True)
        site_font = _get_font(22, bold=False)
        tag_font = _get_font(16, bold=False)

        # Title text (wrapped)
        padding_x = 80
        max_text_width = WIDTH - (padding_x * 2)
        lines = _wrap_text(title, title_font, max_text_width)

        # Calculate title block height for vertical centering
        try:
            line_height = title_font.getbbox("Ay")[3] + 12
        except AttributeError:
            line_height = 60

        total_title_height = len(lines) * line_height
        title_start_y = (HEIGHT - total_title_height) // 2 - 30

        for i, line in enumerate(lines):
            y = title_start_y + i * line_height
            draw.text((padding_x, y), line, fill=TEXT_COLOR, font=title_font)

        # Site name (bottom-left)
        site_y = HEIGHT - 60
        draw.text((padding_x, site_y), SITE_NAME, fill=SUBTITLE_COLOR, font=site_font)

        # Accent dot before site name
        draw.ellipse(
            [(padding_x - 18, site_y + 6), (padding_x - 8, site_y + 16)],
            fill=ACCENT_COLOR,
        )

        # Save
        output_dir = get_image_dir()
        output_path = output_dir / f"{slug}.png"
        img.save(output_path, "PNG", optimize=True)

        log("IMAGE", f"Thumbnail saved: {output_path}")
        return output_path

    except Exception as e:
        log_error("IMAGE", f"Failed to generate thumbnail: {e}")
        return None


if __name__ == "__main__":
    generate_thumbnail(
        "Building AI Agents with Astro and TypeScript for Modern Web",
        "building-ai-agents-astro-typescript"
    )
