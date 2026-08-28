#!/usr/bin/env python3
"""Build editable front-cover concepts from cover/variants.json."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import CMYKColor
from reportlab.lib.units import inch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "cover" / "variants.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "output" / "pdf" / "covers"

FONT_PATHS = {
    "CoverSans": Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    "CoverSansBold": Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    "CoverSerif": Path("/System/Library/Fonts/Supplemental/BigCaslon.ttf"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--variant",
        action="append",
        help="Build only this variant id; repeat to select more than one.",
    )
    return parser.parse_args()


def register_fonts() -> dict[str, str]:
    names = {
        "sans": "Helvetica",
        "sans_bold": "Helvetica-Bold",
        "serif": "Times-Italic",
    }
    for font_name, path in FONT_PATHS.items():
        if path.exists():
            pdfmetrics.registerFont(TTFont(font_name, str(path)))
    if all(path.exists() for path in FONT_PATHS.values()):
        names = {
            "sans": "CoverSans",
            "sans_bold": "CoverSansBold",
            "serif": "CoverSerif",
        }
    return names


def cmyk_from_hex(value: str) -> CMYKColor:
    value = value.lstrip("#")
    red, green, blue = (int(value[i : i + 2], 16) / 255 for i in (0, 2, 4))
    key = 1 - max(red, green, blue)
    if key >= 0.999:
        return CMYKColor(0, 0, 0, 1)
    cyan = (1 - red - key) / (1 - key)
    magenta = (1 - green - key) / (1 - key)
    yellow = (1 - blue - key) / (1 - key)
    return CMYKColor(cyan, magenta, yellow, key)


def draw_rect(c: canvas.Canvas, rect: dict, color: CMYKColor) -> None:
    c.setFillColor(color)
    c.rect(
        rect["x"] * inch,
        rect["y"] * inch,
        rect["w"] * inch,
        rect["h"] * inch,
        stroke=0,
        fill=1,
    )


def draw_outline_rect(
    c: canvas.Canvas,
    rect: dict,
    color: CMYKColor,
    width: float,
    offset_x: float = 0,
    offset_y: float = 0,
) -> None:
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.rect(
        (rect["x"] + offset_x) * inch,
        (rect["y"] + offset_y) * inch,
        rect["w"] * inch,
        rect["h"] * inch,
        stroke=1,
        fill=0,
    )


def build_nested_layers(card: dict, nest: dict) -> list[dict]:
    """Return strictly containing layers ordered from outside to inside."""
    current = dict(card)
    inner_to_outer: list[dict] = []
    patterns = {
        key: nest[key]
        for key in ("growth_w", "growth_h", "shift_x", "shift_y")
    }

    for index in range(nest["count"]):
        values = {
            key: pattern[index % len(pattern)] for key, pattern in patterns.items()
        }
        grow_w = values["growth_w"]
        grow_h = values["growth_h"]
        shift_x = values["shift_x"]
        shift_y = values["shift_y"]
        if abs(shift_x) >= grow_w / 2 or abs(shift_y) >= grow_h / 2:
            raise ValueError("Layer drift must be smaller than half its growth")

        outer = {
            "color": nest["colors"][index % len(nest["colors"])],
            "x": current["x"] - grow_w / 2 + shift_x,
            "y": current["y"] - grow_h / 2 + shift_y,
            "w": current["w"] + grow_w,
            "h": current["h"] + grow_h,
        }
        if not (
            outer["x"] < current["x"]
            and outer["y"] < current["y"]
            and outer["x"] + outer["w"] > current["x"] + current["w"]
            and outer["y"] + outer["h"] > current["y"] + current["h"]
        ):
            raise ValueError(f"Layer {index + 1} does not strictly contain its child")
        inner_to_outer.append(outer)
        current = outer

    return list(reversed(inner_to_outer))


def build_random_nested_layers(card: dict, nest: dict) -> list[dict]:
    """Build reproducibly irregular layers with one strongly expanded edge."""
    generator = random.Random(nest["seed"])
    current = dict(card)
    inner_to_outer: list[dict] = []
    edge_names = ("left", "right", "bottom", "top")

    for index in range(nest["count"]):
        expansion = {
            edge: generator.uniform(nest["base_min"], nest["base_max"])
            for edge in edge_names
        }
        accent_edge = generator.choice(edge_names)
        expansion[accent_edge] += generator.uniform(
            nest["accent_min"], nest["accent_max"]
        )
        outer = {
            "color": nest["colors"][index % len(nest["colors"])],
            "x": current["x"] - expansion["left"],
            "y": current["y"] - expansion["bottom"],
            "w": current["w"] + expansion["left"] + expansion["right"],
            "h": current["h"] + expansion["bottom"] + expansion["top"],
            "accent_edge": accent_edge,
        }
        inner_to_outer.append(outer)
        current = outer

    return list(reversed(inner_to_outer))


def draw_cover(
    output_path: Path,
    page: dict,
    content: dict,
    palette: dict[str, CMYKColor],
    variant: dict,
    fonts: dict[str, str],
) -> None:
    width = page["width_in"] * inch
    height = page["height_in"] * inch
    c = canvas.Canvas(str(output_path), pagesize=(width, height), pageCompression=1)
    c.setTitle(f'{content["title_lines"][0]} {content["title_lines"][1]} - cover concept')
    c.setAuthor(content["author"])
    c.setSubject(variant["name"])

    c.setFillColor(palette[variant["background"]])
    c.rect(0, 0, width, height, stroke=0, fill=1)
    card = variant["card"]
    if "random_nest" in variant:
        layers = build_random_nested_layers(card, variant["random_nest"])
    elif "nest" in variant:
        layers = build_nested_layers(card, variant["nest"])
    else:
        layers = variant["layers"]
    render = variant.get("render", {"mode": "fill"})
    if render["mode"] == "fill":
        for layer in layers:
            draw_rect(c, layer, palette[layer["color"]])
    elif render["mode"] == "outline":
        widths = render["stroke_widths"]
        for index, layer in enumerate(layers):
            draw_outline_rect(
                c,
                layer,
                palette[layer["color"]],
                widths[index % len(widths)],
            )
    elif render["mode"] == "registration":
        for layer in layers:
            for registration in render["registrations"]:
                draw_outline_rect(
                    c,
                    layer,
                    palette[registration["color"]],
                    registration["stroke_width"],
                    registration["offset_x"],
                    registration["offset_y"],
                )
    else:
        raise ValueError(f'Unknown render mode: {render["mode"]}')

    draw_rect(c, card, palette["white"])
    if "card_stroke" in render:
        draw_outline_rect(
            c,
            card,
            palette[render["card_stroke"]["color"]],
            render["card_stroke"]["width"],
        )

    type_spec = variant["type"]
    text_x = type_spec["x"] * inch
    title_baseline = type_spec["title_top"] * inch

    c.setFillColor(palette["ink"])
    c.setFont(fonts["sans_bold"], type_spec["title_size"])
    for index, line in enumerate(content["title_lines"]):
        baseline = title_baseline - index * type_spec["title_leading"]
        c.drawString(text_x, baseline, line)

    default_subtitle_gap = type_spec["title_leading"] / 72 + 0.25
    baseline -= type_spec.get("subtitle_gap", default_subtitle_gap) * inch
    c.setFillColor(palette["muted"])
    c.setFont(fonts["serif"], 12.2)
    c.drawString(text_x, baseline, content["subtitle"])

    baseline -= type_spec.get("author_gap", 0.58) * inch
    c.setFillColor(palette["ink"])
    c.setFont(fonts["sans_bold"], 9.4)
    c.drawString(text_x, baseline, content["author"])

    baseline -= type_spec.get("credit_gap", 0.24) * inch
    c.setFillColor(palette["muted"])
    c.setFont(fonts["sans"], 7.8)
    c.drawString(text_x, baseline, content["credit"])

    c.showPage()
    c.save()


def main() -> None:
    args = parse_args()
    with args.config.open(encoding="utf-8") as stream:
        config = json.load(stream)

    selected = set(args.variant or [])
    variants = [
        variant
        for variant in config["variants"]
        if not selected or variant["id"] in selected
    ]
    missing = selected - {variant["id"] for variant in variants}
    if missing:
        raise SystemExit(f"Unknown variant id(s): {', '.join(sorted(missing))}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    fonts = register_fonts()
    palette = {
        name: cmyk_from_hex(value) for name, value in config["palette"].items()
    }

    for variant in variants:
        output_path = args.output_dir / (
            f'ambient-and-minimalist-music-cover-{variant["id"]}.pdf'
        )
        draw_cover(
            output_path,
            config["page"],
            config["content"],
            palette,
            variant,
            fonts,
        )
        print(f"Built {output_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
