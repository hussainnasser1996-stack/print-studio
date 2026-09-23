# Aesthetic Direction — Editorial / Magazine

Reference exemplars: FT Weekend, The Economist briefing pages, Bloomberg Businessweek features, Stripe Press, MIT Technology Review.

Use this for: long-form briefings, sector deep-dives, thoughtful research notes, anything where the reader will spend more than 60 seconds on a page.

## Typography

```css
:root {
  --font-display: "Fraunces", "Tiempos Headline", "Playfair Display", Georgia, serif;
  --font-body:    "Source Serif 4", "Charter", "Iowan Old Style", Georgia, serif;
  --font-mono:    "JetBrains Mono", "IBM Plex Mono", "Berkeley Mono", monospace;
}
```

- **Display (headlines, hero):** serif with character — Fraunces is the primary choice; vary across documents.
- **Body:** serif with strong x-height for legibility at small print sizes.
- **Sizes:** display 28–48pt, section heads 14–18pt, body 9–10pt, footnotes 7pt.
- **Line height:** 1.45 for body (loose, magazine-feel), 1.1 for display.
- **No italics on entire paragraphs.** Italics for emphasis or pull-quotes only.

## Color palette

```css
:root {
  --ink:          #0F0F0E;   /* near-black, body text */
  --paper:        #FBFAF6;   /* warm off-white, page background */
  --rule:         #1F1F1E;   /* hairline rules + key elements */
  --accent:       #B5402A;   /* one bold accent — restrained use */
  --muted:        #6B6B68;   /* metadata, captions, footnotes */
  --highlight:    #F4E9C9;   /* subtle paper-highlight for callouts */
}
```

- Dominant: ink on paper.
- Accent (`--accent`): use ONCE per page max — for the strongest callout, not for general headers.
- Backgrounds: warm paper, not pure white. Pure `#FFFFFF` reads as web/AI-generic.
- Avoid: cool grays, navy headers, teal accents.

## Spatial composition

- **Strong typographic hierarchy** carries the page. Reduce decorative chrome.
- **Hairline rules** (1px solid `--rule`) separate sections — never colored boxes or background fills.
- **Two-column body** for long-form prose; one-column for KPI rows or charts.
- **Pull-quote treatment** for the single most important sentence on the page: larger display font, accent color, hangs in the margin or breaks the column grid.
- **Drop caps** acceptable on the lead paragraph — large display character, 2-3 lines deep.
- **Generous outer margins** (15–20mm). Content density comes from typography, not edge-to-edge bleeds.

## Visual details

- Charts: minimal — no gridlines, no borders, light tick marks, labels in `--muted`. Single accent color for the data series that matters most; everything else in `--ink` or `--muted`.
- Tables: hairline horizontal rules only, no vertical lines, no zebra-striping. Numerals in tabular figures (`font-variant-numeric: tabular-nums`).
- Footnotes: numbered, set in `--font-mono` at 7pt, hangs in the bottom margin.
- Page numbers + section titles in a thin running-head row, set in `--muted`.

## Anti-patterns to avoid

- Boxed callouts with rounded corners and colored backgrounds (web-app default).
- Flat-color section headers with white text.
- Gridded layouts where every cell has equal weight.
- More than one accent color.
- Sans-serif body — defeats the purpose.
