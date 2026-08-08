#!/usr/bin/env python3

"""Convert manuscript headings and paragraph rhythm to the fast-flow format.

This is an intentionally one-way editorial migration. It refuses to run after
the Section/numbered-piece hierarchy has already been applied.
"""

from __future__ import annotations

import argparse
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHAPTER_DIR = PROJECT_ROOT / "chapters"

TOP_HEADING = re.compile(r"^# Chapter (\d+): (.+)$")
SECOND_HEADING = re.compile(r"^## (.+)$")
NUMBERED_SECOND_HEADING = re.compile(r"^(?:Chapter )?\d+[:.] (.+)$")
SENTENCE_EDGE = re.compile(
    r"[.!?](?:[\"”’')\]*_]*)(?:\[\^[^\]]+\])?\s+(?=[“‘\"(\[*_]*[A-Z0-9])"
)

ABBREVIATIONS = {
    "dr.",
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
    "vol.",
}


@dataclass
class ProseBlock:
    file: Path
    block_index: int
    prose_index: int
    text: str
    split_at: int | None


def chapter_files() -> list[Path]:
    return sorted(CHAPTER_DIR.glob("[0-9][0-9]-*.md"))


def blocks_for(path: Path) -> list[str]:
    return re.split(r"\n{2,}", path.read_text(encoding="utf-8").strip())


def is_prose(block: str, in_notes: bool) -> bool:
    first = block.lstrip().splitlines()[0]
    if in_notes:
        return False
    if first.startswith(("#", "- ", "* ", "+ ", ">", "```", "~~~", "[^")):
        return False
    if re.match(r"^\d+[.)]\s", first):
        return False
    if first == "---":
        return False
    return True


def flattened(block: str) -> str:
    return re.sub(r"\s+", " ", block.strip())


def valid_sentence_edges(text: str) -> list[int]:
    edges: list[int] = []
    for match in SENTENCE_EDGE.finditer(text):
        prefix = text[: match.start() + 1]
        word_match = re.search(r"([A-Za-z]+\.)$", prefix)
        if word_match and word_match.group(1).lower() in ABBREVIATIONS:
            continue
        if re.search(r"\b[A-Z]\.$", prefix):
            continue
        edge = match.end()
        if edge >= 80 and len(text) - edge >= 80:
            edges.append(edge)
    return edges


def choose_edge(text: str) -> int | None:
    if len(text) < 190:
        return None
    edges = valid_sentence_edges(text)
    if not edges:
        return None
    midpoint = len(text) / 2
    return min(edges, key=lambda edge: abs(edge - midpoint))


def inventory() -> tuple[dict[Path, list[str]], list[ProseBlock], int]:
    files = chapter_files()
    if not files:
        raise SystemExit("No manuscript files found.")

    all_blocks: dict[Path, list[str]] = {}
    prose: list[ProseBlock] = []
    prose_index = 0
    internal_headings = 0

    for path in files:
        blocks = blocks_for(path)
        all_blocks[path] = blocks
        in_notes = False

        for block_index, block in enumerate(blocks):
            heading = SECOND_HEADING.fullmatch(block.strip())
            if heading:
                if heading.group(1).strip().lower() == "notes":
                    in_notes = True
                else:
                    internal_headings += 1
                continue

            if block.lstrip().startswith("[^"):
                in_notes = True

            if is_prose(block, in_notes):
                text = flattened(block)
                prose.append(
                    ProseBlock(
                        file=path,
                        block_index=block_index,
                        prose_index=prose_index,
                        text=text,
                        split_at=choose_edge(text),
                    )
                )
                prose_index += 1

    return all_blocks, prose, internal_headings


def evenly_distributed(candidates: list[ProseBlock], target: int) -> set[tuple[Path, int]]:
    if target >= len(candidates):
        return {(item.file, item.block_index) for item in candidates}
    if target <= 0:
        return set()
    if target == 1:
        chosen = [candidates[len(candidates) // 2]]
    else:
        chosen = []
        used: set[int] = set()
        for position in range(target):
            index = round(position * (len(candidates) - 1) / (target - 1))
            if index not in used:
                chosen.append(candidates[index])
                used.add(index)
        if len(chosen) < target:
            for index, item in enumerate(candidates):
                if index not in used:
                    chosen.append(item)
                    used.add(index)
                    if len(chosen) == target:
                        break
    return {(item.file, item.block_index) for item in chosen}


def wrapped(text: str) -> str:
    return textwrap.fill(
        text.strip(),
        width=79,
        break_long_words=False,
        break_on_hyphens=False,
    )


def section_reference_language(text: str) -> str:
    replacements = (
        ("This chapter", "This section"),
        ("this chapter", "this section"),
        ("The chapter", "The section"),
        ("the chapter", "the section"),
        ("previous chapter", "previous section"),
        ("preceding chapter", "preceding section"),
        ("next chapter", "next section"),
        ("later chapter", "later section"),
        ("its own chapter", "its own section"),
        ("chapter on", "section on"),
        ("In Chapter 4,", "In Section 4,"),
        ("last chapter", "last section"),
    )
    for before, after in replacements:
        text = text.replace(before, after)
    return text


def renumber_numbered_pieces() -> None:
    global_number = 0
    files = chapter_files()

    for path in files:
        transformed: list[str] = []
        for block in blocks_for(path):
            second = SECOND_HEADING.fullmatch(block.strip())
            if not second or second.group(1).strip().lower() == "notes":
                transformed.append(block.rstrip())
                continue

            title = second.group(1).strip()
            numbered = NUMBERED_SECOND_HEADING.fullmatch(title)
            if numbered:
                title = numbered.group(1)
            global_number += 1
            transformed.append(f"## {global_number}. {title}")

        path.write_text("\n\n".join(transformed).rstrip() + "\n", encoding="utf-8")

    print(f"Renumbered {global_number} pieces across {len(files)} Sections.")


def transform(apply: bool) -> None:
    all_blocks, prose, internal_headings = inventory()
    candidates = [item for item in prose if item.split_at is not None]
    target = min(round(len(prose) * 0.5), len(candidates))
    selected = evenly_distributed(candidates, target)

    print(f"Sections: {len(all_blocks)}")
    print(f"Numbered pieces: {internal_headings}")
    print(f"Body prose paragraphs before: {len(prose)}")
    print(f"Splittable body paragraphs: {len(candidates)}")
    print(f"Paragraphs selected for splitting: {len(selected)}")
    print(f"Body prose paragraphs after: {len(prose) + len(selected)}")
    if prose:
        print(f"Paragraph ratio: {(len(prose) + len(selected)) / len(prose):.3f}x")

    if not apply:
        return

    first_heading = next(iter(all_blocks.values()))[0].strip()
    if first_heading.startswith("# Section "):
        raise SystemExit("The fast-flow hierarchy has already been applied.")

    global_number = 0
    prose_by_location = {(item.file, item.block_index): item for item in prose}

    for path, blocks in all_blocks.items():
        transformed: list[str] = []

        for block_index, block in enumerate(blocks):
            stripped = block.strip()
            top = TOP_HEADING.fullmatch(stripped)
            if top:
                transformed.append(f"# Section {top.group(1)}: {top.group(2)}")
                continue

            second = SECOND_HEADING.fullmatch(stripped)
            if second and second.group(1).strip().lower() != "notes":
                global_number += 1
                transformed.append(f"## {global_number}. {second.group(1)}")
                continue

            location = (path, block_index)
            prose_block = prose_by_location.get(location)
            if location in selected and prose_block and prose_block.split_at is not None:
                edge = prose_block.split_at
                transformed.append(
                    wrapped(section_reference_language(prose_block.text[:edge]))
                )
                transformed.append(
                    wrapped(section_reference_language(prose_block.text[edge:]))
                )
            else:
                transformed.append(section_reference_language(block.rstrip()))

        path.write_text("\n\n".join(transformed).rstrip() + "\n", encoding="utf-8")

    if global_number != internal_headings:
        raise SystemExit(
            f"Numbered {global_number} pieces but expected {internal_headings}."
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group()
    action.add_argument(
        "--apply",
        action="store_true",
        help="rewrite the manuscript; without this flag only report counts",
    )
    action.add_argument(
        "--renumber",
        action="store_true",
        help="renumber all existing or newly inserted second-level pieces",
    )
    args = parser.parse_args()
    if args.renumber:
        renumber_numbered_pieces()
    else:
        transform(apply=args.apply)


if __name__ == "__main__":
    main()
