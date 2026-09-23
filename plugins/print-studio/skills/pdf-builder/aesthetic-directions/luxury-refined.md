# Aesthetic Direction — Luxury / Refined

Reference exemplars: Lombard Odier, Pictet, Edmond de Rothschild, Hermès annual reports, the cleaner Goldman Sachs / Lazard private-banking decks.

Use this for: HNW client materials, family-office documents, bespoke deal teasers, foundation reports, anything where restraint signals quality.

## Typography

```css
:root {
  --font-display: "Söhne", "GT Sectra", "Tiempos Headline", "Optima", "Times New Roman", serif;
  --font-body:    "Söhne", "Inter", -apple-system, "Helvetica Neue", sans-serif;
  --font-mono:    "GT Sectra Mono", "Berkeley Mono", "JetBrains Mono", monospace;
}
```

- **Display:** can be a refined serif (GT Sectra, Tiempos) OR a precise sans (Söhne, Suisse) — but ONE choice per document, used consistently.
- **Body:** sans-serif, high contrast strokes, generous letter-spacing.
- **Sizes:** display 22–32pt, section heads 11–13pt with letter-spacing, body 9pt, footnotes 7pt.
- **Letter-spacing:** display headers tracked +20–40 units (`letter-spacing: 0.04em`). Section heads in small caps with +80 units (`text-transform: uppercase; letter-spacing: 0.12em`).
- **Line height:** 1.5 for body, 1.2 for display.

## Color palette

```css
:root {
  --ink:        #1A1814;   /* warm near-black */
  --paper:      #F5F2EC;   /* aged paper / cream */
  --gold:       #8C6F2F;   /* muted gold for rules + highlights */
  --gold-light: #C9B280;   /* soft gold for fills */
  --burgundy:   #5A1F26;   /* secondary accent for one element per page */
  --muted:      #7A766E;   /* metadata, captions */
  --line:       #2A2620;   /* dark line color, rare use */
}
```

- Dominant: ink on cream paper.
- Gold (`--gold`) for rule lines, KPI accents, monogram elements — never as a fill behind text.
- Burgundy used at most ONCE per document, as the strongest emphasis.
- Avoid: any cool blues, teals, or modern startup colors.

## Spatial composition

- **Generous whitespace.** Outer margins 18–25mm. Density is the enemy.
- **Strong horizontal rules** in gold (1px) separate sections — paired with vertical thin rules creating quadrants only when the data warrants it.
- **Centered hero treatment** for cover pages — company name + monogram element + a single line of metadata.
- **Asymmetric body** is fine on interior pages: one wide column + one narrow margin column for metadata and pull-quotes.
- **One dominant element per page.** Never two competing focal points.

## Visual details

- Charts: minimal, refined, gold accent for the highlighted series, everything else in muted tones. No 3D, no gradients, no shadows.
- Tables: hairline gold rules between rows, no vertical rules, tabular figures, right-aligned numbers with consistent decimal precision.
- Numerals: use OldStyle figures (`font-variant-numeric: oldstyle-nums`) in body prose; tabular figures in tables.
- Monogram or logo treatment: if a logo exists, give it room — never crop it tight to the edge.
- Footer treatment: thin gold rule + section title + page number, all in small caps, all in `--muted`.

## Anti-patterns to avoid

- Drop shadows of any kind.
- Rounded corners on boxes or images.
- Background gradients.
- Color-block hero sections.
- Bold weights heavier than 600.
- Bright accent colors. Saturated reds, hot pinks, electric blues = wrong direction.
- Crowded layouts. If a section feels full, cut content rather than reduce whitespace.
