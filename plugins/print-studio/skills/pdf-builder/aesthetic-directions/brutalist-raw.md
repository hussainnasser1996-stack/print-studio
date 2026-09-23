# Aesthetic Direction — Brutalist / Raw

Reference exemplars: Bloomberg Terminal printouts, raw research notes from Hindenburg / Muddy Waters, Wikileaks docs, technical white papers, dense academic preprints.

Use this for: contrarian research, diligence packs, technical deep-dives, anything where the message is "we did the work, here's the data, draw your own conclusions" — and visual polish would undercut credibility.

## Typography

```css
:root {
  --font-display: "JetBrains Mono", "Berkeley Mono", "IBM Plex Mono", "Courier New", monospace;
  --font-body:    "IBM Plex Sans", "Söhne", "Inter", -apple-system, sans-serif;
  --font-mono:    "JetBrains Mono", "Berkeley Mono", "IBM Plex Mono", monospace;
}
```

- **Display:** monospace. Headers, hero, KPI numbers — all monospace.
- **Body:** geometric sans, neutral, tight.
- **Sizes:** display 16–22pt mono, section heads 10pt mono uppercase, body 9pt sans, footnotes 7pt mono.
- **Letter-spacing:** zero or slightly negative on display. Section heads in uppercase with `letter-spacing: 0.05em`.
- **Weights:** 400 body, 600 headers. Avoid bold beyond that.
- **Line height:** 1.35 body, 1.0 display (tight).

## Color palette

```css
:root {
  --ink:       #000000;     /* pure black */
  --paper:     #FFFFFF;     /* pure white */
  --rule:      #000000;     /* hard black rules */
  --highlight: #FFFF00;     /* hi-vis yellow — single-use only */
  --warn:      #FF3B30;     /* alert red — single-use only */
  --grid:      #E5E5E5;     /* subtle grid lines if needed */
  --muted:     #666666;     /* metadata, citations */
}
```

- Dominant: pure black on pure white. No off-whites, no warm tones.
- Highlight (`--highlight`): yellow marker treatment for the single most important number/claim per page. Use `<mark>` or background fills.
- Warn red: only for negative deltas, downside scenarios, contrarian flag elements. Once per page max.
- Avoid: any blues, greens, or "professional" colors.

## Spatial composition

- **Hard rules.** 2px solid black borders separating sections. No soft greys.
- **Grid-based but dense.** 12-column grid, narrow gutters, content packed against the rules.
- **Asymmetric weight.** A monospace data dump in one column, sparse callouts in the next — deliberate inconsistency.
- **No rounded corners. Anywhere.** All rectangles have 0 radius.
- **No shadows. No gradients. No fills beyond the highlight color.**
- **Marginal annotations.** Footnote refs in the right margin in mono, like a code review.

## Visual details

- Charts: black lines on white, mono labels, no gridlines or minimal `--grid` ticks. Highlight color for the one data series that matters. Axes are black solid 1.5px.
- Tables: hard black 2px outer border, 1px black inner rules, mono numerics in tabular figures, no zebra-striping. Dense.
- Headers: SECTION HEADERS IN ALL CAPS MONO with a 2px black rule underneath that spans the full column width.
- KPI treatment: large mono number, label in mono uppercase below, single yellow highlight for the headline metric.
- Footer: page number + run-time stamp, mono, justified.

## Specific elements

- **"REDACTED" or "CONFIDENTIAL" stamps** can be placed as visible elements (uppercase mono, red, rotated 0 — not 45° because that's web-design cliché).
- **Annotations**: any commentary or analyst-overlay is set in mono italic with a `>` prefix in the margin, like a comment block.
- **Numerical formatting**: explicit decimals, no rounding in tables, asterisks for source citations linking to a numbered footnote section.

## Anti-patterns to avoid

- Anything that looks like a startup pitch deck.
- Soft colors.
- Rounded corners.
- Drop shadows.
- Gradients.
- Decorative icons.
- Whitespace as breathing room — density is the point.
