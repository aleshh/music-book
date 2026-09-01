# Building the Book

Run this from the project directory:

```sh
make book
```

That builds both editions:

- `output/pdf/ambient-and-minimalist-music.pdf`
- `output/epub/ambient-and-minimalist-music.epub`

You can also run `make pdf`, `make epub`, or `make clean`.

For the paperback production pair, run:

```sh
make paperback
```

This rebuilds the interior PDF, reads its final page count, and creates the
matching full-wrap cover at
`output/pdf/ambient-and-minimalist-music-paperback-cover.pdf`. To regenerate
only the cover from an already-current interior, run `make paperback-cover`.
The cover assumes black ink on cream paper; edit `cover/full-wrap.json` to
change its copy or production inputs.

To report the manuscript count without rebuilding anything, run:

```sh
make word-count
```

This reports a full reader-facing count and a stable core-Section count, both
excluding generated `N.` heading labels, plus their literal Markdown-source
counts. The full count includes the Foreword, Introduction, usage note, twelve
Sections, diagnostic index, and author note; it excludes title and publication
data and cover copy. Counts include headings, exercises, notes, and source
URLs. The script also reports average, median, population standard deviation,
quartile range, 90th percentile, and full range for body-prose sentence length
in the twelve Sections. Sentence statistics exclude headings, source notes,
and footnote markers so citations and URLs do not distort the prose
measurements.

## Requirements

- Pandoc 3 or newer
- Google Chrome or Chromium for PDF rendering
- Python 3 with `pypdf` and `reportlab` for deterministic Section-page checks
  and final physical-page folios
- `make` and Bash

The script looks for Chrome in its standard macOS and command-line locations.
If yours is elsewhere, run:

```sh
CHROME_BIN="/path/to/chrome" make pdf
```

The build automatically checks `PYTHON_BIN`, the system `python3`, and the
Python runtime bundled with Codex. If none can import `pypdf` and `reportlab`,
install them into the Python environment used by the build or point the build
at another interpreter:

```sh
python3 -m pip install pypdf reportlab
PYTHON_BIN="/path/to/python3" make pdf
```

## What gets included

Every file matching `chapters/[0-9][0-9]-*.md` is included in filename order.
Despite the historical directory name, each file is now one reader-facing
Section. Second-level headings are short pieces numbered globally without a
categorical label. Section notes are kept with their Section and restart at 1;
the Markdown files themselves are not modified during a build.

The EPUB is split at heading level 2, so each numbered piece is packaged as its
own document. This produces a reliable page transition even in readers that
ignore CSS page-break requests.

After inserting, deleting, or moving a numbered piece, renumber the sequence:

```sh
python3 scripts/restructure-fast-flow.py --renumber
```

## Formatting controls

- Edit `book.yaml` for the title, subtitle, language, and other book metadata.
- Edit `frontmatter/publication.md` for the publication statement and the scope
  of the publisher's copyright claim. Declare AI-generated content in KDP's
  publishing workflow rather than adding a separate legalistic notice here.
- Edit `frontmatter/foreword.md` for Alesh Houdek's Foreword and
  `frontmatter/introduction.md` for the collaboratively developed Introduction.
  `frontmatter/how-to-use-this-book.md` follows them and explains the book's
  sequential and problem-led reading modes. They appear in that order after the
  contents and before Section 1. Each starts on a new page, but its heading and
  opening text share that page.
- Edit `backmatter/when-the-piece-stops-moving.md` for the diagnostic index and
  36 interventions. It follows Section 12.
- Edit `backmatter/about-the-authorial-voice.md` for the closing "About the author" explanation of
  the generated Romanovský persona. It follows the diagnostic index.
- Edit `styles/base.css` for the body and heading fonts, type size, leading,
  colors, paragraph indents, and shared typography.
- Edit `styles/pdf.css` for the PDF page size, margins, title page, contents,
  page numbers, Section divider pages, numbered-piece starts, and print-specific
  spacing.
- Edit `styles/epub.css` for EPUB-only layout choices.

The PDF is designed as a 4.25 by 7 inch, no-bleed paperback interior. It uses
mirrored margins: 0.625 inch at the binding edge, 0.375 inch outside, 0.48 inch
above, and 0.54 inch below. Body copy is 9.25 point Adobe Caslon Pro when that
font is installed, with Cooper Hewitt for headings. Long source URLs are
allowed to wrap so they cannot make the browser shrink the rest of the page.

The compact PDF layout lets numbered pieces follow one another instead of
forcing each one onto a new page. Every Section receives one divider page with
only its small bold label and left-aligned title; the opening
numbered piece begins on the immediately following page, without an inserted blank verso. The build
finishes with `scripts/ensure-print-spreads.py`, which applies the final physical
page numbers and verifies every Section transition.

The title page identifies Jonathan Romanovský as a generated authorial persona,
credits the book's development and editing to Alesh Houdek, and credits his
Foreword.
The following publication page names Alesh Houdek as self-publisher and states
the scope of his copyright claim. The Introduction gives the reader a plain
account of the book's human-AI collaboration.

Body paragraphs are set without vertical space between them. The first
paragraph of each numbered piece is flush left; subsequent body paragraphs are
indented. Block quotations, lists, and notes remain flush left. Reader-facing
Section, piece, and exercise headings use sentence case.

This is a custom KDP paperback trim within the regular-trim range. Before
upload, compare the final page count with KDP's current inside-margin table;
books above 500 pages require at least a 0.75 inch inside margin. The current
317-page build requires 0.625 inch inside, so the current setting meets the
requirement and remains sufficient through 500 pages. For a tactile pocket-
guide feel, black ink on cream paper with a matte cover is the working
production assumption. EPUB readers often let readers override fonts, size,
color, and spacing, so EPUB typography remains intentionally less rigid.

To use a font file you are licensed to distribute, create a `fonts/` directory
and add an `@font-face` rule near the top of `styles/base.css`, for example:

```css
@font-face {
  font-family: "My Book Serif";
  font-style: normal;
  font-weight: 400;
  src: url("../fonts/MyBookSerif-Regular.otf");
}
```

Then put `"My Book Serif"` first in `--book-serif`. Referenced font resources
are embedded in the generated formats. Do not add font files to the repository
unless their license permits embedding and distribution.
