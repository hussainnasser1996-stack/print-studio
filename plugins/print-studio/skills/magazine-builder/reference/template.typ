// ============================================================================
//  EDITORIAL KIT — a print-grade magazine / bookazine template for Typst
//  Part of Print Studio
//
//  Compile:  typst compile template.typ out.pdf --font-path fonts --root .
//  Fonts (all free / OFL): Archivo, Anton, Newsreader, Space Mono, Caveat.
//  Everything below the CONFIG block is the reusable component library — you
//  rarely need to touch it. Edit CONFIG to rebrand; write pages at the bottom.
// ============================================================================

// =========================== CONFIG — EDIT ME ===============================
#let BRAND   = "ATLAS"                    // masthead word
#let TAGLINE = "THE CRAFT QUARTERLY"      // mono sub-line under masthead

// palette — swap these six hex values to fully rebrand the issue
#let ink      = rgb("#16130E")            // near-black text
#let paper    = rgb("#F4EEE2")            // default page
#let cream    = rgb("#FBF7EE")            // lighter page
#let accent   = rgb("#E0392A")            // signature / primary accent
#let c2       = rgb("#27407A")            // section colour 2
#let c3       = rgb("#1C857C")            // section colour 3
#let c4       = rgb("#D99A1C")            // section colour 4
#let c5       = rgb("#B83069")            // section colour 5
#let c6       = rgb("#5B3A86")            // section colour 6

// type — change the family names to restyle (run `typst fonts` to see options)
#let bodyfont = "Newsreader 16pt"
#let sans     = "Archivo"
#let display  = "Anton"
#let mono     = "Space Mono"
#let script   = "Caveat"

// trim size (page). A4 = 210×297mm; this is a bookazine ratio.
#let PW = 210mm
#let PH = 286mm
// ============================================================================

#set document(title: BRAND, author: BRAND)
#set page(width: PW, height: PH, margin: 0pt)

// ------------------------------------------------------------- components ----

// Big condensed display title (with the Anton line-gap fix baked in)
#let ftitle(t, col: ink, size: 50pt) = {
  set text(font: display, fill: col, size: size, top-edge: "cap-height",
           bottom-edge: "baseline")
  set par(leading: 0.14em)
  upper(t)
}

// Brush-script accent head
#let brush(t, col: accent, size: 40pt) = text(font: script, weight: 700,
  size: size, fill: col)[#t]

// Mono kicker / eyebrow
#let kicker(t, col) = text(font: mono, weight: 700, size: 8.5pt,
  tracking: 3pt, fill: col)[#upper(t)]

// Small-caps running word
#let runword(t, col) = text(font: sans, weight: 800, size: 8pt, tracking: 3pt,
  fill: col)[#upper(t)]

// Pull quote
#let pull(q, col) = {
  set par(leading: 0.5em)
  text(font: bodyfont, style: "italic", weight: 600, size: 21pt, fill: col)[“#q”]
}

// Typewriter caption box (overlaid mono note)
#let caption(body, col: ink, bg: rgb("#FFFFFFE8")) = box(fill: bg,
  stroke: 0.7pt + col, inset: 6.5pt, radius: 1.5pt,
  text(font: mono, size: 6.8pt, fill: ink, baseline: 0pt)[
    #set par(leading: 0.55em); #body])

// Framed image: thin border + soft drop shadow + optional rotation
#let framed(path, w, h, border: white, bw: 2.4pt, rot: 0deg) = {
  rotate(rot, box[
    #place(top + left, dx: 1.7mm, dy: 1.9mm,
      rect(width: w, height: h, fill: rgb(0, 0, 0, 60), radius: 1.5pt))
    #box(stroke: bw + border, radius: 1.5pt, clip: true,
      image(path, width: w, height: h, fit: "cover"))
  ])
}

// Vertical edge tab (section ribbon on the outer margin)
#let edgetab(label, col) = place(top + right, dx: 0pt, dy: 26mm,
  rotate(90deg, origin: top + right,
    box(fill: col, inset: (x: 7mm, y: 2.6mm), radius: (bottom-right: 2pt))[
      #text(font: sans, weight: 800, size: 8pt, tracking: 2.6pt, fill: white)[
        #upper(label)]]))

// Page-number tab (outer-bottom corner)
#let folio(n, col) = place(bottom + right, dx: 0pt, dy: 0pt,
  box(fill: col, inset: (x: 5mm, y: 3mm), radius: (top-left: 3pt))[
    #text(font: sans, weight: 800, size: 9pt, fill: white)[#n]])

// Tiny running header (brand + section)
#let runhead(section, col) = place(top + left, dx: 15mm, dy: 9mm,
  grid(columns: (auto, 1fr), column-gutter: 4mm, align: horizon,
    text(font: sans, weight: 900, size: 8.5pt, tracking: 2pt, fill: ink)[#BRAND],
    runword(section, col)))

// Standard editorial page scaffold — wrap your page body in this.
#let leaf(section: "", col: accent, n: 1, fill: paper, head: true, body) = page(
  fill: fill, margin: 0pt)[
  #edgetab(section, col)
  #folio(n, col)
  #if head { runhead(section, col) }
  #pad(top: 17mm, bottom: 14mm, left: 15mm, right: 19mm, body)
]

// ---- info-design: linear-vs-eased spacing dots (a sample data graphic) ----
#let spacingdots(col) = {
  let lin = (0, 14, 28, 42, 56, 70, 84, 98)
  let eas = (0, 4, 11, 24, 46, 68, 85, 98)
  box(width: 100%)[
    #place(top + left, dy: 0mm, text(font: mono, size: 6.5pt, fill: ink)[LINEAR])
    #for x in lin { place(top + left, dx: (15 + x * 0.9) * 1mm, dy: 5mm,
      circle(radius: 1.6mm, fill: col)) }
    #place(top + left, dy: 14mm, text(font: mono, size: 6.5pt, fill: ink)[EASED])
    #for x in eas { place(top + left, dx: (15 + x * 0.9) * 1mm, dy: 19mm,
      circle(radius: 1.6mm, fill: accent)) }
    #v(26mm)
  ]
}

// ---- info-design: COLOUR SCRIPT — a film's emotional colour timeline ----
#let colorscript(cols, labels) = {
  box(width: 100%)[
    #grid(columns: (1fr,) * cols.len(), rows: 18mm,
      ..cols.map(c => rect(width: 100%, height: 100%, fill: c)))
    #v(1mm)
    #grid(columns: (1fr,) * cols.len(),
      ..labels.map(l => align(center, text(font: mono, size: 6pt, fill: ink)[#l])))
    #v(1mm)
    #line(length: 100%, stroke: 0.5pt + ink)
    #grid(columns: (auto, 1fr, auto),
      text(font: mono, size: 6pt, fill: ink)[OPEN],
      align(center, text(font: mono, size: 6pt, fill: rgb("#00000077"))[← read left to right →]),
      text(font: mono, size: 6pt, fill: ink)[CLOSE])
  ]
}

// ---- info-design: AERIAL PERSPECTIVE — receding depth in tints ----
// bands = ((fill, LABEL, note, text-col, note-col), …) front→far
#let depthlayers(bands) = box(width: 100%)[
  #stack(spacing: 0pt, ..bands.map(b => block(width: 100%, height: 15mm,
    fill: b.at(0), inset: (x: 5mm, y: 3mm))[
    #grid(columns: (1fr, auto), align: (left + horizon, right + horizon),
      text(font: sans, weight: 800, size: 9pt, fill: b.at(3))[#b.at(1)],
      text(font: mono, size: 6.5pt, fill: b.at(4))[#b.at(2)])]))
]

// ---- info-design: EXPLODED LAYER STACK (e.g. compositing / satsuei) ----
// lyr = ((TITLE, note, fill-colour), …) — uniform full-width boxes (legible)
#let layerstack(lyr, foot: "") = box(width: 100%)[
  #stack(spacing: 2.6mm, ..lyr.enumerate().map(p => {
    let i = p.at(0); let l = p.at(1)
    block(width: 100%, fill: l.at(2), radius: 1.5pt, inset: (x: 5mm, y: 3mm))[
      #grid(columns: (8mm, 1fr), column-gutter: 3mm, align: horizon,
        text(font: display, size: 16pt, fill: rgb("#FFFFFFCC"))[#str(i + 1)],
        [#text(font: sans, weight: 800, size: 9.5pt, fill: white)[#l.at(0)]
         #h(2.5mm) #text(font: mono, size: 6.3pt, fill: rgb("#FFFFFFCC"))[#l.at(1)]])]
  }))
  #if foot != "" { v(2mm); align(center, text(font: mono, size: 6pt, fill: rgb("#00000088"))[#foot]) }
]

// ---- info-design: PALETTE → MEANING swatch rows ----
// rows = ((colour, WORD, note), …)
#let swatchrows(rows) = grid(columns: (1fr, 1fr), column-gutter: 6mm, row-gutter: 4mm,
  ..rows.map(r => grid(columns: (12mm, 1fr), column-gutter: 3mm, align: horizon,
    rect(width: 12mm, height: 12mm, fill: r.at(0), radius: 1pt),
    [#text(font: sans, weight: 800, size: 9pt, fill: ink)[#r.at(1)] \
     #text(font: mono, size: 6.3pt, fill: rgb("#00000099"))[#r.at(2)]])))

// ------------- DENSITY "FURNITURE" (proven in ANIMA Vol.3–5; from the benchmark) ----
// The competitor magazines win on density: every page carries title + body + 2–4
// captioned images + a sidebar/data-bar/fact-stamp/pull-quote. Use these to match it.

// polaroid — thick white border + tilt (the "instant photo" look, scatter & overlap)
#let polaroid(path, w, h, rot: -2deg) = framed(path, w, h, border: white, bw: 4.5pt, rot: rot)
// highlighter deck — the standfirst as bold text on an accent block
#let deck(t, col) = block(width: 100%, fill: col, inset: (x: 5mm, y: 3.2mm), radius: 1.5pt,
  text(font: sans, weight: 700, size: 10pt, fill: white)[#t])
// data bar — rule-separated LABEL value row (profile furniture: e.g. director/studio/year)
#let databar(items, col) = block(width: 100%, inset: (y: 2.6mm),
  stroke: (top: 0.9pt + col, bottom: 0.9pt + col),
  grid(columns: (1fr,) * items.len(), column-gutter: 4mm, align: horizon,
    ..items.map(it => text(size: 7.5pt)[#text(font: mono, weight: 700, fill: col)[#upper(it.at(0)) ]#text(font: sans, weight: 700, fill: ink)[#it.at(1)]])))
// fact stamp — rotated circular "did you know" badge (col is POSITIONAL — pass plainly)
#let factstamp(label, body, col, rot: -7deg) = rotate(rot,
  box(width: 35mm, height: 35mm, radius: 50%, fill: col, inset: 4.5mm, align(center + horizon)[
    #text(font: sans, weight: 900, size: 7.5pt, fill: white, tracking: 1.2pt)[#upper(label)]
    #v(1.2mm) #text(font: bodyfont, size: 7pt, fill: rgb("#FFFFFFEE"))[#body]]))
// big pull-quote — oversized quote mark + line + attribution
#let bigquote(q, attrib, col) = grid(columns: (15mm, 1fr), column-gutter: 3mm,
  align: (left + top, left + top), text(font: display, size: 58pt, fill: col)[“],
  [#text(font: bodyfont, style: "italic", weight: 600, size: 19pt, fill: ink)[#q]
   #v(2mm) #text(font: mono, size: 7.5pt, fill: col)[— #attrib]])
// profile sidebar — dark vertical panel w/ heading + note
#let profileside(title, body, col: ink) = block(width: 100%, fill: col, radius: 2pt, inset: 6mm)[
  #text(font: mono, weight: 700, size: 7pt, tracking: 2pt, fill: rgb("#FFFFFFAA"))[#upper(title)]
  #v(2mm) #line(length: 28%, stroke: 1pt + rgb("#FFFFFF55")) #v(2.5mm)
  #set par(leading: 0.6em); #text(font: bodyfont, size: 8.5pt, fill: rgb("#FFFFFFE0"))[#body]]
// gallery grid — captioned framed thumbnails (directory/gallery furniture)
#let gallerygrid(items, cols: 3, ih: 38mm) = grid(columns: (1fr,) * cols,
  column-gutter: 5mm, row-gutter: 6mm, ..items.map(it => [#framed(it.at(0), 100%, ih)
    #v(1.4mm) #text(font: sans, weight: 800, size: 8pt, fill: ink)[#it.at(1)] \
    #text(font: mono, size: 6.3pt, fill: rgb("#00000099"))[#it.at(2)]]))
// step row — numbered construction steps (tutorial furniture)
#let steprow(steps, col, h: 40mm) = grid(columns: (1fr,) * steps.len(), column-gutter: 5mm,
  ..steps.map(s => box(stroke: 1pt + col, radius: 2pt, inset: 7pt, height: h)[
    #text(font: display, size: 22pt, fill: col)[#s.at(0)] #v(1mm)
    #text(font: sans, weight: 800, size: 8.5pt, fill: ink)[#s.at(1)] #v(1.5mm)
    #text(font: bodyfont, size: 8pt, fill: rgb("#000000AA"))[#s.at(2)]]))
// NOTE: inside a `.map(x => …)` never name the loop var `v` — it shadows Typst's v()
// spacing function. And avoid `align(…+horizon, …)` as the FIRST child of a fixed-height
// box (it eats the vertical space and pushes later children past the border) — flow from
// the top with explicit #v() spacers instead. Both bugs hit ANIMA Vol.4's viseme boxes.

// ------------- MORE INFO-DESIGN GENERATORS (proven across ANIMA Vol.1–5) ----
// timeline row — a dated point on a vertical timeline (a century of X)
#let tline(year, label, col) = grid(columns: (16mm, 5mm, 1fr), column-gutter: 2mm,
  align: (right + horizon, center + horizon, left + horizon),
  text(font: display, size: 13pt, fill: col)[#year], circle(radius: 2mm, fill: col),
  text(font: bodyfont, size: 9pt, fill: ink)[#label])
// x-sheet / timing-sheet — the animator's frame chart (on-twos demo)
#let xsheet() = table(columns: (8mm, 8mm, 1fr), rows: 5mm, stroke: 0.4pt + rgb("#00000044"),
  align: (center, center, left), inset: 1.5pt,
  fill: (c, r) => if r == 0 { ink } else if calc.odd(r) { rgb("#00000008") } else { white },
  text(font: mono, size: 6pt, fill: white)[FR], text(font: mono, size: 6pt, fill: white)[CEL],
  text(font: mono, size: 6pt, fill: white)[ACTION],
  ..range(1, 16).map(i => { let cel = if calc.odd(i) { str(int((i + 1) / 2)) } else { "·" }
    (text(font: mono, size: 6pt)[#i],
     text(font: mono, size: 6pt, fill: if calc.odd(i) { accent } else { rgb("#00000055") })[#cel],
     text(font: mono, size: 6pt, fill: rgb("#00000077"))[#if i == 1 [key] else if i == 7 [key] else if i == 13 [key] else []])
  }).flatten())
// speed-lines — a motion burst trailing a moving object
#let speedlines(col) = box(width: 100%, height: 30mm)[
  #for i in range(22) { let yy = (2 + i * 1.2) * 1mm; let ww = (20 + calc.rem(i * 13, 40)) * 1mm
    place(left + top, dy: yy, line(start: (0mm, 0mm), end: (ww, 0mm), stroke: (paint: col, thickness: 0.8pt))) }
  #place(right + horizon, dx: -2mm, circle(radius: 6mm, fill: col))]
// background-plane stack — how a flat cel gets depth (back→front)
#let bglayers(lyr) = box(width: 100%)[
  #stack(spacing: 2.6mm, ..lyr.enumerate().map(p => { let i = p.at(0); let l = p.at(1)
    block(width: 100%, fill: l.at(2), radius: 1.5pt, inset: (x: 5mm, y: 3mm))[
      #grid(columns: (8mm, 1fr), column-gutter: 3mm, align: horizon,
        text(font: display, size: 16pt, fill: rgb("#FFFFFFCC"))[#str(i + 1)],
        [#text(font: sans, weight: 800, size: 9.5pt, fill: white)[#l.at(0)]#h(2.5mm)#text(font: mono, size: 6.3pt, fill: rgb("#FFFFFFCC"))[#l.at(1)]])]}))]
// visemes — mouth-shape row for lip-sync (note the fixed-box flow above)
#let visemes(m) = grid(columns: (1fr,) * m.len(), column-gutter: 4mm,
  ..m.map(vm => box(stroke: 1pt + ink, radius: 2pt, inset: 6pt, height: 38mm)[
    #set block(spacing: 0pt)
    #v(3mm)
    #align(center, box(width: 100%, height: 11mm, align(center + horizon, ellipse(width: vm.at(2), height: vm.at(3), fill: accent))))
    #v(2.5mm) #align(center, text(font: display, size: 16pt, fill: ink)[#vm.at(0)])
    #v(2.5mm) #align(center, text(font: mono, size: 6.5pt, fill: rgb("#00000099"))[#vm.at(1)])]))
// For an icon'd pipeline (idea→screen), use steprow, or a card grid with image() icons.

// ============================================================================
//  COVER  — full-bleed hero + masthead. img/cover.jpg ships as an original
//  placeholder (generated, free to use) — replace it with your own art.
// ============================================================================
#page(fill: ink, margin: 0pt)[
  #place(top + left, image("/img/cover.jpg", width: PW, height: PH, fit: "cover"))
  #place(top + left, rect(width: PW, height: 98mm,
    fill: gradient.linear(rgb(6, 7, 12, 240), rgb(6, 7, 12, 0), angle: 90deg)))
  #place(bottom + left, rect(width: PW, height: 120mm,
    fill: gradient.linear(rgb(8, 8, 12, 0), rgb(8, 8, 12, 200), angle: 90deg)))

  #place(top + center, dy: 15mm,
    text(font: sans, weight: 900, size: 92pt, fill: cream, tracking: 10pt)[#BRAND])
  #place(top + center, dy: 47mm,
    text(font: mono, weight: 700, size: 11pt, tracking: 7pt, fill: accent)[#TAGLINE])
  #place(top + center, dy: 55mm, line(length: 54mm, stroke: 1.2pt + cream))

  #place(top + center, dy: 61mm,
    box(fill: accent, inset: (x: 3mm, y: 1.6mm))[
      #text(font: sans, weight: 900, size: 9pt, fill: white, tracking: 1pt)[VOLUME ONE]])

  #place(bottom + left, dx: 13mm, dy: -50mm)[
    #set par(leading: 0.5em)
    #text(font: display, size: 33pt, fill: cream)[YOUR COVER LINE]
    #v(2mm)
    #text(font: bodyfont, style: "italic", size: 14pt, fill: rgb("#F4EEE2CC"))[
      A one-line deck that sells the issue.]
  ]
]

// ============================================================================
//  EXAMPLE PAGE 1 — feature opener (image + kicker + title + body)
// ============================================================================
#leaf(section: "Feature", col: accent, n: 2, fill: paper)[
  #kicker("The Section Eyebrow", accent)
  #v(2mm)
  #ftitle("A Feature Title", col: ink, size: 50pt)
  #v(4mm)
  #grid(columns: (1fr, 1fr), column-gutter: 8mm,
    [
      #set par(justify: true, leading: 0.62em, first-line-indent: 4mm)
      #set text(font: bodyfont, size: 10pt, fill: ink)
      Replace this with your body copy. The #raw("leaf") scaffold gives every page
      consistent margins, an edge tab, a folio and a running header automatically —
      you only write the content. Long text reflows safely because this kit uses
      Typst flow layout, never hand-placed coordinates.

      Add as many paragraphs as you like; the column simply continues. Use the
      components above to build editorial rhythm: a #raw("pull") quote to breathe, a
      #raw("caption") box over an image, a #raw("kicker") to open a section.
    ],
    [
      #framed("img/cover.jpg", 100%, 120mm)  // swap for your image path
      #v(3mm)
      #caption[A typewriter caption sits over or beside the art — credit, note, or aside.]
    ])
  #v(6mm)
  #pull("A pull quote earns its place when the sentence is worth stopping for.", accent)
]

// ============================================================================
//  EXAMPLE PAGE 2 — info-design / data page
// ============================================================================
#leaf(section: "Data", col: c2, n: 3, fill: cream)[
  #kicker("An Information-Design Page", c2)
  #v(2mm)
  #ftitle("Show, Don't Tell", col: c2, size: 50pt)
  #v(8mm)
  #spacingdots(c2)
  #v(4mm)
  #set text(font: bodyfont, size: 10pt, fill: ink)
  #set par(justify: true, leading: 0.62em)
  Hand-authored graphics like the dot diagram above are what make a document read as a
  *magazine* and not a report. Swap the data arrays in #raw("spacingdots") for your own,
  or build new generators the same way. The components above also include colour scripts, depth
  layers, layer stacks and swatch rows.
]

// to add pages: copy a #leaf(...) block, bump n, pick a section colour (c2..c6).
