# Investor teaser sample: Halcyon Cold Chain (fictional)

A two-page Series B teaser built with **pdf-builder** in the `editorial-magazine` direction.

- `build.py` holds the single source of truth: revenue, margins, raise and use of funds.
  The charts, tables and prose placeholders are all generated from it, and the script
  fails if the use of funds doesn't add up to the raise.
- `teaser.template.html` is the layout. `build.py` inlines the bundled fonts as base64 and
  writes `teaser.html` (git-ignored), then prints it to PDF with headless Chrome or Edge.

```bash
python3 build.py      # → Halcyon-Series-B-Teaser.pdf
```

Measured checks on the shipped PDF: 2 pages authored and 2 rendered; trailing space
of 9.6% and 1.5% of page height; no boxes overlapping the footer; legal text present in full.
