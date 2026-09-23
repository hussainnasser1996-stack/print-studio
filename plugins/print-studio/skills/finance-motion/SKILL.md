---
name: finance-motion
description: Turn ONE audited financial data file (report.json) into three outputs whose figures are identical and machine-verified. The outputs are a print-ready PDF (Typst), an animated MP4 for LinkedIn/social (Remotion: count-up KPIs, growing bars, segment mix, revenue waterfall, income statement), and a self-contained interactive HTML report (Apache ECharts). Use when someone wants annual or quarterly results, investor updates, fund reports or KPI highlights as a moving/interactive piece AND a printable one, or asks for animated financial charts or infographics with numbers that must be right. Every figure is validated to foot before rendering, and read back from every output after. NOT for long editorial reports (use magazine-builder's annual-report mode), one-page teasers (pdf-builder), or non-financial explainer videos.
---

# finance-motion

One data file → a print PDF, an animated reel and an interactive web report, with the **same
figures everywhere, verified**. Animated finance content usually breaks this rule. Someone
retypes numbers into a video tool, a chart rounds 16.14% to 16.2%, and the web version drifts
from the PDF. Here, no renderer is allowed to format a number. Every visible figure is a
`display` string copied from `report.json`, and two checkers enforce that.

```
report.json ──validate_report.py──► PASS? ──┬─► pdf/   → report.pdf   (Typst)
  (the only place                           ├─► video/ → reel.mp4     (Remotion)
   numbers live)                            └─► web/   → report.html  (ECharts)
                                                        │
                        verify_outputs.py ◄─────────────┘  every figure visible in every output?
```

## Self-improvement: mandatory on every use

This skill fixes itself. When you, the user or a check find a defect: fix the output, then ask
whether it would happen again on a different report. If yes, patch this skill in its canonical
location (`~/.claude/skills/finance-motion/`, a symlink into the user's Claude Hub repo) as
*symptom → cause → fix*. Write it generically: this skill is public, so no client names, real
figures or job paths. Log one line in `CHANGELOG.md`, and commit only this skill's files:
`git -C ~/.claude/skills/finance-motion add . && git -C ~/.claude/skills/finance-motion commit -m "finance-motion: <lesson>" -- .`
If you installed it some other way, your install folder is canonical; skip the commit.

## The one rule

**Numbers are data, never code.** Each figure in `report.json` has a numeric `value`, which
drives bar heights and animation, and a `display` string, which is what readers see:
`"(2,612)"`, `"$4.82B"`, `"−0.06x"`. Renderers print `display` verbatim. A count-up may
interpolate the value, but its last frame must show the exact `display` string. Deltas carry
their own sign, and `good` sets the colour separately from `direction`: falling leverage is ▼
and green.

## Workflow

1. **Build `report.json`** from the audited source. Copy `examples/meridian/report.json` and
   replace the figures. Paste `display` strings exactly as the source prints them; never
   re-round. Show the user any conflict between sources and let them decide.
2. **Validate:** `python scripts/validate_report.py report.json`. It must PASS before anything
   renders. It checks that displays match values, totals foot, the bridge closes, growth,
   margin and share recompute at the displayed precision, KPIs tie to the tables, and delta
   signs agree with direction. Run `--selftest` once per machine: it plants 7 errors and every
   one must be caught.
3. **Render** the outputs the user wants (sections below).
4. **Verify:** `python scripts/verify_outputs.py report.json --pdf … --mp4 … --html …`.
   Every canonical figure must be visible in every output. It checks the PDF text layer, the
   DOM, and GLM-OCR of pages, held video frames and a static-mode screenshot. Then look at the
   outputs yourself, zoomed in. Checks catch missing figures, not ugly layouts.

## Schema (`report.json`)

| Block | Holds | Checked by the validator |
|---|---|---|
| `meta` | company, period, prior_period, currency, units, source, `fictional`, `theme` colours | — |
| `kpis[]` | id, label, value, display, delta, direction, good | display==value; ties to tables; delta sign vs direction |
| `revenue_history.points[]` | label, value, display | last two points tie to segment totals |
| `segments` | items[] + total: revenue, revenue_prior, op_profit + display{growth, margin, share} | sums foot; ratios recompute |
| `bridge` | start, steps[], end | closes; each step = that segment's change |
| `income_statement` | columns, rows[]: values[], display[], total, sum_of | totals = sum_of rows |

Recognised KPI ids for the cross-checks: `revenue`, `op_profit`, `op_margin` (in the same
units as the segment tables ÷ 1000). Other ids are allowed and are checked only for
display==value and delta sign.

## Output 1: print PDF (`pdf/`, Typst)

`bash pdf/build.sh report.json out.pdf` validates the data, then renders three A4 pages from
`pdf/report_pages.typ`:
1. highlights: KPI cards, revenue-history bars, segment mix
2. revenue bridge: a waterfall, plus the segment table
3. income statement, with a source line

Typst reads the JSON natively (`json(sys.inputs.at("data"))`), so a figure never passes
through code. Fonts: Archivo, Anton, Newsreader and Space Mono, from magazine-builder's
`assets/fonts-ttf` (override with `FM_FONTS`, or `--input font-sans=…` and similar). Pages are
marked "FICTIONAL SAMPLE DATA" when `meta.fictional` is set. The waterfall's truncated axis
is shown with break marks, never hidden. For a long editorial report, use magazine-builder's
annual-report mode, which shares the same component vocabulary.

## Output 2: animated reel (`video/`, Remotion)

`bash video/render.sh report.json out.mp4 [--format 4x5|9x16|16x9]` renders a ~35 s reel:
title → KPI grid (count-ups) → revenue bars growing → segment mix → revenue waterfall →
income statement → source card. The output is H.264 yuv420p with faststart and no audio, ready
for LinkedIn. Allow ~20 s on a laptop after a one-time `npm install` in `video/`.
- Count-ups interpolate `value` but **land on the exact `display` string**. Every data scene
  ends in a ≥2 s static hold, and the manifest points the verifier at a frame inside it.
- The delta arrow follows `direction` and its colour follows `good`.
- `9x16` and `16x9` scale the 4:5 stage to fit. That's usable, but not a bespoke layout.
- A tiny waterfall step gets a minimum bar height of 8 px, so it reads slightly larger than
  its true size. Its label is still exact.
- **Licence:** Remotion is free for individuals and companies of up to 3 employees; larger
  companies need a Remotion company licence.

## Output 3: interactive web report (`web/`, ECharts)

`python web/build_html.py report.json out.html [--offline]` writes one self-contained HTML
page:
- a hero
- KPI cards whose digits roll, then settle on the exact display string
- animated revenue bars
- a segment donut with a clickable legend and detail panel
- the revenue waterfall
- the income statement as a real table

Sections animate in on scroll. `?static=1` (or prefers-reduced-motion) renders the final state
with no motion; use it for screenshots and verification. Charts use ECharts' SVG renderer, so
labels are real DOM text, and axis tick labels are hidden so no unstated number appears.
ECharts 5.6.0 is pinned from jsDelivr; `--offline` inlines it (~1 MB). The page works at phone
width (390 px) with no sideways scroll.

## Manifests: how the verifier knows where to look

Every renderer writes `<output file>.manifest.json`, using the full filename, because
`report.pdf` and `report.html` share a stem:
- PDF: `{"section","page"}`
- MP4: `{"section","t"}`, where `t` is inside the static hold
- HTML: `{"section","selector"}`

A new renderer must write one too, or `verify_outputs.py` refuses to check it. Sections
without figures (a hero) are skipped.

## Verification in one line

```bash
python scripts/validate_report.py report.json && \
python scripts/verify_outputs.py report.json --pdf out/report.pdf --mp4 out/reel.mp4 --html out/report.html
```

OCR runs locally (GLM-OCR via transformers, ~2 GB model once). Setup:
`pip install pymupdf pillow torch torchvision "transformers>=5.17" accelerate`. Use `--no-ocr` for a
fast text-layer/DOM-only pass; that pass can't see hidden or clipped text.
