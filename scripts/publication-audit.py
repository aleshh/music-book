#!/usr/bin/env python3
"""Run deterministic publication checks on the manuscript and built EPUB."""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHAPTER_DIR = PROJECT_ROOT / "chapters"
EPUB_PATH = PROJECT_ROOT / "output" / "epub" / "Ambient and Minimalist Music.epub"
EXPECTED_TITLE = "Ambient and Minimalist Music"
EXPECTED_AUTHOR = "Jonathan Romanovský"
EXPECTED_IDENTIFIER = "urn:uuid:6571744f-18c0-4cfe-8305-f86a7b7291d8"
URL = re.compile(r"https?://[^ )>\"`]+")
PIECE = re.compile(r"^## (\d+)\. ", re.MULTILINE)
SECTION = re.compile(r"^# Section (\d+): ", re.MULTILINE)
FOOTNOTE_DEFINITION = re.compile(r"^\[\^([^\]]+)\]:", re.MULTILINE)
FOOTNOTE_REFERENCE = re.compile(r"\[\^([^\]]+)\]")


class Audit:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.details: list[str] = []

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.failures.append(message)

    def detail(self, message: str) -> None:
        self.details.append(message)


def footnote_sets(text: str) -> tuple[set[str], set[str]]:
    definitions = set(FOOTNOTE_DEFINITION.findall(text))
    references: set[str] = set()
    for line in text.splitlines():
        if re.match(r"^\[\^[^\]]+\]:", line):
            continue
        references.update(FOOTNOTE_REFERENCE.findall(line))
    return references, definitions


def audit_manuscript(audit: Audit) -> None:
    chapters = sorted(CHAPTER_DIR.glob("[0-9][0-9]-*.md"))
    audit.require(len(chapters) == 12, f"expected 12 Section files, found {len(chapters)}")
    texts = [path.read_text(encoding="utf-8") for path in chapters]
    manuscript = "\n".join(texts)
    sections = [int(value) for value in SECTION.findall(manuscript)]
    pieces = [int(value) for value in PIECE.findall(manuscript)]
    audit.require(sections == list(range(1, 13)), "Section numbering is incomplete")
    audit.require(pieces == list(range(1, 166)), "piece numbering is not contiguous 1-165")

    source_files = [
        PROJECT_ROOT / "frontmatter" / "introduction.md",
        PROJECT_ROOT / "frontmatter" / "how-to-use-this-book.md",
        *chapters,
    ]
    footnote_total = 0
    url_total: set[str] = set()
    for path in source_files:
        text = path.read_text(encoding="utf-8")
        references, definitions = footnote_sets(text)
        audit.require(
            references == definitions,
            f"footnote mismatch in {path.relative_to(PROJECT_ROOT)}: "
            f"missing={sorted(references - definitions)}, "
            f"unused={sorted(definitions - references)}",
        )
        footnote_total += len(definitions)
        url_total.update(value.rstrip(".,;:") for value in URL.findall(text))

    for chapter in chapters:
        stem = chapter.stem
        ledger = PROJECT_ROOT / "chapter-notes" / f"{stem}-source-ledger.md"
        audit.require(ledger.exists(), f"missing source ledger: {ledger.name}")

    publication = (PROJECT_ROOT / "frontmatter" / "publication.md").read_text(
        encoding="utf-8"
    )
    audit.require("Self-published by" not in publication, "obsolete self-published line remains")
    audit.detail(f"12 Sections; 165 numbered pieces")
    audit.detail(f"{footnote_total} resolved source notes; {len(url_total)} unique source URLs")


def audit_epub(audit: Audit) -> None:
    audit.require(EPUB_PATH.exists(), f"missing built EPUB: {EPUB_PATH.relative_to(PROJECT_ROOT)}")
    if not EPUB_PATH.exists():
        return

    with zipfile.ZipFile(EPUB_PATH) as archive:
        bad_member = archive.testzip()
        audit.require(bad_member is None, f"corrupt EPUB member: {bad_member}")
        members = archive.infolist()
        audit.require(bool(members), "EPUB archive is empty")
        if members:
            audit.require(members[0].filename == "mimetype", "EPUB mimetype is not first")
            audit.require(
                members[0].compress_type == zipfile.ZIP_STORED,
                "EPUB mimetype must be stored without compression",
            )
            audit.require(
                archive.read("mimetype") == b"application/epub+zip",
                "EPUB mimetype has the wrong value",
            )
        for member in members:
            if member.filename.lower().endswith((".xhtml", ".opf", ".ncx", ".svg")):
                try:
                    ElementTree.fromstring(archive.read(member.filename))
                except ElementTree.ParseError as error:
                    audit.require(False, f"malformed XML in {member.filename}: {error}")
        opf = ElementTree.fromstring(archive.read("EPUB/content.opf"))
        ns = {
            "opf": "http://www.idpf.org/2007/opf",
            "dc": "http://purl.org/dc/elements/1.1/",
        }
        titles = [node.text for node in opf.findall(".//dc:title", ns)]
        creators = [node.text for node in opf.findall(".//dc:creator", ns)]
        identifiers = [node.text for node in opf.findall(".//dc:identifier", ns)]
        cover_items = [
            node
            for node in opf.findall(".//opf:manifest/opf:item", ns)
            if "cover-image" in node.attrib.get("properties", "").split()
        ]
        audit.require(titles == [EXPECTED_TITLE], f"unexpected EPUB titles: {titles}")
        audit.require(creators == [EXPECTED_AUTHOR], f"unexpected EPUB creators: {creators}")
        audit.require(EXPECTED_IDENTIFIER in identifiers, "stable EPUB identifier is missing")
        audit.require(len(cover_items) == 1, f"expected one EPUB cover image, found {len(cover_items)}")
        if cover_items:
            href = cover_items[0].attrib["href"]
            audit.require(f"EPUB/{href}" in archive.namelist(), f"missing embedded cover: {href}")
    audit.detail(
        "EPUB title, author, identifier, cover declaration, package structure, "
        "XML, and archive integrity verified"
    )


def main() -> None:
    audit = Audit()
    audit_manuscript(audit)
    audit_epub(audit)
    if audit.failures:
        for failure in audit.failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        raise SystemExit(1)
    for detail in audit.details:
        print(f"PASS: {detail}")


if __name__ == "__main__":
    main()
