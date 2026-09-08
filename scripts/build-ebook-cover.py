#!/usr/bin/env python3
"""Build a front-only RGB cover for EPUB and Kindle distribution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "cover" / "full-wrap.json"

FONT_PATHS = {
    "sans": Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    "sans_bold": Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    "serif": Path("/System/Library/Fonts/Supplemental/BigCaslon.ttf"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    return parser.parse_args()


def font(path: Path, points: float, dpi: float) -> ImageFont.FreeTypeFont:
    if not path.exists():
        raise SystemExit(f"Missing cover font: {path}")
    return ImageFont.truetype(str(path), round(points * dpi / 72))


def build_cover(config: dict) -> Path:
    source_path = PROJECT_ROOT / config["front_art"]
    output_path = PROJECT_ROOT / config["ebook_cover"]
    width = int(config["ebook_width_px"])
    height = int(config["ebook_height_px"])
    if not source_path.exists():
        raise SystemExit(f"Missing front-cover art: {source_path}")

    with Image.open(source_path) as source:
        cover = ImageOps.fit(
            source.convert("RGB"),
            (width, height),
            method=Image.Resampling.LANCZOS,
        )

    dpi = width / float(config["trim_width_in"])
    draw = ImageDraw.Draw(cover)
    x = round(1.92 * dpi)
    first_baseline = round((float(config["trim_height_in"]) - 3.445) * dpi)
    ink = (23, 23, 23)
    dark_muted = (61, 61, 61)
    muted = (82, 82, 82)

    sans_bold_18 = font(FONT_PATHS["sans_bold"], 18.5, dpi)
    serif_10 = font(FONT_PATHS["serif"], 9.8, dpi)
    sans_bold_8 = font(FONT_PATHS["sans_bold"], 7.8, dpi)
    sans_7 = font(FONT_PATHS["sans"], 7.1, dpi)

    draw.text(
        (x, first_baseline),
        config["title_lines"][0],
        font=sans_bold_18,
        fill=ink,
        anchor="ls",
    )
    draw.text(
        (x, first_baseline + round(0.27 * dpi)),
        config["title_lines"][1],
        font=sans_bold_18,
        fill=ink,
        anchor="ls",
    )
    draw.text(
        (x, first_baseline + round(0.54 * dpi)),
        config["subtitle"],
        font=serif_10,
        fill=dark_muted,
        anchor="ls",
    )
    draw.text(
        (x, first_baseline + round(0.94 * dpi)),
        config["author"],
        font=sans_bold_8,
        fill=ink,
        anchor="ls",
    )
    draw.text(
        (x, first_baseline + round(1.10 * dpi)),
        config["cover_credit"],
        font=sans_7,
        fill=muted,
        anchor="ls",
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cover.save(
        output_path,
        format="JPEG",
        quality=95,
        subsampling=0,
        dpi=(round(dpi), round(dpi)),
        optimize=True,
    )
    return output_path


def main() -> None:
    args = parse_args()
    config_path = args.config
    if not config_path.is_absolute():
        config_path = PROJECT_ROOT / config_path
    with config_path.open(encoding="utf-8") as stream:
        config = json.load(stream)
    output = build_cover(config)
    print(f"Built {output.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
