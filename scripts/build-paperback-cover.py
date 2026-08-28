#!/usr/bin/env python3
"""Build the KDP full-wrap paperback cover from the final interior page count."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageOps
from pypdf import PdfReader
from reportlab.lib.colors import CMYKColor
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "cover" / "full-wrap.json"
TEMP_IMAGE = PROJECT_ROOT / "tmp" / "pdfs" / "paperback-front-cmyk.jpg"

FONT_PATHS = {
    "CoverSans": Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    "CoverSansBold": Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    "CoverSerif": Path("/System/Library/Fonts/Supplemental/BigCaslon.ttf"),
}

PAPER_SPINE_FACTORS = {
    "white": 0.002252,
    "cream": 0.0025,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    return parser.parse_args()


def register_fonts() -> dict[str, str]:
    fallback = {
        "sans": "Helvetica",
        "sans_bold": "Helvetica-Bold",
        "serif": "Times-Roman",
    }
    if not all(path.exists() for path in FONT_PATHS.values()):
        return fallback
    for name, path in FONT_PATHS.items():
        pdfmetrics.registerFont(TTFont(name, str(path)))
    return {
        "sans": "CoverSans",
        "sans_bold": "CoverSansBold",
        "serif": "CoverSerif",
    }


def fit_front_art(source: Path, width_in: float, height_in: float) -> Path:
    target = (math.ceil(width_in * 300), math.ceil(height_in * 300))
    with Image.open(source) as image:
        image = image.convert("RGB")
        fitted = ImageOps.fit(image, target, method=Image.Resampling.LANCZOS)
        TEMP_IMAGE.parent.mkdir(parents=True, exist_ok=True)
        fitted.convert("CMYK").save(
            TEMP_IMAGE,
            format="JPEG",
            quality=95,
            subsampling=0,
            dpi=(300, 300),
        )
    return TEMP_IMAGE


def draw_paragraph(
    pdf: canvas.Canvas,
    text: str,
    style: ParagraphStyle,
    x: float,
    top: float,
    width: float,
    max_height: float,
) -> float:
    paragraph = Paragraph(text, style)
    paragraph_width, paragraph_height = paragraph.wrap(width, max_height)
    if paragraph_height > max_height:
        raise ValueError("Cover copy does not fit in its allocated area")
    paragraph.drawOn(pdf, x, top - paragraph_height)
    return top - paragraph_height


def centered_rotated_baseline(font_name: str, font_size: float) -> float:
    """Return a baseline that centers a rotated line across the spine width."""
    ascent, descent = pdfmetrics.getAscentDescent(font_name, font_size)
    return -(ascent + descent) / 2


def draw_back_field(pdf: canvas.Canvas, width: float, height: float) -> None:
    paper = CMYKColor(0.03, 0.04, 0.11, 0)
    mint = CMYKColor(0.24, 0.02, 0.18, 0.03)
    yellow = CMYKColor(0.02, 0.09, 0.42, 0)
    pink = CMYKColor(0.02, 0.22, 0.12, 0)
    charcoal = CMYKColor(0, 0, 0, 0.82)

    pdf.setFillColor(paper)
    pdf.rect(0, 0, width, height, fill=1, stroke=0)
    pdf.setFillColor(mint)
    pdf.rect(0, height - 1.46 * inch, 1.34 * inch, 1.46 * inch, fill=1, stroke=0)
    pdf.setFillColor(pink)
    pdf.rect(0.55 * inch, 0, 1.1 * inch, 0.72 * inch, fill=1, stroke=0)
    pdf.setFillColor(yellow)
    pdf.rect(3.58 * inch, height - 0.72 * inch, 0.8 * inch, 0.72 * inch, fill=1, stroke=0)

    line_colors = (mint, charcoal, yellow, mint, pink)
    lengths = (2.9, 3.5, 2.2, 3.85, 2.65, 3.2, 1.95, 3.7)
    for index, length in enumerate(lengths):
        y = height - (0.52 + index * 0.105) * inch
        pdf.setStrokeColor(line_colors[index % len(line_colors)])
        pdf.setLineWidth(0.45 if index % 3 else 0.8)
        pdf.line(0, y, length * inch, y)


def build_cover(config: dict) -> tuple[Path, int, float, float, float, float]:
    interior_path = PROJECT_ROOT / config["interior_pdf"]
    source_art = PROJECT_ROOT / config["front_art"]
    output_path = PROJECT_ROOT / config["output_pdf"]
    if not interior_path.exists():
        raise SystemExit(f"Missing interior PDF: {interior_path}")
    if not source_art.exists():
        raise SystemExit(f"Missing front-cover art: {source_art}")

    page_count = len(PdfReader(interior_path).pages)
    paper = config["paper"].lower()
    if paper not in PAPER_SPINE_FACTORS:
        raise SystemExit(f"Unsupported paper type: {paper}")

    trim_width = float(config["trim_width_in"])
    trim_height = float(config["trim_height_in"])
    bleed = float(config["bleed_in"])
    spine_width = page_count * PAPER_SPINE_FACTORS[paper]
    cover_width = bleed + trim_width + spine_width + trim_width + bleed
    cover_height = bleed + trim_height + bleed

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fonts = register_fonts()
    prepared_art = fit_front_art(source_art, trim_width + bleed, cover_height)

    pdf = canvas.Canvas(
        str(output_path),
        pagesize=(cover_width * inch, cover_height * inch),
        pageCompression=1,
    )
    pdf.setTitle("Ambient and Minimalist Music - paperback cover")
    pdf.setAuthor("Alesh Houdek")
    pdf.setSubject(
        f"KDP full-wrap cover; {page_count} pages; {spine_width:.4f} inch spine"
    )

    full_width_pt = cover_width * inch
    full_height_pt = cover_height * inch
    draw_back_field(pdf, full_width_pt, full_height_pt)

    back_left = bleed * inch
    back_right = (bleed + trim_width) * inch
    spine_left = back_right
    spine_right = spine_left + spine_width * inch
    front_left = spine_right

    pdf.drawImage(
        str(prepared_art),
        front_left,
        0,
        width=(trim_width + bleed) * inch,
        height=cover_height * inch,
        preserveAspectRatio=False,
        mask=None,
    )

    ink = CMYKColor(0, 0, 0, 0.91)
    muted = CMYKColor(0, 0, 0, 0.61)
    paper_color = CMYKColor(0.03, 0.04, 0.11, 0)

    # Front typography: its top aligns with the yellow block in the artwork.
    front_text_x = front_left + 1.92 * inch
    title_top = 3.57 * inch
    pdf.setFillColor(ink)
    pdf.setFont(fonts["sans_bold"], 18.5)
    pdf.drawString(front_text_x, title_top, config["title_lines"][0])
    pdf.drawString(front_text_x, title_top - 0.27 * inch, config["title_lines"][1])
    pdf.setFillColor(CMYKColor(0, 0, 0, 0.76))
    pdf.setFont(fonts["serif"], 9.8)
    pdf.drawString(front_text_x, title_top - 0.54 * inch, config["subtitle"])
    pdf.setFillColor(ink)
    pdf.setFont(fonts["sans_bold"], 7.8)
    pdf.drawString(front_text_x, title_top - 0.94 * inch, config["author"])
    pdf.setFillColor(CMYKColor(0, 0, 0, 0.68))
    pdf.setFont(fonts["sans"], 7.1)
    pdf.drawString(front_text_x, title_top - 1.10 * inch, config["cover_credit"])

    # Back-cover copy, with the lower-right barcode area deliberately empty.
    copy_x = back_left + 0.35 * inch
    copy_width = 3.42 * inch
    top = full_height_pt - 1.72 * inch
    lead_style = ParagraphStyle(
        "BackLead",
        fontName=fonts["serif"],
        fontSize=11.2,
        leading=14.2,
        textColor=ink,
        spaceAfter=0,
    )
    top = draw_paragraph(
        pdf,
        config["back_blurb"],
        lead_style,
        copy_x,
        top,
        copy_width,
        3.0 * inch,
    )

    bio_heading_y = min(top - 0.34 * inch, 2.53 * inch)
    pdf.setFillColor(ink)
    pdf.setFont(fonts["sans_bold"], 7.2)
    pdf.drawString(copy_x, bio_heading_y, "ABOUT THE AUTHOR")
    bio_style = ParagraphStyle(
        "BackBio",
        fontName=fonts["sans"],
        fontSize=7.35,
        leading=9.4,
        textColor=muted,
    )
    draw_paragraph(
        pdf,
        config["author_bio"],
        bio_style,
        copy_x,
        bio_heading_y - 0.14 * inch,
        copy_width,
        1.15 * inch,
    )

    # Spine text remains well inside KDP's 0.0625-inch fold safety margin.
    spine_center = (spine_left + spine_right) / 2
    pdf.saveState()
    pdf.translate(spine_center, full_height_pt - 0.55 * inch)
    pdf.rotate(-90)
    pdf.setFillColor(ink)
    spine_title_size = 10.0
    pdf.setFont(fonts["sans_bold"], spine_title_size)
    pdf.drawString(
        0,
        centered_rotated_baseline(fonts["sans_bold"], spine_title_size),
        config["spine_title"],
    )
    pdf.setFillColor(muted)
    spine_author_size = 7.0
    pdf.setFont(fonts["sans"], spine_author_size)
    pdf.drawRightString(
        5.9 * inch,
        centered_rotated_baseline(fonts["sans"], spine_author_size),
        config["spine_author"],
    )
    pdf.restoreState()

    # A paper-colored patch guarantees a quiet area for KDP's generated barcode.
    pdf.setFillColor(paper_color)
    pdf.rect(
        back_right - 2.2 * inch,
        0.25 * inch,
        2.0 * inch,
        1.2 * inch,
        fill=1,
        stroke=0,
    )

    pdf.showPage()
    pdf.save()
    return (
        output_path,
        page_count,
        spine_width,
        cover_width,
        cover_height,
        spine_center / inch,
    )


def main() -> None:
    args = parse_args()
    config_path = args.config
    if not config_path.is_absolute():
        config_path = PROJECT_ROOT / config_path
    with config_path.open(encoding="utf-8") as stream:
        config = json.load(stream)

    output, pages, spine, width, height, spine_center = build_cover(config)
    print(f"Built {output.relative_to(PROJECT_ROOT)}")
    print(
        f"KDP cover: {width:.4f} x {height:.4f} in; "
        f"{pages} cream-paper pages; {spine:.4f} in spine"
    )
    spine_left = float(config["bleed_in"]) + float(config["trim_width_in"])
    print(
        f"Spine placement: {spine_left:.4f} to {spine_left + spine:.4f} in; "
        f"text centered at x={spine_center:.4f} in"
    )


if __name__ == "__main__":
    main()
