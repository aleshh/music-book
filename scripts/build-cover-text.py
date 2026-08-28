#!/usr/bin/env python3
"""Build tightly cropped text-only cover assets for layout applications."""

from pathlib import Path

from reportlab.lib.colors import CMYKColor
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PDF = PROJECT_ROOT / "output" / "pdf" / "ambient-and-minimalist-music-cover-text.pdf"
OUTPUT_SVG = PROJECT_ROOT / "output" / "figma" / "ambient-and-minimalist-music-cover-text.svg"

FONT_PATHS = {
    "CoverSans": Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    "CoverSansBold": Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    "CoverSerif": Path("/System/Library/Fonts/Supplemental/BigCaslon.ttf"),
}


def register_fonts() -> dict[str, str]:
    fonts = {
        "sans": "Helvetica",
        "sans_bold": "Helvetica-Bold",
        "serif": "Times-Roman",
    }
    if all(path.exists() for path in FONT_PATHS.values()):
        for name, path in FONT_PATHS.items():
            pdfmetrics.registerFont(TTFont(name, str(path)))
        fonts = {
            "sans": "CoverSans",
            "sans_bold": "CoverSansBold",
            "serif": "CoverSerif",
        }
    return fonts


def main() -> None:
    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    fonts = register_fonts()
    width, height = 220 * inch / 72, 133 * inch / 72
    ink = CMYKColor(0, 0, 0, 0.91)
    muted = CMYKColor(0, 0, 0, 0.58)

    pdf = canvas.Canvas(str(OUTPUT_PDF), pagesize=(width, height), pageCompression=1)
    pdf.setTitle("Ambient and Minimalist Music - cover text")
    pdf.setAuthor("Jonathan Romanovský")
    pdf.setSubject("Text-only cover typography for import into Figma")

    x = 8
    title_baseline = height - 26.565
    title_leading = 26.5

    pdf.setFillColor(ink)
    pdf.setFont(fonts["sans_bold"], 25.5)
    pdf.drawString(x, title_baseline, "Ambient and")
    pdf.drawString(x, title_baseline - title_leading, "Minimalist Music")

    subtitle_baseline = title_baseline - title_leading - 0.29 * inch
    pdf.setFillColor(muted)
    pdf.setFont(fonts["serif"], 13.5)
    pdf.drawString(x, subtitle_baseline, "A Composer’s Field Guide")

    author_baseline = subtitle_baseline - 0.52 * inch
    pdf.setFillColor(ink)
    pdf.setFont(fonts["sans_bold"], 10.8)
    pdf.drawString(x, author_baseline, "Jonathan Romanovský")

    pdf.setFillColor(muted)
    pdf.setFont(fonts["sans"], 9.0)
    pdf.drawString(x, author_baseline - 0.16 * inch, "Preface by Alesh Houdek")

    pdf.showPage()
    pdf.save()

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="220pt" height="133pt" viewBox="0 0 220 133" role="img" aria-labelledby="title desc">
  <title id="title">Ambient and Minimalist Music cover text</title>
  <desc id="desc">Title, subtitle, author, and preface credit</desc>
  <g text-anchor="start">
    <text x="8" y="26.565" fill="#171717" font-family="Arial" font-size="25.5" font-weight="700">Ambient and</text>
    <text x="8" y="53.065" fill="#171717" font-family="Arial" font-size="25.5" font-weight="700">Minimalist Music</text>
    <text x="8" y="73.945" fill="#6b6b6b" font-family="Big Caslon" font-size="13.5">A Composer’s Field Guide</text>
    <text x="8" y="111.385" fill="#171717" font-family="Arial" font-size="10.8" font-weight="700">Jonathan Romanovský</text>
    <text x="8" y="122.905" fill="#6b6b6b" font-family="Arial" font-size="9">Preface by Alesh Houdek</text>
  </g>
</svg>
'''
    OUTPUT_SVG.write_text(svg, encoding="utf-8")
    print(f"Built {OUTPUT_PDF.relative_to(PROJECT_ROOT)}")
    print(f"Built {OUTPUT_SVG.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
