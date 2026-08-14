#!/usr/bin/env python3

"""Report stable word and sentence-length statistics for the manuscript.

The editorial count excludes generated ``N.`` labels so a structural
renumbering does not masquerade as added prose. It otherwise counts every
whitespace-delimited token in the numbered manuscript files, including Section
titles, numbered-piece titles, exercises, notes, and source URLs. The raw source
count is included as a transparent comparison.

Sentence statistics describe body prose only. They exclude headings, source
notes, generated number labels, and Markdown footnote markers so structural
markup and URLs do not masquerade as prose style.
"""

from __future__ import annotations

import re
import statistics
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHAPTER_DIR = PROJECT_ROOT / "chapters"
NUMBERED_PIECE_LABEL = re.compile(r"^(##) \d+\. ", re.MULTILINE)
NUMBERED_PIECE_HEADING = re.compile(r"^## (\d+)\. ", re.MULTILINE)
SECTION_HEADING = re.compile(r"^# Section (\d+): ", re.MULTILINE)
BLOCK_SPLIT = re.compile(r"\n{2,}")
LIST_ITEM = re.compile(r"^\s*(?:[-+*]|\d+[.)])\s+")
LEADING_LABEL = re.compile(r"^\*\*[^*]+[.!?]\*\*\s*")
FOOTNOTE_REFERENCE = re.compile(r"\[\^[^\]]+\]")
MARKDOWN_LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")
AUTOLINK = re.compile(r"<(?:https?://|mailto:)[^>]+>")
HTML_TAG = re.compile(r"<[^>]+>")
SENTENCE_END = re.compile(r"[.!?]+(?:[\"”’')\]]*)?(?=\s+|$)")

ABBREVIATIONS = {
    "dr.",
    "e.g.",
    "i.e.",
    "jr.",
    "mr.",
    "mrs.",
    "ms.",
    "no.",
    "op.",
    "p.",
    "pp.",
    "prof.",
    "sr.",
    "st.",
    "u.k.",
    "u.s.",
    "vol.",
}


def token_count(text: str) -> int:
    return len(text.split())


def body_units(text: str) -> list[str]:
    """Return prose and list-item units from the manuscript body."""
    body = text.partition("\n---\n")[0]
    units: list[str] = []

    for block in BLOCK_SPLIT.split(body.strip()):
        if not block or block.lstrip().startswith("#"):
            continue

        current: list[str] = []

        def flush() -> None:
            if current:
                units.append(" ".join(current))
                current.clear()

        for line in block.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if LIST_ITEM.match(stripped):
                flush()
                stripped = LIST_ITEM.sub("", stripped, count=1)
            stripped = stripped.removeprefix("> ")
            current.append(stripped)
        flush()

    return units


def clean_markdown(text: str) -> str:
    text = FOOTNOTE_REFERENCE.sub("", text)
    text = MARKDOWN_LINK.sub(r"\1", text)
    text = AUTOLINK.sub("", text)
    text = HTML_TAG.sub("", text)
    text = LEADING_LABEL.sub("", text)
    text = text.replace("**", "").replace("__", "")
    text = text.replace("*", "").replace("_", "").replace("`", "")
    return re.sub(r"\s+", " ", text).strip()


def is_abbreviation(fragment: str) -> bool:
    match = re.search(r"([A-Za-z.]+\.)[\"”’')\]]*$", fragment)
    if not match:
        return False
    return match.group(1).lower() in ABBREVIATIONS


def split_sentences(unit: str) -> list[str]:
    """Split one prose unit conservatively at terminal punctuation."""
    sentences: list[str] = []
    start = 0

    for match in SENTENCE_END.finditer(unit):
        end = match.end()
        fragment = unit[start:end].strip()
        if not fragment or is_abbreviation(fragment):
            continue

        remainder = unit[end:].lstrip()
        sentence_starters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789“‘\"(["
        if remainder and remainder[0] not in sentence_starters:
            continue

        sentences.append(fragment)
        start = end

    remainder = unit[start:].strip()
    if remainder:
        sentences.append(remainder)
    return sentences


def sentence_lengths(texts: list[str]) -> list[int]:
    lengths: list[int] = []
    for text in texts:
        for unit in body_units(text):
            cleaned = clean_markdown(unit)
            for sentence in split_sentences(cleaned):
                length = token_count(sentence)
                if length:
                    lengths.append(length)
    return lengths


def percentile(values: list[int], proportion: float) -> float:
    """Return a linearly interpolated percentile for sorted integer values."""
    ordered = sorted(values)
    position = (len(ordered) - 1) * proportion
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def main() -> None:
    files = sorted(CHAPTER_DIR.glob("[0-9][0-9]-*.md"))
    if not files:
        raise SystemExit("word-count: no numbered manuscript files found")

    texts = [path.read_text(encoding="utf-8") for path in files]
    manuscript = "\n".join(texts)
    piece_numbers = [
        int(match.group(1)) for match in NUMBERED_PIECE_HEADING.finditer(manuscript)
    ]
    section_numbers = [
        int(match.group(1)) for match in SECTION_HEADING.finditer(manuscript)
    ]

    if section_numbers != list(range(1, len(section_numbers) + 1)):
        raise SystemExit("word-count: Section numbering is incomplete or out of order")
    if piece_numbers != list(range(1, len(piece_numbers) + 1)):
        raise SystemExit("word-count: piece numbering is incomplete or out of order")

    editorial_text = NUMBERED_PIECE_LABEL.sub(r"\1 ", manuscript)
    editorial_count = token_count(editorial_text)
    source_count = token_count(manuscript)
    lengths = sentence_lengths(texts)
    if not lengths:
        raise SystemExit("word-count: no body-prose sentences found")

    print(f"Editorial manuscript: {editorial_count:,} words")
    print(f"Markdown source:      {source_count:,} words")
    print(
        "Structure:            "
        f"{len(section_numbers)} Sections, {len(piece_numbers)} numbered pieces"
    )
    print()
    print("Editorial count excludes generated 'N.' labels.")
    print("Both counts include headings, exercises, notes, and source URLs.")
    print()
    print("Sentence length (body prose only):")
    print(f"  Sentences:            {len(lengths):,}")
    print(f"  Average:              {statistics.mean(lengths):.2f} words")
    print(f"  Median:               {statistics.median(lengths):.1f} words")
    print(f"  Standard deviation:   {statistics.pstdev(lengths):.2f} words")
    print(
        "  Middle 50%:           "
        f"{percentile(lengths, 0.25):.1f}–{percentile(lengths, 0.75):.1f} words"
    )
    print(f"  90th percentile:      {percentile(lengths, 0.90):.1f} words")
    print(f"  Range:                {min(lengths)}–{max(lengths)} words")
    print()
    print("Sentence statistics exclude headings, source notes, and footnote markers.")
    print("Standard deviation is population standard deviation.")


if __name__ == "__main__":
    main()
