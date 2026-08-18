# Building the Book

Run this from the project directory:

```sh
make book
```

That builds both editions:

- `output/pdf/ambient-and-minimalist-music.pdf`
- `output/epub/ambient-and-minimalist-music.epub`

You can also run `make pdf`, `make epub`, or `make clean`.

To report the manuscript count without rebuilding anything, run:

```sh
make word-count
```

This reports a stable editorial count that excludes generated `N.` heading
labels, plus the literal Markdown-source count. Both include headings,
exercises, notes, and source URLs. It also reports average, median, population
standard deviation, quartile range, 90th percentile, and full range for body-
prose sentence length. Sentence statistics exclude headings, source notes, and
footnote markers so citations and URLs do not distort the prose measurements.

## Requirements

- Pandoc 3 or newer
- Google Chrome or Chromium for PDF rendering
- `make` and Bash

The script looks for Chrome in its standard macOS and command-line locations.
If yours is elsewhere, run:

```sh
CHROME_BIN="/path/to/chrome" make pdf
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

The compact layout lets numbered pieces follow one another instead of forcing
each one onto a new page. Each Section still begins on a new page, but its
opening piece follows the Section title rather than occupying another sheet.

This is a custom KDP paperback trim within the regular-trim range. Before
upload, compare the final page count with KDP's current inside-margin table;
books above 500 pages require at least a 0.75 inch inside margin. The current
290-page build requires only 0.5 inch inside, so the 0.625 inch setting leaves
comfortable binding clearance and remains sufficient through 500 pages. For a
tactile pocket-guide feel, black ink on cream paper with a matte cover is the
working production assumption. EPUB readers often let readers override fonts,
size, color, and spacing, so EPUB typography remains intentionally less rigid.

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
