#!/usr/bin/env python3

"""Report stable word counts for the manuscript.

The editorial count excludes generated ``Chapter N:`` labels so a structural
renumbering does not masquerade as added prose. It otherwise counts every
whitespace-delimited token in the numbered manuscript files, including Section
titles, Chapter titles, exercises, notes, and source URLs. The raw source count
is included as a transparent comparison.
"""

from __future__ import annotations

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHAPTER_DIR = PROJECT_ROOT / "chapters"
SHORT_CHAPTER_LABEL = re.compile(r"^(##) Chapter \d+: ", re.MULTILINE)
SHORT_CHAPTER_HEADING = re.compile(r"^## Chapter (\d+): ", re.MULTILINE)
SECTION_HEADING = re.compile(r"^# Section (\d+): ", re.MULTILINE)


def token_count(text: str) -> int:
    return len(text.split())


def main() -> None:
    files = sorted(CHAPTER_DIR.glob("[0-9][0-9]-*.md"))
    if not files:
        raise SystemExit("word-count: no numbered manuscript files found")

    texts = [path.read_text(encoding="utf-8") for path in files]
    manuscript = "\n".join(texts)
    chapter_numbers = [
        int(match.group(1)) for match in SHORT_CHAPTER_HEADING.finditer(manuscript)
    ]
    section_numbers = [
        int(match.group(1)) for match in SECTION_HEADING.finditer(manuscript)
    ]

    if section_numbers != list(range(1, len(section_numbers) + 1)):
        raise SystemExit("word-count: Section numbering is incomplete or out of order")
    if chapter_numbers != list(range(1, len(chapter_numbers) + 1)):
        raise SystemExit("word-count: Chapter numbering is incomplete or out of order")

    editorial_text = SHORT_CHAPTER_LABEL.sub(r"\1 ", manuscript)
    editorial_count = token_count(editorial_text)
    source_count = token_count(manuscript)

    print(f"Editorial manuscript: {editorial_count:,} words")
    print(f"Markdown source:      {source_count:,} words")
    print(f"Structure:            {len(section_numbers)} Sections, {len(chapter_numbers)} Chapters")
    print()
    print("Editorial count excludes generated 'Chapter N:' labels.")
    print("Both counts include headings, exercises, notes, and source URLs.")


if __name__ == "__main__":
    main()
