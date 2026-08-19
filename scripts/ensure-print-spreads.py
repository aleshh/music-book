#!/usr/bin/env python3
"""Finalize Section title pages and add physical folios."""

from __future__ import annotations

import argparse
import re
from io import BytesIO
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError as exc:
    raise SystemExit(
        "ensure-print-spreads: missing pypdf; run `python3 -m pip install pypdf`"
    ) from exc

try:
    from reportlab.lib.colors import HexColor
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen.canvas import Canvas
except ImportError as exc:
    raise SystemExit(
        "ensure-print-spreads: missing reportlab; "
        "run `python3 -m pip install reportlab`"
    ) from exc


SECTION_TITLE = re.compile(r"^Section\s+\d+", re.IGNORECASE)
PUBLICATION_PAGE = re.compile(r"^Copyright\s+©\s+\d{4}\s+Alesh Houdek")


def page_text(page: object) -> str:
    return (page.extract_text() or "").strip()


def section_title_indices(reader: PdfReader) -> list[int]:
    return [
        index
        for index, page in enumerate(reader.pages)
        if SECTION_TITLE.match(page_text(page))
    ]


def page_size(page: object) -> tuple[float, float]:
    return float(page.mediabox.width), float(page.mediabox.height)


def should_number(page_number: int, text: str) -> bool:
    return (
        page_number > 1
        and bool(text)
        and not SECTION_TITLE.match(text)
        and not PUBLICATION_PAGE.match(text)
    )


def add_page_numbers(writer: PdfWriter) -> None:
    font_name = "PocketPageNumber"
    pdfmetrics.registerFont(TTFont(font_name, "Vera.ttf"))

    packet = BytesIO()
    first_width, first_height = page_size(writer.pages[0])
    canvas = Canvas(packet, pagesize=(first_width, first_height))

    numbered_pages: list[bool] = []
    for page_number, page in enumerate(writer.pages, start=1):
        width, height = page_size(page)
        canvas.setPageSize((width, height))
        text = page_text(page)
        add_number = should_number(page_number, text)
        numbered_pages.append(add_number)

        if add_number:
            canvas.setFillColor(HexColor("#696969"))
            canvas.setFont(font_name, 7)
            if page_number % 2 == 0:
                canvas.drawString(27, 18, str(page_number))
            else:
                canvas.drawRightString(width - 27, 18, str(page_number))

        canvas.showPage()

    canvas.save()
    packet.seek(0)
    overlays = PdfReader(packet)

    for page, overlay, add_number in zip(
        writer.pages, overlays.pages, numbered_pages, strict=True
    ):
        if add_number:
            page.merge_page(overlay)


def finalize_pdf(input_path: Path, output_path: Path, expected_count: int) -> None:
    reader = PdfReader(input_path)
    title_indices = section_title_indices(reader)

    if len(title_indices) != expected_count:
        raise SystemExit(
            "ensure-print-spreads: found "
            f"{len(title_indices)} Section title pages; expected {expected_count}"
        )

    writer = PdfWriter()
    writer.clone_document_from_reader(reader)

    add_page_numbers(writer)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(".tmp.pdf")
    with temporary_path.open("wb") as stream:
        writer.write(stream)
    temporary_path.replace(output_path)

    result = PdfReader(output_path)
    result_titles = section_title_indices(result)
    failures: list[str] = []

    if len(result_titles) != expected_count:
        failures.append(
            f"found {len(result_titles)} Section title pages after writing"
        )

    for title_index in result_titles:
        page_number = title_index + 1
        title_text = page_text(result.pages[title_index])
        if len(title_text.splitlines()) < 2:
            failures.append(f"Section title on page {page_number} lacks its summary")
        if title_index + 1 >= len(result.pages):
            failures.append(f"Section title on page {page_number} lacks following content")
            continue
        if not page_text(result.pages[title_index + 1]):
            failures.append(f"page {page_number + 1} is unexpectedly blank")

    for page_number, page in enumerate(result.pages, start=1):
        text = page_text(page)
        if should_number(page_number, text):
            if not text.splitlines() or text.splitlines()[-1] != str(page_number):
                failures.append(f"page {page_number} has an incorrect printed folio")

    if failures:
        output_path.unlink(missing_ok=True)
        raise SystemExit("ensure-print-spreads: " + "; ".join(failures))

    print(
        "Finalized "
        f"{len(result_titles)} Section title pages across {len(result.pages)} pages"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_pdf", type=Path)
    parser.add_argument("output_pdf", type=Path)
    parser.add_argument("--expected-count", type=int, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    finalize_pdf(args.input_pdf, args.output_pdf, args.expected_count)


if __name__ == "__main__":
    main()
