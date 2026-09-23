# magazine-builder — changelog

One line per lesson: date · what broke · what changed. Newest first. Keep entries generic (this file is public).

- 2026-09-23 · Annual-report template: typed contents page pointed at the wrong pages · TOC now reads page numbers from `<label>`s via `counter(page).at(locate(..))`.
- 2026-09-23 · Annual-report template: a YoY % was mis-rounded (16.2 vs 16.1) and a falling leverage ratio printed as "+0.06x" · Deltas are typed with their sign; `good:` sets colour independently of direction on `kpicard`/`yoyrow`.
- 2026-09-23 · Annual-report template: bar-chart value label overprinted the heading above; contents and letter pages half empty · Chart headroom; fuller sample pages; added cash-flow table and a segment page that foots to the income statement.
- 2026-09-23 · `template.typ` failed to compile out of the box (missing cover image) · Ships an original placeholder cover (`reference/img/cover.jpg`).
- 2026-09-23 · Fonts break size-capped skill registries · Added `scripts/fetch_fonts.py` and OFL licence texts.
- 2026-09-23 · Added the self-improvement protocol.
