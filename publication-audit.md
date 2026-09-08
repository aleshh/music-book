# Publication audit

Audit date: September 1, 2026

This is editorial and production documentation. It is not included in the
reader-facing book and is not legal advice.

## Conclusion

The manuscript has a complete recoverable source trail and no identified
quotation, image, or font problem that should prevent publication. The
remaining publication tasks are production checks and KDP form entries, not
missing research.

The most important factual anecdotes have already been handled with the right
qualifications: Takemitsu's wartime recollection does not identify a disputed
singer; the Satie event paraphrases rather than dramatizes uncertain shouted
phrases; Cage's anechoic-chamber story is not treated as a single origin; the
Eno harp-and-rain story names the disagreement about who set the level; the
Scelsi and Eastman accounts preserve authorship and transmission disputes; and
the *Oblique Strategies* quotations are not assigned to one physical edition.

## Source-trail audit

- All twelve Sections have a dedicated source ledger.
- The Introduction and “How to use this book” have separate source ledgers.
- The reader-facing source-bearing files contain 109 resolved notes and 143
  unique external source URLs. No footnote reference lacks a definition, and
  no definition is unused.
- Factual prose distinguishes primary testimony, later recollection, scholarly
  reconstruction, institutional work data, and the book's own musical
  analysis.
- Central claims were spot-checked again against live versions of sources for
  Takemitsu, Cage, Satie, Eno and Judy Nylon, Oliveros, Eno and Peter Schmidt,
  Patrick Shiroishi, Julius Eastman, Morton Feldman, Arvo Pärt, John Luther
  Adams, and Gavin Bryars.
- The archived 1997 DJ Shadow interview intermittently times out when fetched
  directly, but remains indexed with the relevant first-person passages. Its
  account of the approximately sixteen fragments in “The Number Song” is also
  consistent with the manuscript's more general, independently accessible DJ
  Shadow sources. Retain the full bibliographic description rather than
  relying on the URL alone.

The deterministic portion of this audit can be repeated with `make audit`
after `make epub`.

## Quotation and text-rights audit

No external source is quoted at length. The attributable prose excerpts are
brief and used for criticism or explanation rather than as decoration or a
substitute for the originals. They include short phrases from Brian Eno,
Morton Feldman, Roscoe Mitchell, and Pauline Oliveros, plus three *Oblique
Strategies* cards totaling fifteen words. The book does not reproduce song
lyrics, a score, a card set, an interview, or another author's sustained prose.

The Foreword's block quotation reproduces Alesh Houdek's own initiating prompt.
Invented score instructions elsewhere in the book are the manuscript's own
examples, not unattributed quotations.

The current publication statement claims Alesh Houdek's copyright only in the
Foreword, original human-authored revisions, and the selection, coordination,
and arrangement of the edition. It does not make an undifferentiated claim over
machine-generated prose.

## Image and font-rights audit

- The selected cover art was generated for this project and uses no imported
  photograph, illustration, logo, or other third-party visual asset.
- The five interior diagrams were created for this manuscript. They are
  monochrome, described in text, and do not reproduce copyrighted notation or
  diagrams from a source.
- No font file is distributed inside the EPUB. The build requests local system
  fonts for rendering and falls back to standard fonts; it does not place a
  third-party font file in the publication package.
- KDP should be told that both text and cover art contain AI-generated content
  when its setup form asks. That platform disclosure is separate from the
  book's reader-facing account of the collaboration.

## Current publication identity

- **Title:** *Ambient and Minimalist Music*
- **Subtitle:** *A Composer's Field Guide*
- **Author:** Jonathan Romanovský
- **Author status:** a generated authorial persona, explained in the
  Introduction and “About the author”
- **Development and editing:** Alesh Houdek
- **Foreword:** Alesh Houdek
- **Edition:** first edition, 2026
- **Language:** English (United States)
- **Stable EPUB identifier:**
  `urn:uuid:6571744f-18c0-4cfe-8305-f86a7b7291d8`
- **Paperback format:** 4.25 by 7 inches, no-bleed black interior on cream
  paper; full-color matte cover is the working specification
- **Copyright statement:** scoped as described above

The ISBN/imprint choice, list price, sales territories, categories, keywords,
and final store description are not encoded in the manuscript repository.
Those remain KDP listing decisions. If a free KDP ISBN is used, Amazon supplies
the associated “Independently published” imprint; an owned ISBN permits a
publisher/imprint chosen by its registrant.

## Production checks completed

- The EPUB filename now preserves the title's capitalization and spaces.
- The EPUB metadata contains one title, one author, the stable identifier, and
  the scoped rights statement.
- The EPUB contains a front-only RGB cover and marks it as the cover image in
  both modern and legacy metadata.
- The experimental SVG diagrams were removed after editorial review; the
  reader-facing manuscript contains no third-party visual assets.
- The listening paths and composer/work finder appear in the EPUB navigation.

The final print proof should be made only after the interior page count is
frozen, because the full-wrap paperback spine is derived from that count.
