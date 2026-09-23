# Aesthetic Direction — Modern Minimal

Reference exemplars: Linear changelog pages, Notion product reports, Vercel pricing/spec pages, modern fintech (Mercury, Brex) statements.

Use this for: data-forward dashboards, KPI reviews, performance reports, founder updates, monthly investor letters — anywhere the data carries the page and chrome would be noise.

## Typography

```css
:root {
  --font-display: "Söhne", "Inter Display", "GT America", -apple-system, sans-serif;
  --font-body:    "Söhne", "Inter", -apple-system, "Helvetica Neue", sans-serif;
  --font-mono:    "Söhne Mono", "JetBrains Mono", "Berkeley Mono", monospace;
}
```

- **Display:** clean modern sans, slight optical sizing — Söhne preferred, Inter Display acceptable.
- **Body:** same family, regular weight. Single-family discipline is the look.
- **Sizes:** display 24–36pt, section heads 12pt, body 9.5pt, footnotes 7.5pt.
- **Weights:** 400 body, 500 section heads, 600 hero numbers. NEVER bold beyond 600.
- **Letter-spacing:** -0.01em on display (tight, modern), 0 on body, +0.04em uppercase on small labels.
- **Line height:** 1.5 body (open, breathing), 1.1 display.
- **Tabular figures + slashed zeros** in all numerics.

## Color palette

```css
:root {
  --ink:        #0A0A0A;     /* near-black */
  --paper:      #FFFFFF;     /* pure white */
  --grey-50:    #FAFAFA;     /* alt-row, subtle fills */
  --grey-100:   #F4F4F5;     /* card backgrounds */
  --grey-200:   #E4E4E7;     /* borders */
  --grey-400:   #A1A1AA;     /* metadata */
  --grey-600:   #52525B;     /* secondary text */
  --accent:     #0E5FE8;     /* one bold accent — use sparingly */
  --positive:   #15803D;     /* deltas: positive */
  --negative:   #DC2626;     /* deltas: negative */
}
```

- Dominant: ink on white with grey scaffolding.
- Accent: ONE accent color only. Default electric blue; vary per document (try `#0E5FE8`, `#7C3AED`, `#10B981` — pick one and lock it).
- Positive/negative: only for KPI deltas, not for general highlighting.
- Avoid: warm earth tones, golds, gradients, multi-color palettes.

## Spatial composition

- **Massive whitespace.** Outer margins 18mm+. Content breathes.
- **Hero number treatment** for the headline KPI: 48-72pt display, single line, with a tiny-caps label above.
- **Card-based sections.** Subtle `--grey-100` fill, 1px `--grey-200` border, generous internal padding (12mm). Corner radius 4-6px (not larger).
- **Single dominant element per page.** Eye lands first on the hero number; everything else supports.
- **Consistent vertical rhythm.** Section spacing should be a multiple of a base unit (8pt grid).

## Visual details

- **Charts:** axis labels in `--grey-400`, gridlines if needed in `--grey-100`, line series in ink with the highlighted series in `--accent`. No fills under area charts beyond a 10% alpha accent. Smooth lines, no markers.
- **Tables:** no outer border. Hairline `--grey-200` rows. Header row with `--grey-600` text uppercase tracked. Right-aligned numerics with consistent decimals.
- **KPI cards:** number in 36pt+ ink, label in 9pt uppercase tracked `--grey-600`, delta in 11pt with `--positive`/`--negative`, optional sparkline in `--accent` underneath.
- **No icons in line with text.** If an icon is used, it's standalone and large.
- **Section dividers:** whitespace, not rules. Let air separate sections.

## Layout patterns

- **Hero card** at top: company/period/headline KPI.
- **3-up KPI row** beneath: three equal cards with number + label + delta.
- **Two-column body** with charts in one column and supporting prose in the other.
- **Bottom-of-page summary** with the single recommendation or takeaway in a `--accent` accent block.

## Anti-patterns to avoid

- Drop shadows (everything flat).
- Gradients (everything flat).
- More than one accent color.
- Decorative borders or rules where whitespace would do.
- "Pitch deck" hero blocks with full-bleed color.
- Bold weight 700+.
- Mixing serif and sans (single-family discipline).
- Charts with a legend embedded inside the plot — put the legend above or below.
