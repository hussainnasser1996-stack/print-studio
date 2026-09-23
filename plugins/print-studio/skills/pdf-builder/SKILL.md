---
name: pdf-builder
description: Build professional, distinctive single-file HTML→PDF business documents — investor teasers, one-pagers, pitch decks, financial reports, company profiles, deal documents, term sheet summaries. Use when the user asks for a print-ready PDF that needs to be auditable against source documents AND visually distinctive. Renders via headless Chrome (Mac) / Edge (Windows) / Chromium (Linux). NOT for free-form web UI, long-form text (50+ pages), or design-tool round-trips.
---

# PDF Builder

Build print-ready, single-file HTML→PDF business documents that are **(a) numerically auditable against source documents** and **(b) visually distinctive** — not generic AI-default output.

This skill has two layers:

1. **Aesthetic direction** — pick a bold visual direction *before* writing HTML. Lock typography, color palette, and spatial composition as CSS variables. Never default to "modern professional navy/teal/gold + Inter everywhere."
2. **Build process** — single self-contained HTML file, inline SVG charts, base64 images, headless-browser render, read-the-PDF-back verification loop.

The build process is non-negotiable (it's why the output is reliable). The aesthetic direction is what keeps every doc from looking like the last one.

---

## Self-improvement: mandatory on every use

This skill fixes itself. It's used across many projects (work documents, client reports,
personal publications), and any defect it lets through will happen again on the next job
unless the skill itself changes.

**Canonical copy:** `~/.claude/skills/pdf-builder/`, a symlink into the user's Claude Hub repo
(`custom-skills/pdf-builder/`). Edit **only** there. Every other copy (the public GitHub repo, a
release zip, a plugin cache) is downstream and gets overwritten from the Hub. If you installed
this skill some other way, your install folder is the canonical copy; skip the commit step.

When you, the user or a read-back check finds a defect during a job:
1. **Fix the document first.**
2. **Ask: would this happen again on a different document?** Wrong sizing, font fallback,
   overflow, clipped text, a wrong command, a template bug, a misleading instruction, a check
   that failed to fire: yes, those are skill defects. If it only concerns this document's
   content or this client's brand, it isn't a skill defect, so stop here.
3. **Patch the canonical copy.** Put the rule where the next reader will hit it (the relevant
   section, or the gotchas list), written as *symptom → cause → fix*. If an existing rule
   already covered it and was ignored, strengthen or move that rule instead of adding a
   duplicate. When the bug is in a template or script, fix the file itself.
4. **Write it generically.** This skill is published publicly. No client, company, fund or
   person names, no real figures, no paths from the job: write "a 12-page fund report", not
   the report's real name. Private notes go in `LOCAL.md`, which is never published.
5. **Log it:** one line in `CHANGELOG.md` (date · what broke · what changed).
6. **Commit only this skill's files** (git follows the symlink to the Hub repo):
   `git -C ~/.claude/skills/pdf-builder add . && git -C ~/.claude/skills/pdf-builder commit -m "pdf-builder: <lesson>" -- .`
7. **Tell the user in one line:** "Skill updated: <lesson>."

---

## When to use

✅ Investor teasers, one-pagers, pitch decks, financial reports, company profiles, board packs, term-sheet summaries, deal-process documents, dashboards, invoices.

✅ Anything print-style where layout precision matters and the document gets sent to a third party (LP, IC, regulator, prospect, client).

## When NOT to use

❌ **Free-form visual design** (logos, illustrations, hero pages with lots of imagery) — Figma/Adobe is better.

❌ **Long-form text** (50+ page reports, books, contracts) — LaTeX or Word.

❌ **Multi-column flowing text** (newspapers, magazines) — InDesign.

❌ **Web UI / app interfaces** — use the `frontend-design` skill instead. This skill is for *print* output; web-only patterns (motion, hover, scroll-trigger, custom cursors) don't render in print.

---

## Step 0 — Pick the aesthetic direction (mandatory, before any code)

**Skipping it is how you end up with five different teasers that all look the same.**

The user picks ONE of:

### A. Pre-baked direction (fastest)

Reference one of the bundled directions in `aesthetic-directions/`. Each is a self-contained spec for typography, color palette, spatial composition, and visual details. Current set:

| Direction | One-liner | Use when |
|---|---|---|
| `editorial-magazine` | FT/Economist editorial — serif headers, generous whitespace, hairline rules | Long-form reports, thoughtful briefings, sector deep-dives |
| `luxury-refined` | Deep neutrals, gold rule lines, restrained — private bank / family office feel | High-net-worth client materials, bespoke deal teasers |
| `institutional-classic` | Navy/teal/gold, Inter — the safe corporate default | Standard IC memos, term sheet summaries (when nothing else applies) |
| `brutalist-raw` | Mono headers, hard rules, no rounded corners, dense | Diligence packs, technical research, contrarian/edgy positioning |
| `modern-minimal` | Sans, white space, dense data tables, no chrome | Data-forward dashboards, KPI reviews, performance reports |

Load the direction's `.md` file and treat its rules as binding for the whole document.

### B. Reference-PDF mode (extract from a real document)

User provides an existing PDF (FT article, McKinsey one-pager, a competitor's teaser, an old deal doc they liked). Extract:

- **Color palette** — sample 4-8 dominant hex codes (use Python + Pillow on the rendered image: `pip install pdf2image pillow` if needed; or have the user provide hex codes directly)
- **Typography** — identify display vs body font; if proprietary, pick a closest open-source equivalent and note the substitution
- **Layout density** — count column structure, KPI tile size, header proportion, footer treatment
- **Hierarchy** — what's the strongest visual element on page 1? Replicate that level of dominance.

Lock these as CSS variables before writing any HTML.

### C. Custom direction (user provides explicit rules)

User gives explicit hex codes, font choices, density preferences. Lock them. Don't second-guess.

### Anti-AI-slop guardrails (always apply)

Regardless of direction, **never**:

- Default to Inter for *every* text element. Inter for body is fine; headers should use a distinctive display face (Fraunces, Tiempos, Söhne, GT Sectra, Playfair Display, JetBrains Mono — pick one with character).
- Use cliché AI-generic palettes (purple gradients on white, evenly-distributed pastel rainbows, "default Tailwind").
- Produce a layout where every section has the same density, the same column structure, and the same visual weight. Asymmetry, deliberate density variation, and grid-breaking are good.
- Add motion, hover states, transitions, scroll-triggers — print is static. Strip these from any direction file before applying.
- Converge on the same choices across documents. If you used `Fraunces` last time, try `Tiempos` this time. Variety across docs is a feature.

---

## Source documents and source-of-truth hierarchy

```
SOURCE DOCUMENTS  (in [absolute path to the project folder])
- [file 1.pdf]   – [what it is, e.g. "signed term sheet — senior source of truth"]
- [file 2.xlsx]  – [e.g. "financial model — supporting basis for forecasts"]
- [file 3.pdf]   – [e.g. "company profile — operational/brand context"]
- [logo.png/jpg] – embed in the header
- [optional]     – existing PDF to match the theme of (Reference-PDF mode)

SOURCE-OF-TRUTH HIERARCHY  (enforce on every numeric or factual claim):
  1. [doc 1] — wins all conflicts
  2. [doc 2] — supporting basis, used where doc 1 is silent
  3. [doc 3] — last-resort, only when neither doc 1 nor doc 2 speaks

If numbers in different sources disagree, FLAG them to the user before
building. Don't silently pick one. Don't invent numbers.
```

---

## Build approach (mandatory — do not deviate)

- **Single self-contained HTML file** with all CSS embedded, all SVG charts inline, all images base64-embedded. No external assets, no CDN, no fonts that need downloading. *Exception:* if a chosen direction calls for a Google Font, embed it via `@font-face` with base64-encoded woff2 — never `<link rel="stylesheet">`.
- **Render to PDF with a headless Chromium browser** (same flags on every OS):
  ```bash
  # macOS — Google Chrome
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    --headless=new --disable-gpu --no-pdf-header-footer \
    --print-to-pdf="output.pdf" "file:///absolute/path/to/file.html"
  ```
  ```powershell
  # Windows — Microsoft Edge (preinstalled on Windows 10/11)
  & "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" `
    --headless=new --disable-gpu --no-pdf-header-footer `
    --print-to-pdf="output.pdf" "file:///C:/absolute/path/to/file.html"
  ```
  On Linux use `chromium --headless=new …` with the same flags, or Playwright's `page.pdf()`.
- **Page setup:** A4 portrait, `@page { size: A4; margin: 0 }` with each page as `<section class="page">` sized 210mm × 297mm. `page-break-after: always`.
- **Print color preservation:** `* { -webkit-print-color-adjust: exact; print-color-adjust: exact; }`
- **Charts:** hand-author inline SVG with manually computed coordinates. No Chart.js, no D3, no chart libraries.
- **Logo and any images:** base64-encode and inline into `<img src="data:...">` tags.

### DO NOT USE
- Python PDF libraries (reportlab, fpdf, weasyprint) unless the user explicitly asks
- Markdown → PDF tools
- Word, Google Docs, LaTeX
- Figma, Pencil, or any design-tool round-trip
- Tools that require `pip install` or `npm install` unless headless browsers are genuinely unavailable
- Chart.js, D3, or any chart library — hand-author SVG
- Web fonts loaded via `<link rel="stylesheet">` — embed as base64 `@font-face` if needed
- Motion, animations, hover states — none of these render in print

---

## Page structure ([N] pages total)

Spell out the page plan, then apply the spatial composition rules below:

```
[Spell out roughly what goes on each page. Examples:]

PAGE 1: Hero header (logo + company name + confidentiality line),
        deal-terms sub-bar, KPI tile row, [N] columns of context
        (market / business model / traction), financial snapshot
        table, revenue + margin charts.

PAGE 2: Transaction terms table (every line item from the term sheet),
        timeline, returns scenarios.

PAGE 3: Valuation methodology, sensitivity analysis, comparable
        companies, key takeaway.
```

**Spatial composition rules** (from frontend-design, adapted for print):

- **Asymmetry over even grids.** A page with one dominant element + smaller supporting blocks reads stronger than four equal quadrants.
- **Deliberate density variation.** Page 1 hero can breathe; page 2 deal terms can be dense and tabular. They don't need to look the same.
- **Strong visual hierarchy.** The eye should know exactly where to land first. Use scale, color, and whitespace to enforce this — don't rely on the reader to figure it out.
- **Grid-breaking is allowed when it serves the content.** A KPI tile bleeding into the margin, a chart spanning two columns, a callout in the gutter. Use sparingly; intentionally.
- **Generous negative space OR controlled high density** — not the soggy middle. Pick one per section.

If layout decisions affect content density, ask the user before building.

---

## Vertical composition — the page-fill discipline

**This is the single strongest tell that separates a human-made report from a generated one,
and it is invisible at thumbnail scale. Check it by measurement, never by eye.**

The tell is not white space. It is *undifferentiated* white space — content poured into a
fixed-height box, stopping wherever it happens to stop, leaving a differently-ragged bottom
edge on every page. A human designer never ships that. The opposite failure is just as
damning: padding every page to ~95% with filler sentences so all pages look identical.
Uniform density with no rhythm reads as machine-made too.

**The rule: every page's bottom edge must be a decision.** Not an accident, and not a
uniform target.

### Page types, each with its own rule

| Type | Rule |
|---|---|
| **Cover / section opener** | Composed. Anchor a block top and a block bottom; carry the space in the middle. Space *is* the design here. |
| **Dense analytical page** | Running argument, cards, tables. Fill to a consistent baseline. A trailing gap here is a defect. |
| **Hero page** (one chart, one idea) | Deliberately spare — but the content must be optically anchored, never top-stacked over a hole. |
| **Closing page** | Sources and legal matter pinned to the foot, argument above, space at the seam between them. |

### Fixes, in order of preference

1. **Size the page to the content.** If the page format is yours to choose (a mobile/scroll
   variant, a screen-read PDF), and content naturally fills ~70% of the box, the box is wrong.
   Shorten it. This is the best fix and the most often missed — do not stretch content to fit
   a height that was inherited rather than chosen. A4/Letter is fixed; a custom format is not.
2. **Add real content.** Only if the page is genuinely thin on substance. Never filler
   sentences that restate the paragraph above — that is the thing you are trying to avoid.
3. **Scale the block to the measure.** For a card grid or a short section, add a per-page
   class that raises padding and type ~10–15% so the grid fills its box. Establish one such
   class (e.g. `.exec`, `.grid-fill`) and reuse it rather than hand-tuning each page.
4. **Anchor one element to the foot** — `display:flex; flex-direction:column` on the page plus
   `margin-top:auto` on the single element that belongs at the bottom.
   **Only valid when the residual is small (under ~15% of page height).** Anchoring on a page
   that is 30% short does not fix the hole; it relocates it to the middle of the page, which
   looks worse than the ragged foot did. Apply to **one** element per page — never spread the
   space evenly between every element, which produces a visibly stretched page.

⚠️ **CSS source-order trap:** a `.tail { margin-top:auto }` utility declared near the top of
the stylesheet loses to any component that sets its own `margin-top` later (`.callout`,
`.toc`, `.src`). Declare the utility **last**, or use `!important`. Symptom: the anchoring
silently does nothing and fill numbers do not move.

### Measure it — four checks, all required

Visual inspection catches none of these reliably. Run all three on the rendered PDF:

```python
import fitz
d = fitz.open(pdf); H = d[0].rect.height
for i, pg in enumerate(d):
    dr = [r['rect'] for r in pg.get_drawings() if r['rect'].y1 < H - FOOTER_ZONE]
    tx = [b for b in pg.get_text('blocks') if b[4].strip() and not is_footer(b, H)]
    pts = sorted([(b[1], b[3]) for b in tx] + [(r.y0, r.y1) for r in dr])
    gap = 0; cur = pts[0][1]
    for a, b in pts[1:]:
        gap = max(gap, a - cur); cur = max(cur, b)     # largest internal hole
    trailing = (H - FOOTER_Y) - max(e for _, e in pts)  # ragged-foot measure
```

1. **Trailing space** — distance from the lowest ink to the footer. Target a median well under
   ~15% of page height, with variation that is *intentional* (a spare hero page is fine; nine
   pages all ending at a random height is not).
2. **Largest internal gap** — should be in the range of normal paragraph spacing (roughly
   15–30pt). A gap of 100pt+ means an anchor opened a hole mid-page.
3. **Content completeness** — assert that required strings are present in the extracted text:
   the full disclaimer, every legal clause, the last sentence of the last section.

### A fourth check: footer clearance — and prove your checker fires

The footer (and any repeating page furniture) is not content. **Nothing may overlap it** — not
a paragraph, and not the border of a callout or card whose box has grown down into it. This is
a distinct failure from the trailing-space and clipping checks and neither one catches it: the
page can be perfectly filled, nothing clipped, and a card border still runs straight through
the footer text.

```python
foot = [line for line in lines(pg) if line.rect.y1 > H-60 and is_footer_text(line)]
for fr in foot:
    for r in drawn_boxes:          # exclude only the full-page background fill
        if (r & fr).is_valid:      # ANY intersection, not just an edge crossing
            fail('box over footer')
```

Two mistakes to avoid when writing this check, both of which produce a silent false pass:

- **Do not filter drawings out of the footer band** to avoid matching the footer's own hairline.
  That excludes precisely the region where the collision happens. Filter by *shape* (drop the
  full-page background rect and full-width hairlines), never by position.
- **Do not test only for an edge passing strictly through the glyphs.** The common real case is
  a box that *encloses* the footer — its bottom edge sits just below the text, so a
  "strictly inside" test never fires. Test for **any intersection**.

⚠️ **Prove the checker can fail before you trust it passing.** A detector that never fires and
a clean document produce identical output. Build a one-page positive control — a box positioned
to overlap the footer at the same coordinates as the real layout — render it, and confirm the
checker reports it. If the control does not fire, the checker is broken, not the document.
Match the control's geometry to the real page (a footer 30pt from the bottom edge, not 80pt),
or the control will miss for reasons that have nothing to do with the bug.

⚠️ **Scope banned-term regexes to context.** A rule like "no `$18B`" will match a chart's axis
gridline labels (`0 · $6B · $12B · $18B · $24B`) and report a compliance breach that is not
one. Anchor the pattern to the subject — the company name within N characters — and print the
surrounding text with every hit so a false positive is obvious at a glance.

⚠️ **The clipping trap, and why check 3 is not optional.** With `overflow:hidden` on a
fixed-height page (the standard pattern), overrun content is **silently deleted from the
output** — no error, no scrollbar, no visual artefact. It is therefore invisible to checks 1
and 2, because clipped text is not in the PDF to be measured. A truncated legal disclaimer is
the realistic failure mode, and it is a compliance problem, not a layout one. **If the legal
block does not fit, give it its own page** — never shrink it to squeeze it in.

---

## Process (mandatory — follow in order)

0. **Aesthetic direction** — confirm with user (or have them pick) before any code. Load the direction file. Lock typography and palette as CSS variables.
1. **Read every source document.** If anything is too large or in a format you can't read directly (Excel, large PDFs), use `openpyxl` with `data_only=True` for xlsx, or spawn an Explore subagent to extract content from oversized PDFs. Don't skip this step.
2. **Build a discrepancy table** before building anything: every number that appears in the document must be traceable to a specific source. Where sources disagree, show the user the conflict and let them decide.
3. **Plan the page structure.** Apply the spatial composition rules above. Ask the user to confirm any layout calls that affect content density.
4. **Build the HTML file.** Use placeholders like `LOGOB64` for base64 images, then substitute via Python after writing. Keeps Edit/Write tool calls manageable.
5. **Render to PDF via headless Chrome / Edge / Chromium** (see Build approach).
6. **READ THE PDF BACK YOURSELF and verify — measured checks first, then visual:**
   - **Run the four vertical-composition checks** (trailing space, largest internal gap,
     content completeness, footer clearance) from the section above — and confirm the
     checker itself fires on a positive control before trusting a clean result. Do this *before* looking at the pages:
     underfill and silent clipping are invisible at thumbnail scale, and clipped text cannot
     be seen at all because it is absent from the PDF.
   - **Page count equals pages authored.** More means something overflowed.
   - Layout fits the page (no overflow, no orphaned content on an extra page)
   - Logo renders crisp
   - Charts are correct (numbers, axes, labels)
   - Tables are aligned and not clipped
   - All numbers match the source-of-truth documents
   - **Aesthetic direction was honored** (typography, palette, composition match what was locked in step 0 — did it drift to AI-default?)
7. **Iterate.** If anything is off, fix the HTML and re-render. Don't ship on the first render and call it done.
8. **Save outputs:**
   - HTML to `[project]/teaser/teaser.html` (so user can re-edit later)
   - PDF to `[project]/[Company] – [Doc Name].pdf`
   - Leave any existing PDFs untouched (don't overwrite originals)
9. **Write a short README.md** in the build folder documenting:
   - Aesthetic direction chosen (and why, if reference-PDF mode)
   - Version history (what changed in each render)
   - Any intentional deviations from source documents
   - Exact command to regenerate the PDF
   - Key cell references from the model so future audits can verify

---

## What to hand back

- The final PDF, ready to send to investors
- A short summary of any discrepancies between source documents and how you resolved them
- Confirmation that you read the PDF back and verified both layout AND aesthetic direction
- The build folder with HTML source + base64 assets + README

If anything blocks you, stop and ask. Don't guess at numbers, don't invent content to fill space, don't pick a design direction without confirming.

**Worked example:** `examples/investor-teaser/` in this skill's repository — a two-page Series B teaser for a fictional company in the `editorial-magazine` direction, with the build script that keeps every chart, table and sentence tied to one data block.

---

## Specific scenarios

**If source data is in Excel** — use `openpyxl` with `data_only=True`. Otherwise the model reads formula strings (`=SUM(B2:B10)`) instead of computed values.

**If a source PDF is over 20MB** — use `pdftotext` or spawn an Explore subagent. The Read tool refuses files over 20MB.

**If you want multi-version iteration** — save each iteration as V1, V2, V3 PDFs so the user can compare and roll back.

**If the PDF is going to investors, regulators, or external audiences** — be conservative with claims. Don't extrapolate beyond what the source documents say. Anything aspirational must be clearly labeled as a projection or target, not a fact.

**For a one-shot urgent doc** — trim the README and version-history requirements from step 9.

**If the user provides a reference PDF for theme-matching** — extract the palette and typography (or have the user provide them), lock as CSS variables, treat the reference as the binding aesthetic direction. Don't drift toward your defaults.

---

## Why this approach works (and is better than the alternatives)

CSS is a real layout engine. Browsers have spent 30 years solving "text doesn't fit, what do I do" — wrap, ellipsis, push down, reflow, repaginate. Headless Chrome and Edge use the same engine that prints every webpage.

Compare to **reportlab/fpdf**: programmatic PDF libraries where you say "draw rectangle here, put text there, advance 12 pixels." No layout engine. If a number is 8 chars but the cell is sized for 6, text overflows on top of the next cell. That's the "words covering up tables" failure mode.

Compare to **Markdown → PDF**: markdown has no real layout. The model is flying blind, computing nothing, hoping for the best.

Compare to **python-pptx**: same problem as reportlab — fixed-position placeholders, no reflow. Forces you into PowerPoint's layout primitives. Fine for branded slide decks; wrong for dense analytical PDFs.

Compare to **`frontend-design` alone**: produces visually distinctive HTML but ignores numerical accuracy, source-of-truth, render constraints, print rules. Would happily recommend hover animations and scroll-triggered reveals on a printed page.

This skill writes intent ("3-column grid, this table, this navy header bar, editorial-magazine direction") and the browser does the actual layout work. The model can READ THE RENDERED PDF BACK and iterate if something is off — tight feedback loop, no guessing — *and* enforces an aesthetic direction so the output isn't generic.
