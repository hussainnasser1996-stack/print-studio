// ============================================================================
//  ANNUAL REPORT KIT — premium, print-ready annual / financial reports in Typst
//  Part of Print Studio. Extends the editorial magazine engine
//  (template.typ) with the FINANCIAL-DOCUMENT furniture a real annual report
//  needs: KPI cards, financial statement tables, multi-year (YoY) comparison,
//  pure-Typst bar charts + segment-mix bars, a CEO letter layout, footnoted
//  sources (auditability), section dividers and a corporate cover.
//
//  Two aesthetic DIRECTIONS are baked in (ported from pdf-builder):
//  "institutional-classic" (oxford navy + serif, restrained) and
//  "luxury-refined" (charcoal + gold, generous whitespace). Switch with one line.
//
//  Compile (point --font-path at the skill's bundled fonts):
//    typst compile annual_report.typ AR.pdf \
//      --font-path /path/to/magazine-builder/assets/fonts-ttf --root .
//
//  AUDIT RULE (from pdf-builder, non-negotiable for reports): every figure here
//  is typed as a STRING you paste from the audited source — no silent rounding.
//  After each compile, render back to PNG @300DPI and read every numeric table
//  zoomed-in; confirm each total, each YoY %, each footnote ties to source.
// ============================================================================

// ============================ CONFIG — EDIT ME ==============================
#let COMPANY  = "MERIDIAN HOLDINGS"
#let REPORT   = "ANNUAL REPORT"
#let FY       = "2025"
#let DIRECTION = "institutional-classic"   // or "luxury-refined"

// trim — A4 portrait is the annual-report standard
#let PW = 210mm
#let PH = 297mm

// ---- aesthetic presets (palette + type per direction) ----------------------
#let PRESET = (
  "institutional-classic": (
    ink: rgb("#14213D"), paper: rgb("#FCFCFA"), panel: rgb("#F1EFE9"),
    accent: rgb("#1B3A6B"), gold: rgb("#9A7B4F"), pos: rgb("#1C6B4A"), neg: rgb("#A33A2E"),
    body: "Newsreader 16pt", sans: "Archivo", display: "Anton", mono: "Space Mono",
  ),
  "luxury-refined": (
    ink: rgb("#1C1B19"), paper: rgb("#F8F5F0"), panel: rgb("#EEE9E0"),
    accent: rgb("#1C1B19"), gold: rgb("#B8923E"), pos: rgb("#5E7D52"), neg: rgb("#9A4B3B"),
    body: "Newsreader 16pt", sans: "Archivo", display: "Anton", mono: "Space Mono",
  ),
).at(DIRECTION)

#let ink = PRESET.ink
#let paper = PRESET.paper
#let panel = PRESET.panel
#let accent = PRESET.accent
#let gold = PRESET.gold
#let pos = PRESET.pos
#let neg = PRESET.neg
#let bodyfont = PRESET.body
#let sans = PRESET.sans
#let display = PRESET.display
#let mono = PRESET.mono
// ============================================================================

#set document(title: COMPANY + " " + REPORT + " " + FY, author: COMPANY)
#set page(width: PW, height: PH, margin: 0pt)

// ----------------------------------------------------- core typography -------
#let ftitle(t, col: ink, size: 40pt) = {
  set text(font: display, fill: col, size: size, top-edge: "cap-height", bottom-edge: "baseline")
  set par(leading: 0.16em); upper(t)
}
#let kicker(t, col) = text(font: mono, weight: 700, size: 8.5pt, tracking: 3pt, fill: col)[#upper(t)]
#let runword(t, col) = text(font: sans, weight: 800, size: 8pt, tracking: 3pt, fill: col)[#upper(t)]
#let sourceline(t) = text(font: mono, size: 6pt, fill: rgb("#00000088"))[#t]   // footnote / audit source

// running header + folio + page scaffold (flow layout — long narrative reflows safely)
#let runhead(section, col) = place(top + left, dx: 18mm, dy: 12mm,
  box(width: PW - 36mm,
    grid(columns: (1fr, auto), column-gutter: 4mm, align: horizon,
      text(font: sans, weight: 900, size: 8.5pt, tracking: 2pt, fill: ink)[#COMPANY],
      runword(section, col))))
#let folio(n, col) = place(bottom + center, dy: -9mm,
  text(font: mono, size: 8pt, fill: col)[#n])
#let leaf(section: "", col: accent, n: 1, fill: paper, head: true, body) = page(fill: fill, margin: 0pt)[
  #if head { runhead(section, col) }
  #folio(n, col)
  #pad(top: 22mm, bottom: 16mm, left: 18mm, right: 18mm, body)
]

// ----------------------------------------------- FINANCIAL FURNITURE ---------

// KPI card — big metric + label + YoY delta (arrow + colour). up: true/false/none.
// `good` sets the colour (defaults to `up`): falling leverage is ▼ but good.
#let kpicard(value, label, delta: none, up: true, good: auto) = box(width: 100%, fill: panel,
  radius: 2pt, inset: (x: 5mm, y: 5mm), stroke: (left: 2.5pt + accent))[
  #text(font: display, size: 30pt, fill: ink)[#value]
  #v(1.5mm)
  #text(font: sans, weight: 700, size: 8pt, tracking: 1.5pt, fill: rgb("#00000099"))[#upper(label)]
  #if delta != none [
    #v(1mm)
    #let ok = if good == auto { up } else { good }
    #text(font: mono, weight: 700, size: 8pt, fill: if ok { pos } else { neg })[
      #if up [▲] else [▼] #delta]
  ]
]
#let kpirow(cards) = grid(columns: (1fr,) * cards.len(), column-gutter: 5mm, ..cards)

// Financial-statement row: label + right-aligned mono figures. Returns CELLS
// (spread with `..frow(...)` inside a table). bold=totals.
#let frow(label, vals, bold: false, indent: 0mm) = {
  let w = if bold { 700 } else { 400 }
  (pad(left: indent, text(font: sans, weight: w, size: 8.5pt, fill: ink)[#label]),
   ..vals.map(x => align(right + horizon, text(font: mono, weight: w, size: 8.5pt, fill: ink)[#x])))
}
#let fhead(label, cols) = (
  text(font: mono, weight: 700, size: 7pt, tracking: 1pt, fill: accent)[#upper(label)],
  ..cols.map(c => align(right, text(font: mono, weight: 700, size: 7pt, tracking: 1pt, fill: accent)[#upper(c)])),
)
#let fintable(ncols, ..content) = table(
  columns: (1fr,) + (auto,) * ncols, inset: (x: 3mm, y: 2.4mm), stroke: none,
  align: horizon, ..content)

// YoY comparison row (label | this | prior | Δ). Type delta WITH its sign
// ("+11.4%", "−0.06x"); `good` colours it — a fall in leverage is good.
#let yoyrow(label, this_, prior, delta, good: true, bold: false) = {
  let w = if bold { 700 } else { 400 }
  (text(font: sans, weight: w, size: 8.5pt, fill: ink)[#label],
   align(right, text(font: mono, weight: w, size: 8.5pt, fill: ink)[#this_]),
   align(right, text(font: mono, weight: w, size: 8.5pt, fill: rgb("#00000099"))[#prior]),
   align(right, text(font: mono, weight: 700, size: 8.5pt, fill: if good { pos } else { neg })[#delta]))
}

// Pure-Typst vertical BAR CHART. data = ((label, number), …).
#let barchart(data, col: accent, h: 42mm, unit: "") = {
  let mx = calc.max(..data.map(d => d.at(1)))
  grid(columns: (1fr,) * data.len(), column-gutter: 5mm, align: center,
    ..data.map(d => {
      let bh = d.at(1) / mx * h
      box(width: 100%)[
        #box(width: 100%, height: h + 6mm)[   // headroom so the tallest label clears headings above
          #place(bottom + center)[
            #align(center, text(font: mono, size: 6.8pt, fill: col)[#d.at(1)#unit])
            #v(1.2mm)
            #rect(width: 52%, height: bh, fill: col, radius: (top-left: 1.5pt, top-right: 1.5pt))
          ]
        ]
        #v(1.6mm)
        #align(center, text(font: sans, weight: 700, size: 7.5pt, fill: ink)[#d.at(0)])
      ]
    }))
}

// Horizontal SEGMENT-MIX bar + legend. segs = ((label, number, colour), …).
#let mixbar(segs, h: 10mm) = {
  let tot = segs.map(s => s.at(1)).sum()
  block(width: 100%)[
    #grid(columns: segs.map(s => s.at(1) / tot * 1fr), rows: h,
      ..segs.map(s => rect(width: 100%, height: 100%, fill: s.at(2))))
    #v(2.5mm)
    #grid(columns: (1fr,) * calc.min(segs.len(), 4), row-gutter: 2.5mm, column-gutter: 5mm,
      ..segs.map(s => grid(columns: (4mm, 1fr), column-gutter: 2mm, align: horizon,
        rect(width: 3.4mm, height: 3.4mm, fill: s.at(2), radius: 0.5pt),
        text(font: mono, size: 6.8pt, fill: ink)[#s.at(0) #text(weight: 700)[ #calc.round(s.at(1) / tot * 100)%]])))
  ]
}

// Signature block (CEO letter close)
#let signature(name, title) = {
  text(font: "Caveat", size: 26pt, fill: ink)[#name]
  v(1mm)
  line(length: 38mm, stroke: 0.6pt + ink)
  v(1.5mm)
  text(font: sans, weight: 800, size: 8.5pt, fill: ink)[#upper(name)]
  linebreak()
  text(font: mono, size: 7pt, fill: rgb("#00000099"))[#title]
}

// Full-page SECTION DIVIDER
#let divider(num, title, col: accent) = page(fill: col, margin: 0pt)[
  #place(top + left, dx: 18mm, dy: 24mm, text(font: mono, weight: 700, size: 10pt, tracking: 4pt, fill: rgb("#FFFFFFAA"))[SECTION #num])
  #place(left + horizon, dx: 18mm, text(font: display, size: 64pt, fill: white)[#upper(title)])
  #place(bottom + left, dx: 18mm, dy: -22mm, line(length: 46mm, stroke: 1.2pt + gold))
]

// ============================================================================
//  COVER
// ============================================================================
#page(fill: ink, margin: 0pt)[
  #place(top + left, dx: 18mm, dy: 20mm,
    box(fill: gold, inset: (x: 3mm, y: 1.6mm))[#text(font: sans, weight: 900, size: 9pt, fill: white, tracking: 1pt)[FY #FY]])
  #place(left + horizon, dx: 18mm, dy: -28mm, box(width: PW - 36mm)[
    #set par(leading: 0.2em)
    #text(font: sans, weight: 900, size: 46pt, fill: paper, tracking: 1pt)[#COMPANY]
    #v(3mm)
    #text(font: mono, weight: 700, size: 13pt, tracking: 8pt, fill: gold)[#upper(REPORT) #FY]
  ])
  #place(left + horizon, dx: 18mm, dy: 6mm, line(length: 60mm, stroke: 1.2pt + paper))
  #place(bottom + left, dx: 18mm, dy: -20mm,
    text(font: bodyfont, style: "italic", size: 13pt, fill: rgb("#FFFFFFB0"))[Discipline. Compounding. Trust.])
]

// ============================================================================
//  CONTENTS
// ============================================================================
#leaf(section: "Contents", col: accent, n: 2)[
  #kicker("In this report", gold)
  #v(2mm)
  #ftitle("Contents", size: 40pt)
  #v(8mm)
  #set text(font: bodyfont, size: 11pt, fill: ink)
  // Page numbers are READ from labels, never typed — the TOC cannot drift.
  #let toc = (("01", "Chair & CEO letter", <letter>), ("02", "Performance highlights", <highlights>),
              ("03", "Financial statements", <financials>), ("04", "Segment review", <segments>))
  #stack(spacing: 5mm, ..toc.map(r => grid(columns: (12mm, 1fr, auto), align: horizon,
    text(font: display, size: 16pt, fill: accent)[#r.at(0)],
    text(font: sans, weight: 700, size: 11pt, fill: ink)[#r.at(1)],
    context {
      let pg = counter(page).at(locate(r.at(2))).first()
      text(font: mono, size: 9pt, fill: gold)[p.#if pg < 10 [0]#pg]
    })))
  #v(16mm)
  #line(length: 100%, stroke: 0.6pt + accent)
  #v(6mm)
  #kicker(FY + " at a glance", gold)
  #v(5mm)
  #grid(columns: (1fr, 1fr, 1fr), column-gutter: 8mm,
    ..(("4", "operating segments, all profitable"), ("11.4%", "revenue growth, up from 8.8% in FY24"),
       ("27.2%", "operating margin, up 110 bps")).map(f => [
      #text(font: display, size: 34pt, fill: accent)[#f.at(0)]
      #v(2mm)
      #text(font: bodyfont, size: 10pt, fill: ink)[#f.at(1)]
    ]))
  #v(14mm)
  #kicker("About this report", gold)
  #v(4mm)
  #grid(columns: (1fr, 1fr), column-gutter: 9mm, [
    #set par(justify: true, leading: 0.62em)
    #set text(font: bodyfont, size: 9.5pt, fill: ink)
    This report covers the financial year to 31 December #FY. Every figure is taken from
    the audited consolidated financial statements; where a number appears in more than one
    place, it is the same number, typed once from the same source.
  ], [
    #set par(justify: true, leading: 0.62em)
    #set text(font: bodyfont, size: 9.5pt, fill: ink)
    Meridian Holdings is a fictional company. It exists to show the layout — the cover,
    letter, KPI cards, statements and charts — that this template produces out of the box.
    Replace the CONFIG block and the figures with your own audited source.
  ])
]

// ============================================================================
//  CEO LETTER — long-form flowing narrative (Typst flow handles any length)
// ============================================================================
#leaf(section: "Leadership", col: accent, n: 3)[
  #metadata(none) <letter>
  #kicker("Chair & Chief Executive", gold)
  #v(2mm)
  #ftitle("A year of disciplined growth", size: 34pt)
  #v(5mm)
  #set par(justify: true, leading: 0.62em, first-line-indent: 4mm)
  #set text(font: bodyfont, size: 10pt, fill: ink)
  #grid(columns: (1fr, 1fr), column-gutter: 9mm, [
    Dear shareholders, #FY was a year in which our strategy proved its resilience.
    Revenue rose 11.4% to \$4.82 billion on the strength of recurring demand, while
    disciplined cost management lifted our operating margin by 110 basis points to
    27.2%. This is the compounding we have promised you — unglamorous, repeatable, and
    durable.

    Every one of our four segments grew. Services, now 29% of the group, grew fastest at
    20.3%, and for the first time contributed more than a quarter of operating profit.
    Platform remains the engine of the business, but its share of revenue has fallen for
    a third year, and that is by design: a broader base is a safer one.

    We turned 70 cents of every dollar of operating profit into free cash flow, reduced
    net debt to 0.41 times EBITDA, and raised the dividend by 16.4% to \$1.28 per share.
    Our balance sheet has never been stronger, and we intend to keep it that way.
  ], [
    #block(inset: (left: 5mm, y: 2mm), stroke: (left: 2pt + gold))[
      #set par(first-line-indent: 0mm, justify: false)
      #text(font: bodyfont, style: "italic", size: 14pt, fill: accent)[
        A broader base is a safer one. We would rather grow every segment a little than
        one segment a lot.]
    ]
    #v(4mm)

    Our priorities for the year ahead are unchanged. First, protect the core: Platform
    customers renew because the product is dependable, and we will not trade that for
    speed. Second, reinvest behind the highest-returning segments, led by Services.
    Third, return surplus capital to owners, through the dividend and, where the price is
    right, through buybacks.

    None of this happens without our people, whose craft turns strategy into results. On
    behalf of the Board, thank you — to our colleagues, our customers, and to you, our
    shareholders, for your continued trust.

    #v(8mm)
    #set par(first-line-indent: 0mm)
    #signature("Amara Vance", "Chair & Chief Executive Officer")
  ])
]

// ============================================================================
//  PERFORMANCE HIGHLIGHTS — KPI cards + bar chart
// ============================================================================
#leaf(section: "Highlights", col: accent, n: 4, fill: paper)[
  #metadata(none) <highlights>
  #kicker("Performance highlights", gold)
  #v(2mm)
  #ftitle("The year in numbers", size: 34pt)
  #v(6mm)
  #kpirow((
    kpicard("$4.82B", "Total revenue", delta: "11.4%", up: true),
    kpicard("$1.31B", "Operating profit", delta: "16.1%", up: true),
    kpicard("27.2%", "Operating margin", delta: "110 bps", up: true),
  ))
  #v(5mm)
  #kpirow((
    kpicard("$3.41", "Earnings / share", delta: "14.0%", up: true),
    kpicard("$0.92B", "Free cash flow", delta: "8.7%", up: true),
    kpicard("0.41x", "Net debt / EBITDA", delta: "0.06x", up: false, good: true),
  ))
  #v(9mm)
  #grid(columns: (1.3fr, 1fr), column-gutter: 10mm, align: top,
    [
      #runword("Revenue, $B", accent)
      #v(4mm)
      #barchart((("FY21", 3.10), ("FY22", 3.52), ("FY23", 3.98), ("FY24", 4.33), ("FY25", 4.82)),
        col: accent, h: 40mm)
      #v(2mm)
      #sourceline("Source: audited consolidated financial statements, Note 3. Figures in US$ billions.")
    ],
    [
      #runword("Revenue by segment", accent)
      #v(4mm)
      #mixbar(((("Platform", 2.55, accent), ("Services", 1.42, gold),
                ("Hardware", 0.61, pos), ("Other", 0.24, rgb("#7A7A7A")))))
      #v(4mm)
      #set text(font: bodyfont, size: 9pt, fill: ink)
      #set par(leading: 0.6em, justify: true)
      Platform remains the engine of the group, now 53% of revenue, while Services
      compounds fastest. Concentration risk continues to fall year over year.
    ])
]

// ============================================================================
//  FINANCIAL STATEMENTS — income statement + YoY comparison (auditable)
// ============================================================================
#leaf(section: "Financials", col: accent, n: 5, fill: paper)[
  #metadata(none) <financials>
  #kicker("Consolidated income statement", gold)
  #v(2mm)
  #ftitle("Financial statements", size: 30pt)
  #v(6mm)
  #fintable(2,
    ..fhead("US$ millions", ("FY25", "FY24")),
    table.hline(stroke: 0.8pt + accent),
    ..frow("Revenue", ("4,820", "4,328")),
    ..frow("Cost of sales", ("(2,612)", "(2,431)")),
    table.hline(stroke: 0.3pt + rgb("#00000044")),
    ..frow("Gross profit", ("2,208", "1,897"), bold: true),
    ..frow("Operating expenses", ("(898)", "(769)")),
    table.hline(stroke: 0.3pt + rgb("#00000044")),
    ..frow("Operating profit", ("1,310", "1,128"), bold: true),
    ..frow("Net finance cost", ("(86)", "(94)")),
    ..frow("Tax", ("(289)", "(244)")),
    table.hline(stroke: 0.8pt + accent),
    ..frow("Profit for the year", ("935", "790"), bold: true),
  )
  #v(3mm)
  #sourceline("Extracted from the audited consolidated financial statements. Prior year restated for IFRS 18.")

  #v(10mm)
  #kicker("Year-on-year comparison", gold)
  #v(4mm)
  #table(columns: (1fr, auto, auto, auto), inset: (x: 3mm, y: 2.6mm), stroke: none, align: horizon,
    ..fhead("Key metric", ("FY25", "FY24", "Δ YoY")),
    table.hline(stroke: 0.8pt + accent),
    ..yoyrow("Revenue ($M)", "4,820", "4,328", "+11.4%"),
    ..yoyrow("Operating profit ($M)", "1,310", "1,128", "+16.1%"),
    ..yoyrow("EPS ($)", "3.41", "2.99", "+14.0%"),
    ..yoyrow("Dividend / share ($)", "1.28", "1.10", "+16.4%"),
    ..yoyrow("Net debt / EBITDA", "0.41x", "0.47x", "−0.06x", good: true, bold: true),
  )

  #v(10mm)
  #kicker("Cash flow summary", gold)
  #v(4mm)
  #fintable(3,
    ..fhead("US$ millions", ("FY25", "FY24", "Δ YoY")),
    table.hline(stroke: 0.8pt + accent),
    ..frow("Cash generated from operations", ("1,150", "1,060", "+8.5%")),
    ..frow("Capital expenditure", ("(230)", "(214)", "+7.5%")),
    table.hline(stroke: 0.8pt + accent),
    ..frow("Free cash flow", ("920", "846", "+8.7%"), bold: true),
  )
  #v(3mm)
  #sourceline("Consolidated cash flow statement. Free cash flow = cash from operations less capital expenditure; 70% of operating profit.")
]

// ============================================================================
//  SECTION DIVIDER example (use between major parts)
// ============================================================================
#divider("04", "Segment review", col: accent)

// ============================================================================
//  SEGMENT REVIEW — segment table that FOOTS to the income statement
// ============================================================================
#leaf(section: "Segments", col: accent, n: 7, fill: paper)[
  #metadata(none) <segments>
  #kicker("Segment review", gold)
  #v(2mm)
  #ftitle("Four engines, all growing", size: 30pt)
  #v(6mm)
  #fintable(5,
    ..fhead("US$ millions", ("Rev FY25", "Rev FY24", "Growth", "Op. profit", "Margin")),
    table.hline(stroke: 0.8pt + accent),
    ..frow("Platform", ("2,550", "2,330", "9.4%", "820", "32.2%")),
    ..frow("Services", ("1,420", "1,180", "20.3%", "360", "25.4%")),
    ..frow("Hardware", ("610", "590", "3.4%", "70", "11.5%")),
    ..frow("Other", ("240", "228", "5.3%", "60", "25.0%")),
    table.hline(stroke: 0.8pt + accent),
    ..frow("Group", ("4,820", "4,328", "11.4%", "1,310", "27.2%"), bold: true),
  )
  #v(3mm)
  #sourceline("Segment note 4 to the audited financial statements. Segment totals foot to the consolidated income statement on page 5.")
  #v(10mm)
  #grid(columns: (1fr, 1fr), column-gutter: 10mm, align: top,
    [
      #runword("Revenue growth by segment, %", accent)
      #v(4mm)
      #barchart((("Platform", 9.4), ("Services", 20.3), ("Hardware", 3.4), ("Other", 5.3)),
        col: accent, h: 44mm)
    ],
    [
      #runword("What moved", accent)
      #v(4mm)
      #set text(font: bodyfont, size: 9.5pt, fill: ink)
      #set par(justify: true, leading: 0.62em)
      *Services* was the standout, adding \$240 million of revenue at a 25.4% margin as
      multi-year contracts renewed at higher prices.

      *Platform* grew 9.4% and remains the most profitable segment at 32.2%; its share of
      group revenue eased to 53% from 54%.

      *Hardware* grew modestly and is managed for cash rather than growth.
    ])
  #v(10mm)
  #line(length: 100%, stroke: 0.4pt + rgb("#00000033"))
  #v(6mm)
  #grid(columns: (1fr, 1fr), column-gutter: 10mm, align: top,
    [
      #runword("Operating profit by segment", accent)
      #v(4mm)
      #mixbar((("Platform", 820, accent), ("Services", 360, gold),
               ("Hardware", 70, pos), ("Other", 60, rgb("#7A7A7A"))))
      #v(2mm)
      #sourceline("US$ millions; total 1,310, as reported on page 5.")
    ],
    [
      #runword("Outlook", accent)
      #v(4mm)
      #set text(font: bodyfont, size: 9.5pt, fill: ink)
      #set par(justify: true, leading: 0.62em)
      We expect Services to keep outgrowing the group and to reach a third of revenue
      within three years. Platform investment continues at current levels; Hardware
      capital spending falls again.
    ])
]

// To extend: copy a #leaf(...) block, bump n, add a `#metadata(none) <label>` and a TOC row; for a new figure use kpicard/barchart/
// mixbar/fintable/yoyrow; switch DIRECTION at the top to restyle the whole report.
