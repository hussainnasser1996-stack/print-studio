---
name: magazine-builder
description: Build global-quality, image-led editorial MAGAZINES, bookazines, and ANNUAL / FINANCIAL REPORTS as print-ready PDFs in Typst — multi-page features, infographics, timelines, directories, glossaries, covers, KPI cards, financial-statement tables, multi-year comparisons, charts. Use for any magazine / zine / bookazine / lookbook / editorial-spread layout, OR any long, multi-page report (annual reports, corporate/financial reports) where typography, imagery, multi-page flow, and auditable numbers matter and the result must look like a real newsstand title or premium corporate report. For annual/financial reports see "Annual-report mode" + `reference/annual_report.typ`. NOT for short business one-pagers, teasers, or pitch decks (use `pdf-builder`), and NOT for motion/video.
---

# Magazine Builder

Build print-ready, **image-led editorial magazines** that look like a real global newsstand issue — not an AI-default document. Output is a multi-page PDF (cover, contents, editor's letter, feature spreads, infographics, directories, glossary, back cover).

This skill is the **Typst** counterpart to `pdf-builder` (which is HTML/CSS for numeric business docs). For magazines, Typst wins: LaTeX-grade typography you can drive *and verify*, native flow layout (which structurally prevents the #1 failure below), and a single free binary.

## Self-improvement: mandatory on every use

This skill fixes itself. It's used across many projects (work documents, client reports,
personal publications), and any defect it lets through will happen again on the next job
unless the skill itself changes.

**Canonical copy:** `~/.claude/skills/magazine-builder/`, a symlink into the user's Claude Hub repo
(`custom-skills/magazine-builder/`). Edit **only** there. Every other copy (the public GitHub repo, a
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
   `git -C ~/.claude/skills/magazine-builder add . && git -C ~/.claude/skills/magazine-builder commit -m "magazine-builder: <lesson>" -- .`
7. **Tell the user in one line:** "Skill updated: <lesson>."

---

## When to use / not

✅ Anime/film/art/craft magazines, bookazines, zines, lookbooks, sector "the story of X" specials, multi-page editorial features with mixed text + infographics + imagery.

❌ Business one-pagers, investor teasers, IC memos, dashboards → `pdf-builder`. ❌ Slide decks. ❌ Video/motion of any kind.

---

## THE TWO CARDINAL RULES (most failures are one of these)

### 1. FLOW LAYOUT ONLY for text. Never hand-place flowing text at absolute coordinates.
The single biggest mistake: positioning each text block with `place(top+left, dy: 96mm, …)` and *guessing* the heights. When a block runs longer than you guessed, it silently overprints the next one. **Browsers and Typst both have real layout engines — use them.** Author content in normal flow: page margins, `grid`, `columns`, `stack`, blocks that stack automatically. Then overlap is *structurally impossible*.
- `place()` is allowed ONLY for cover/poster composition (full-bleed image, scrims, masthead) and decorative watermarks — and you MUST verify those zoomed-in.

### 2. VERIFY EVERY PAGE ZOOMED-IN. Never judge from thumbnails.
After every compile: render the PDF back to PNG at **300 DPI** with `pypdfium2`, and **read native-resolution crops of the text regions** (not a shrunk full-page thumbnail — overlaps hide at thumbnail scale). **Read EVERY page**, in batches. Checks every time:
- **Page count == pages you authored.** If it grew, a page overflowed (often by a 1mm sliver into a near-blank page). Tighten spacing or trim copy until it's back.
- **No text touching/overprinting** in the zoomed crops.
- **Folios are CONSECUTIVE and match the Contents.** A stale page number (e.g. authoring jumps `n:17` → `n:19`) prints a visible gap a collector will notice. Verify the printed folios run 2,3,4… with no skips, and that every TOC page number matches where that section actually lands. (Real bug found in *ANIMA* Vol.01, the worked example below: folio 18 was skipped.)
- **Caption/credit boxes placed over images are actually legible AND clear of flow text** (see the dark-on-dark + place-collision gotchas below).

This is *why magazines work where motion fails*: a PDF is still pages you can actually see. Use that. Iterate honestly; never claim quality you didn't view.

---

## Environment setup (all free, no Homebrew needed — cross-platform)

Typst ships as a single static binary from GitHub releases — **pick the build for your OS**.
Fonts are **bundled with this skill** at `assets/fonts-ttf/` (Anton, Archivo, Archivo Black,
Newsreader, Newsreader Italic, Space Mono, Caveat — all SIL OFL, licences in
`assets/fonts-ttf/licenses/`), so the look is identical on every machine. If that folder is
empty (a "lite" install from a size-capped registry), run `python3 scripts/fetch_fonts.py` once.

**macOS / Linux (bash):**
```bash
# Typst — Apple Silicon shown; Intel Mac = x86_64-apple-darwin; Linux = x86_64-unknown-linux-musl
curl -sL "https://github.com/typst/typst/releases/latest/download/typst-aarch64-apple-darwin.tar.xz" -o /tmp/typst.tar.xz
tar -xJf /tmp/typst.tar.xz -C /tmp && cp /tmp/typst-*/typst ~/.local/bin/typst
python3 -m pip install -q pypdfium2 pillow              # render-back verification
```

**Windows (PowerShell):**
```powershell
# Typst — Windows x64 zip from the same release
$u="https://github.com/typst/typst/releases/latest/download/typst-x86_64-pc-windows-msvc.zip"
Invoke-WebRequest $u -OutFile "$env:TEMP\typst.zip"
Expand-Archive "$env:TEMP\typst.zip" "$env:TEMP\typst" -Force
Copy-Item "$env:TEMP\typst\*\typst.exe" "$env:USERPROFILE\.local\bin\typst.exe"  # ensure this dir is on PATH
py -m pip install pypdfium2 pillow                       # render-back verification (use `python` if `py` is absent)
```
(Winget alt: `winget install --id Typst.Typst`.)

Compile with the project dir as root so image paths resolve, pointing `--font-path` at the
**bundled** fonts (adjust the relative path to wherever this skill sits):
```bash
# any OS — replace <skill> with this skill's folder (backslashes are fine on Windows)
typst compile --root .. --font-path <skill>/assets/fonts-ttf issue.typ ISSUE.pdf
```
Smoke test after setup — both references compile out of the box:
`typst compile --root <skill>/reference --font-path <skill>/assets/fonts-ttf <skill>/reference/template.typ test.pdf`
Then verify: `typst fonts --font-path <…>/assets/fonts-ttf` must list the families before you
rely on them (variable-font instance names differ — see the gotcha below).

---

## Process (follow in order)

### Step 0 — Design DNA + lock a system (before any layout)
If the user gives a reference issue/PDF, **study its design only** (never copy its copyrighted art or text): render a few pages with `pypdfium2` and sample the dominant hex palette + identify display vs body type + the grid/density. Then lock a **distinctive** system as variables — don't default to "Inter everywhere + navy/teal".
- A premium baseline that works: **ink + warm paper + ONE bold accent** (e.g. `#16130F` / `#F2ECDE` / a vermilion `#DD4327`).
- Type: a heavy condensed display (Anton), a grotesque for labels/headlines (Archivo / Archivo 900), an editorial serif for body (Newsreader / Source Serif). All OFL and **bundled** in `assets/fonts-ttf/` — pass that to `--font-path` (no download needed).
- Pick ONE characterful display face to own the identity; vary it across issues.

### Step 1 — Flatplan
Decide the page order and the light/dark rhythm. A real issue alternates **light text features** with **dark infographic pages**. Typical 16–18pp arc: Cover → Contents → Editor's Letter → History/Timeline spread → 3–4 Feature spreads (each = a light text opener + a dark infographic) → Directory → Glossary → Back cover. Make the Contents page numbers match the real pages.

### Step 2 — Build with the template (`reference/template.typ`)
Use the `CONFIG` block + helpers in `reference/template.typ`: `leaf(section:…, col:…, n:…, fill:…)` (page scaffold: margins + edge tab + folio + running head), `ftitle` / `brush` / `kicker` / `runword` / `pull` (typography), `framed` (bordered image + drop shadow), `caption` (note box — keep its default white bg over dark art), plus the info-design generators `spacingdots`, `colorscript`, `depthlayers`, `layerstack`, `swatchrows`, and the **density "furniture"** `polaroid`, `deck`, `databar`, `factstamp`, `bigquote`, `profileside`, `gallerygrid`, `steprow`. Rebrand by editing only the `CONFIG` block (BRAND, the 6 palette hexes, fonts, trim). Author each page in flow. **Match the rivals' DENSITY**: every page should carry a title + body + 2–4 captioned images + at least one furniture element (a data bar, fact stamp, pull-quote, profile sidebar, or gallery). Minimal/sparse pages read as a document, not a magazine. Originality of *information design* carries the visuals — build real graphics: pipeline diagrams, timelines, X-sheets/time-sheets, spacing/easing dot diagrams, exploded-layer stacks, bar/cost charts, capsule-card directories. These are hand-authored with Typst `grid`/`table`/`stack`/`place`+`circle`/`rect`/`line` and are fully ownable.

### Step 3 — Imagery (this is what makes it a magazine, not a document)
A magazine needs pictures. **Never reproduce copyrighted art** (anime/film stills, character designs, brand key art). Three legitimate sources — use all three:
1. **Original information design** — the infographics above. Ownable, on-brand, infinite.
2. **Your own renders** — Blender/3D-toon stills, photography you shot. Drop in via `imgfig`.
3. **Original AI illustrations, generated locally & free** — `reference/aigen.py` (diffusers + a style/anime SD model). Prompt **original scenes only** (e.g. "a lone swordsman at dusk", "an animator's desk") — never named characters/IP. Or use **CC0 / public-domain / Wikimedia** photos with the license checked per image.
- **Cover = image-led**: full-bleed hero image + top/bottom gradient **scrims** (`gradient.linear` with alpha) for text legibility + masthead + cover lines. This single change is the biggest jump toward "looks like a real magazine".

### Step 4 — Verify (see Cardinal Rule 2) and iterate. Then export + a contact sheet.

---

## Typst gotchas (cheat sheet — these cost real time)

- **Variable-font family names differ.** `typst fonts --font-path …` may list Newsreader as `"Newsreader 16pt"` (the opsz named instance) and there's no separate `"Archivo Black"` — use `font:"Archivo", weight:900`. Always run `typst fonts` and use the exact names, or you fall back to default and don't notice.
- **Big display titles (Anton) leak huge line gaps.** Set `text(…, top-edge:"cap-height", bottom-edge:"baseline")` AND tight `par(leading: size*0.12)`. Otherwise a 2-line title eats half the page and pushes content off.
- **Default block/paragraph spacing stacks on top of your `#v()`.** In tightly-composed blocks (covers), `#set block(spacing: 0pt)` and `#set par(spacing: 0pt)` but keep `leading` ~`0.6em` (leading:0 cramps multi-line text — a real bug).
- **Image paths are sandboxed to the project root.** `../img/x.png` errors unless you compile with `--root ..` (or move images under the typst root).
- **Cover overflow.** Anchor the cover's lower text block with `place(bottom+left, dy:-16mm, …)` so cover lines sit a fixed distance from the bottom and the masthead stacks above — never `place(top, dy: guessed)`.
- **Near-blank overflow page** = content exceeds the text area by a hair. Drop one line / shrink a gap; re-check page count.
- **Dark-on-dark captions = invisible.** A `caption()`/note box hardcodes dark ink text. If you give it a dark `bg:` to sit on a dark image, the text vanishes and it renders as an empty bordered box. **Over dark images, keep the DEFAULT light (white) caption box** — a small white note reads fine on dark art. (Bit ANIMA twice: Vol.01 Golden Age + Vol.02 Rain & Glass.)
- **`place()`'d captions/credits collide with flow text.** A credit dropped at `place(bottom+right, dy:-22mm)` happily overprints the body paragraph that flows into the same zone. Put credits in a region with no flowing text (e.g. `top+left` over the image scrim), and ALWAYS verify the placed element zoomed.
- **Exploded/indented diagram boxes cramp text.** Diagonally indenting a stack (`pad(left: i*6mm)` + shrinking width) starves later boxes and forces ugly wraps in a narrow column. Prefer **uniform full-width boxes** (`layerstack` in the template) for legibility — the numbered order already reads as a stack.
- **No `color.lightness` field access** in current Typst — pass explicit per-row text colours into a generator instead of computing contrast.

## AI image gen — local, free, original (`reference/aigen_xl.py` + `driver.py` + `cutout.py`)
**Use SDXL anime (`cagliostrolab/animagine-xl-4.0`) for newsstand-grade fidelity** — the
big quality jump over SD1.5. `reference/aigen.py` is the older SD1.5 recipe; prefer
`aigen_xl.py`. Hard-won gotchas, all baked into the reference scripts:
- **The all-black/NaN bug on Apple MPS is caused by `enable_attention_slicing()`, NOT the
  dtype and NOT the VAE.** (The old "use fp32" advice is the *slow trap* — fp32 is correct
  but the ~14GB model swap-thrashes a 16GB Mac → ~50 min/image.) **WORKING FAST CONFIG:
  fp16 UNet + `pipe.upcast_vae()` (VAE→fp32) + NO attention slicing → ~3 min/image, full
  colour, fits 16GB.** Scheduler = Euler-a, cfg ~6, 28 steps, quality prefix
  `"masterpiece, high score, great score, absurdres"`.
- **Generate each image in its own process** (`reference/driver.py`). A persistent pipeline
  accumulates MPS memory across images and *stalls* mid-batch. The driver is self-healing:
  per-image 8-min timeout + retry + verify (`img.getextrema()` ≠ flat, size == upscaled).
- Generate ~1024px then **Lanczos-upscale 1.7×** (`ANIMA_UPSCALE`) for print crispness.
  CLIP truncates prompts >77 tokens → front-load the subject. `reference/cutout.py`
  (rembg `isnet-anime`) makes transparent cut-out figures for clean editorial placement.
- Confirm the model id still exists (HF removes repos): `curl -s -o /dev/null -w "%{http_code}"
  https://huggingface.co/api/models/<id>` → want 200.
- **Original prompts only — generic archetypes, never named IP characters/series.** This is
  also the *licensing solution*: every pixel is yours → the issue is freely publishable.

---

## Worked example — *ANIMA*, a five-volume bookazine series built with this skill
**ANIMA, Volume One** ("The Story of Anime"): a 19-page original-IP bookazine built to global
newsstand quality, benchmarked frame-by-frame against *ImagineFX Presents: The Story of Anime*.
Preview pages are in the repository README. What made it work:
- **Reusable design system** (the ancestor of `reference/template.typ`): `leaf` (page scaffold w/ vertical edge tab +
  page-number tab + running head), `ftitle`/`brush`/`kicker`/`pull` (typography), `framed`
  (bordered image + drop shadow), `caption` (typewriter note box), plus info-design generators
  `xsheet`, `spacingdots`, `tline`, `pstep`. Sections are **colour-zoned** (one hue each).
- **Imagery, all ownable:** 12 original SDXL key visuals (Animagine XL 4.0) + hand-authored
  Typst infographics (century timeline, on-twos x-sheet, eased-vs-linear spacing dots,
  8-stage pipeline, colour-key swatches) + original criticism/history text.
- Fonts (OFL): Archivo (masthead/UI), Anton (display), Newsreader (body serif), Space Mono
  (captions), Caveat (brush accents).
**ANIMA, Volume Two** ("Light & Time"), a 19-page
issue proving the format is a **repeatable series**. Two-part arc (Light / Time). Adds four
reusable info-design generators now in `reference/template.typ`: **`colorscript`** (a film's
emotional colour timeline), **`depthlayers`** (aerial-perspective depth bands), **`layerstack`**
(exploded compositing/satsuei stack — uniform full-width boxes), **`swatchrows`** (palette→meaning).

## Producing a SERIES / many issues (the repeatable Vol.N recipe)
The engine is built once; each new issue is mostly prompts + copy. To spin up Vol.N:
1. **Sibling folder** `<brand>-volN/`: copy `aigen_xl.py` + `driver.py` + `cutout.py`,
   make `src/ img/ build/`. For fonts, just point `--font-path` at this skill's bundled
   `assets/fonts-ttf/` (no symlink needed — symlinks are unreliable on Windows; copy the folder
   in if you prefer it local). Add a `.gitignore` (ignore `build/_*`, `img/*_orig.png`).
2. **`src/jobs.json`** — ~10–12 prompts, **original archetypes only** (no franchise names). Vary
   `seed` per image.
3. **Generate in the background:** `nohup python src/driver.py > build/_gen.log 2>&1 &`. It is
   self-healing (subprocess-per-image + retry + flat/black verify). On a 16 GB Mac it **throttles
   under memory pressure — real times range ~3–33 min/image**, so a full issue's art is a multi-hour
   background job. That is expected and fine; let it run, poll the log for `BATCH COMPLETE`.
4. **Author `src/<brand>N.typ`** on the component engine. While art renders, **test-compile against
   flat placeholder PNGs** (same names/sizes) to catch every Typst error early — don't wait the
   hours only to hit a typo. Then recompile with the real art.
5. **Audit (Cardinal Rule 2): read every page zoomed, fix, recompile.** Folios consecutive from the
   start; captions over dark art stay white; verify placed elements.
6. **Ship:** teasers + teaser PDF from the final build; a Gumroad/store kit; commit.

**Repo hygiene at scale:** the print PDFs are ~50–60 MB each and GitHub warns >50 MB. For a large
back catalogue, consider keeping hi-res `build/*.pdf` local-only (gitignored) and committing source +
`img/` + a compressed web PDF, or moving to Git LFS — decide with the owner before it bloats history.

## Annual-report mode (financial / corporate reports)

Annual reports are a hybrid — numeric & auditable like a business doc, but long, multi-column
and editorial like a magazine. **This skill (Typst) is the right backbone** (pdf-builder
explicitly bows out of 50+ pages and multi-column flow), with two things borrowed from
`pdf-builder`: its **aesthetic-direction** discipline and its **numeric-audit** loop.

Start from **`reference/annual_report.typ`** — it extends the editorial engine with the
financial furniture a report needs and compiles to a polished 7-page A4 report out of the box
(cover, contents, CEO letter, KPI highlights, financial statements + cash flow, section divider,
segment review). The sample company, Meridian Holdings, is fictional — but its figures **foot**:
segments sum to the group, the letter's claims match the tables, every YoY % ties.

- **Components added:** `kpicard`/`kpirow` (metric + YoY delta; `good:` sets the colour separately
  from the arrow, because falling leverage is ▼ but good), `fintable` + `frow`/`fhead`
  (income-statement table, right-aligned mono figures, bold totals, `(parenthesised)` negatives),
  `yoyrow` (comparison row; type the Δ **with its sign** and set `good:` — never infer good/bad from the sign), `barchart` (pure-Typst vertical bars),
  `mixbar` (horizontal segment mix + % legend), `signature` (CEO letter close), `divider`
  (full-page section opener), `sourceline` (footnoted audit source under every figure).
- **Two aesthetic directions** (ported from `pdf-builder/aesthetic-directions/`): set
  `DIRECTION` at the top to `"institutional-classic"` (oxford-navy + serif, restrained) or
  `"luxury-refined"` (charcoal + gold, generous whitespace). One line restyles the whole report.
  Both verified rendering correctly.
- **Contents page numbers are READ, never typed.** Put `#metadata(none) <label>` at the top of each
  section and let the TOC call `counter(page).at(locate(<label>))`. A typed TOC drifts the moment a
  page is added — the shipped template once said p.09 for a section on page 6.
- **THE AUDIT RULE (non-negotiable for reports):** every figure is typed as a **string you paste
  from the audited source** — no computed/rounded numbers in the layout. After each compile, render
  back to PNG @300 DPI and **read every numeric table zoomed-in**: confirm each total foots, each
  YoY % ties, each footnote matches source. Wrong numbers in an annual report are a disaster the
  pretty layout will happily hide.
- **Why Typst over HTML/CSS here:** reliable page breaks across dozens of pages, automatic TOC /
  running heads / folios / footnotes, and real multi-column flow — exactly what CSS paged-media is
  fiddly at and what a long report lives on.

Compile: `typst compile annual_report.typ AR.pdf --font-path <skill>/assets/fonts-ttf --root .`

## The meta-lesson
Pick the engine from the *job* (editorial & long-form → Typst; short numeric one-pagers/decks →
`pdf-builder`), build with flow not coordinates, and **verify every page by actually viewing it
zoomed-in before claiming it's good.** A magazine or report is one of the few deliverables where the
model can genuinely see and check its own output — so there is no excuse for shipping overlaps,
empty pages, or numbers that don't foot.
