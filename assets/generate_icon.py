"""Generates assets/icon.ico: a simple rising-bars mark for PyInvest.

Usage:
    python assets/generate_icon.py
"""
from pathlib import Path

from PIL import Image, ImageDraw

SIZE = 256
BG_COLOR = (14, 98, 70, 255)       # dark green
BAR_COLOR = (255, 255, 255, 255)   # white
ACCENT_COLOR = (74, 222, 128, 255)  # light green (tallest bar highlight)


def build_icon() -> Image.Image:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = int(SIZE * 0.08)
    draw.rounded_rectangle(
        [margin, margin, SIZE - margin, SIZE - margin],
        radius=int(SIZE * 0.20),
        fill=BG_COLOR,
    )

    bar_heights = [0.32, 0.48, 0.64, 0.82]
    bar_colors = [BAR_COLOR, BAR_COLOR, BAR_COLOR, ACCENT_COLOR]
    n = len(bar_heights)

    area_left = SIZE * 0.24
    area_right = SIZE * 0.80
    area_bottom = SIZE * 0.74
    area_top = SIZE * 0.24

    gap = SIZE * 0.035
    bar_width = (area_right - area_left - gap * (n - 1)) / n

    for i, (h_ratio, color) in enumerate(zip(bar_heights, bar_colors)):
        x0 = area_left + i * (bar_width + gap)
        x1 = x0 + bar_width
        bar_h = (area_bottom - area_top) * h_ratio
        y0 = area_bottom - bar_h
        y1 = area_bottom
        radius = bar_width * 0.28
        draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=color)

    return img


if __name__ == "__main__":
    icon = build_icon()
    out_path = Path(__file__).parent / "icon.ico"
    icon.save(out_path, format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"Ícone salvo em: {out_path.resolve()}")
