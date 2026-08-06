# Building the Book

Run this from the project directory:

```sh
make book
```

That builds both editions:

- `output/pdf/ambient-and-minimalist-music.pdf`
- `output/epub/ambient-and-minimalist-music.epub`

You can also run `make pdf`, `make epub`, or `make clean`.

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
This means drafted chapters build correctly even while some chapter numbers are
still missing. Chapter footnotes are kept with their chapter and restart at 1;
the Markdown files themselves are not modified.

## Formatting controls

- Edit `book.yaml` for the title, subtitle, language, and other book metadata.
- Edit `styles/base.css` for the body and heading fonts, type size, leading,
  colors, paragraph indents, and shared typography.
- Edit `styles/pdf.css` for the PDF page size, margins, title page, contents,
  page numbers, and print-specific spacing.
- Edit `styles/epub.css` for EPUB-only layout choices.

The default PDF trim size is 6 by 9 inches. EPUB readers often let readers
override fonts, size, color, and spacing, so EPUB typography is intentionally
less rigid.

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
