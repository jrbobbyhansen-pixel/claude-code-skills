#!/usr/bin/env python3
"""One-time setup: build assets/endcard.png (1080x1920) from a logo image.

Background is sampled from the logo's own corner so the card reads as a
seamless extension of the icon. Optional gold tagline under the mark.

Usage: make_endcard.py <logo.png> [--tagline "text"] [--out path]
Run with the videocut venv python (needs Pillow).
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
GOLD = (201, 160, 76)
FONTS = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
         "/System/Library/Fonts/Helvetica.ttc"]


def load_font(size):
    for f in FONTS:
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("logo")
    ap.add_argument("--tagline", default="")
    ap.add_argument("--out", default=str(Path(__file__).parent.parent / "assets" / "endcard.png"))
    args = ap.parse_args()

    logo = Image.open(args.logo).convert("RGB")
    bg = logo.getpixel((5, 5))
    card = Image.new("RGB", (W, H), bg)

    lw = 880
    lh = round(logo.height * lw / logo.width)
    logo = logo.resize((lw, lh), Image.LANCZOS)
    card.paste(logo, ((W - lw) // 2, (H - lh) // 2 - 80))

    if args.tagline:
        d = ImageDraw.Draw(card)
        f = load_font(52)
        tw = d.textlength(args.tagline, font=f)
        d.text(((W - tw) / 2, (H + lh) // 2 + 40), args.tagline, fill=GOLD, font=f)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    card.save(args.out)
    print(f"end card -> {args.out} (bg {bg})")


if __name__ == "__main__":
    main()
