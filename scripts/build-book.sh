#!/usr/bin/env bash

set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

output_stem="ambient-and-minimalist-music"
pdf_output="output/pdf/${output_stem}.pdf"
pdf_raw="tmp/pdfs/${output_stem}-chrome.pdf"
epub_output="output/epub/${output_stem}.epub"
pdf_html="tmp/pdfs/${output_stem}.html"
publication_html="tmp/pdfs/publication.html"
publication_source="frontmatter/publication.md"
foreword_source="frontmatter/foreword.md"
introduction_source="frontmatter/introduction.md"
how_to_use_source="frontmatter/how-to-use-this-book.md"
interventions_source="backmatter/when-the-piece-stops-moving.md"
about_source="backmatter/about-the-authorial-voice.md"
chrome_log="tmp/pdfs/chrome.log"

die() {
  printf 'build-book: %s\n' "$1" >&2
  exit 1
}

need_command() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

find_chrome() {
  if [[ -n "${CHROME_BIN:-}" && -x "$CHROME_BIN" ]]; then
    printf '%s\n' "$CHROME_BIN"
    return
  fi

  local candidate
  for candidate in \
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    "/Applications/Chromium.app/Contents/MacOS/Chromium"; do
    if [[ -x "$candidate" ]]; then
      printf '%s\n' "$candidate"
      return
    fi
  done

  for candidate in google-chrome chromium chromium-browser; do
    if command -v "$candidate" >/dev/null 2>&1; then
      command -v "$candidate"
      return
    fi
  done

  die "PDF output needs Google Chrome or Chromium; set CHROME_BIN to its executable"
}

find_pdf_python() {
  local candidate

  if [[ -n "${PYTHON_BIN:-}" ]]; then
    candidate="$PYTHON_BIN"
    if [[ -x "$candidate" ]] && "$candidate" -c 'import pypdf, reportlab' >/dev/null 2>&1; then
      printf '%s\n' "$candidate"
      return
    fi
  fi

  if command -v python3 >/dev/null 2>&1; then
    candidate="$(command -v python3)"
    if "$candidate" -c 'import pypdf, reportlab' >/dev/null 2>&1; then
      printf '%s\n' "$candidate"
      return
    fi
  fi

  if [[ -n "${HOME:-}" ]]; then
    candidate="${HOME}/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
    if [[ -x "$candidate" ]] && "$candidate" -c 'import pypdf, reportlab' >/dev/null 2>&1; then
      printf '%s\n' "$candidate"
      return
    fi
  fi

  die "PDF finalization needs Python 3 with pypdf and reportlab; set PYTHON_BIN or install both"
}

shopt -s nullglob
chapter_files=(chapters/[0-9][0-9]-*.md)
(( ${#chapter_files[@]} > 0 )) || die "no numbered Markdown files found in chapters/"

common_args=(
  --from=markdown+smart
  --standalone
  --file-scope
  --metadata-file=book.yaml
  --lua-filter=filters/chapter-notes.lua
  --lua-filter=filters/section-headings.lua
  --resource-path=".:styles:fonts"
  --section-divs
  --toc
  --toc-depth=2
  --top-level-division=part
)

build_pdf() {
  need_command pandoc
  local chrome_bin
  chrome_bin="$(find_chrome)"
  local pdf_python
  pdf_python="$(find_pdf_python)"

  mkdir -p output/pdf tmp/pdfs

  pandoc \
    --from=markdown+smart \
    --to=html5 \
    --output="$publication_html" \
    "$publication_source"

  pandoc \
    "${common_args[@]}" \
    --to=html5 \
    --template=templates/pdf.html \
    --include-before-body="$publication_html" \
    --css=styles/base.css \
    --css=styles/pdf.css \
    --embed-resources \
    --output="$pdf_html" \
    "$foreword_source" \
    "$introduction_source" \
    "$how_to_use_source" \
    "${chapter_files[@]}" \
    "$interventions_source" \
    "$about_source"

  local chrome_profile
  chrome_profile="$(mktemp -d /tmp/ambient-book-chrome.XXXXXX)"
  trap 'rm -rf -- "$chrome_profile"' RETURN

  local chrome_status=0
  "$chrome_bin" \
    --headless=new \
    --disable-gpu \
    --disable-extensions \
    --no-pdf-header-footer \
    --user-data-dir="$chrome_profile" \
    --print-to-pdf="$project_root/$pdf_raw" \
    "file://$project_root/$pdf_html" >"$chrome_log" 2>&1 || chrome_status=$?

  rm -rf -- "$chrome_profile"
  trap - RETURN

  if (( chrome_status != 0 )); then
    sed -n '1,120p' "$chrome_log" >&2
    die "Chrome PDF rendering failed with status $chrome_status"
  fi

  [[ -s "$pdf_raw" ]] || die "Chrome did not create $pdf_raw"

  "$pdf_python" scripts/ensure-print-spreads.py \
    --expected-count="${#chapter_files[@]}" \
    "$pdf_raw" \
    "$pdf_output"

  [[ -s "$pdf_output" ]] || die "PDF finalization did not create $pdf_output"
  printf 'Built %s\n' "$pdf_output"
}

build_epub() {
  need_command pandoc
  mkdir -p output/epub

  pandoc \
    "${common_args[@]}" \
    --to=epub3 \
    --split-level=2 \
    --css=styles/base.css \
    --css=styles/epub.css \
    --output="$epub_output" \
    "$publication_source" \
    "$foreword_source" \
    "$introduction_source" \
    "$how_to_use_source" \
    "${chapter_files[@]}" \
    "$interventions_source" \
    "$about_source"

  [[ -s "$epub_output" ]] || die "Pandoc did not create $epub_output"
  printf 'Built %s\n' "$epub_output"
}

clean_outputs() {
  rm -rf -- output tmp/pdfs
  printf 'Removed generated output and PDF intermediates\n'
}

case "${1:-book}" in
  book|all)
    build_pdf
    build_epub
    ;;
  pdf)
    build_pdf
    ;;
  epub)
    build_epub
    ;;
  clean)
    clean_outputs
    ;;
  *)
    die "usage: $0 [book|pdf|epub|clean]"
    ;;
esac
