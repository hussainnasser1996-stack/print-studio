# Aesthetic Direction — Institutional / Classic

The original Reusable PDF Builder Prompt's default. Reference exemplars: bulge-bracket bank pitch books, IC memos, standard term-sheet summaries, Citi/JPM client decks.

Use this for: standard IC memos, term-sheet summaries, deal documents going to institutional LPs, anything where "looking like a real bank doc" is the goal and distinctiveness is not. **This is the safe default — pick another direction if the doc has any room for character.**

## Typography

```css
:root {
  --font-display: "Inter", "Söhne", -apple-system, "Helvetica Neue", sans-serif;
  --font-body:    "Inter", -apple-system, "Helvetica Neue", "Arial", sans-serif;
  --font-mono:    "JetBrains Mono", "Source Code Pro", "Consolas", monospace;
}
```

- **Display + body:** Inter throughout (or system stack). This is the one direction where Inter for everything is acceptable — it's the institutional default by design.
- **Sizes:** display 18–24pt, section heads 11pt bold, body 9pt, footnotes 7pt.
- **Weights:** 400 body, 600 section heads, 700 hero only. Avoid 800/900.
- **Line height:** 1.4 body, 1.2 display.
- **Tabular figures** everywhere there's a number.

## Color palette

```css
:root {
  --navy:       #0B2A4A;   /* dark navy — primary brand color, headers */
  --teal:       #14B8A6;   /* teal accent — KPIs, callouts */
  --gold:       #D4A017;   /* gold highlight — top-line metrics */
  --ink:        #111827;   /* body text */
  --grey-50:    #F9FAFB;   /* page bg or alt-row fill */
  --grey-100:   #F3F4F6;   /* light row fills */
  --grey-300:   #D1D5DB;   /* rules and borders */
  --grey-600:   #4B5563;   /* metadata, secondary text */
  --paper:      #FFFFFF;   /* page background */
}
```

- Dominant: ink on white.
- Navy: header bars, hero backgrounds, table-header fills.
- Teal: KPI tile accents, chart highlight series, callout borders.
- Gold: the single most important number on the page (deal size, revenue, IRR).
- Light grey: zebra-stripe alternate table rows.

## Spatial composition

- **Grid-based.** A clear 12-column grid; KPI rows of 3 or 4 equal tiles.
- **Hero header bar** in navy across the page top, with company name + confidentiality line in white.
- **Sub-bar of deal terms** beneath the hero — light grey fill, key-value pairs in 2 or 3 rows.
- **Section headers** in navy with a teal underline rule.
- **Table-driven body.** Density is fine; this is what institutional readers expect.
- **Footer:** page number + footnote source citations.

## Visual details

- Charts: clean axes, gridlines acceptable but light, navy + teal as the two-series default. Add gold for the highlighted data point.
- Tables: navy header row with white text, alternating grey-50 rows, right-aligned numerics.
- KPI tiles: light grey fill with a teal left border, large gold number, label below in `--grey-600`.
- Callouts: light grey fill, teal left border (4px), no rounded corners or 1px radius max.

## Anti-patterns to avoid (still apply)

- Drop shadows beyond a soft 1-2px on KPI tiles.
- Rounded corners > 4px.
- More than 3 colors on the same page.
- Decorative chrome (icons inside KPI tiles, illustrative graphics).

## When to NOT use this

If you have any room for character at all, pick another direction. This is the safe default for when the audience expects "bank deck" and nothing more interesting is appropriate.
