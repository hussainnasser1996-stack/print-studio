// finance-motion — PRINT output. Three A4 pages drawn straight from report.json.
//
// Compile (build.sh does this for you):
//   typst compile report_pages.typ out.pdf --root <dir> --input data=<path-from-root>/report.json \
//         --font-path <fonts>
// Fonts: Archivo, Anton, Newsreader 16pt, Space Mono (SIL OFL). They ship with the sibling
// magazine-builder skill at ../magazine-builder/assets/fonts-ttf. Override any family with
// --input font-sans=… font-display=… font-body=… font-mono=… if you use other fonts.
//
// THE RULE: Typst never computes or formats a figure. Every printed number is a `display`
// string from the JSON (validated by scripts/validate_report.py). Numeric `value`s only drive
// bar geometry.

#let r = json(sys.inputs.at("data", default: "report.json"))
#let M = r.meta
#let T = M.theme
#let C(k) = rgb(T.at(k))
#let ink = C("ink")
#let paper = C("paper")
#let panel = C("panel")
#let accent = C("accent")
#let gold = C("gold")
#let pos = C("pos")
#let neg = C("neg")
#let muted = rgb(T.at("muted", default: "#7A7A7A"))
#let sans = sys.inputs.at("font-sans", default: "Archivo")
#let display = sys.inputs.at("font-display", default: "Anton")
#let bodyfont = sys.inputs.at("font-body", default: "Newsreader 16pt")
#let mono = sys.inputs.at("font-mono", default: "Space Mono")
#let fictional = M.at("fictional", default: false)

#set document(title: M.company + " " + M.period, author: M.company)
#set page(paper: "a4", margin: 0pt, fill: paper)
#set text(font: sans, fill: ink, size: 9pt)

// ---------------------------------------------------------------- furniture --
#let kicker(t, col: gold) = text(font: mono, weight: 700, size: 8.5pt, tracking: 3pt, fill: col)[#upper(t)]
#let ftitle(t, size: 34pt) = {
  set text(font: display, fill: ink, size: size, top-edge: "cap-height", bottom-edge: "baseline")
  set par(leading: 0.16em); upper(t)
}
#let h3(t) = text(font: sans, weight: 900, size: 8.5pt, tracking: 2.5pt, fill: accent)[#upper(t)]
#let sourceline(t) = text(font: mono, size: 6.5pt, fill: rgb("#00000088"))[#t]

#let leaf(section, n, body) = page[
  #place(top + left, dx: 18mm, dy: 12mm, box(width: 174mm, grid(columns: (1fr, auto), align: horizon,
    text(font: sans, weight: 900, size: 8.5pt, tracking: 2pt)[#upper(M.company)],
    text(font: sans, weight: 800, size: 8pt, tracking: 3pt, fill: accent)[#upper(section)])))
  #if fictional {
    place(bottom + left, dx: 18mm, dy: -9mm, text(font: mono, size: 6.5pt, fill: rgb("#00000077"))[FICTIONAL SAMPLE DATA])
  }
  #place(bottom + center, dy: -9mm, text(font: mono, size: 8pt, fill: accent)[#n])
  #pad(top: 24mm, bottom: 18mm, x: 18mm, body)
]

#let arrow(k) = if k.direction == "up" [▲] else [▼]
#let kpicard(k) = box(width: 100%, fill: panel, radius: 2pt, inset: (x: 5mm, y: 5mm), stroke: (left: 2.5pt + accent))[
  #text(font: display, size: 28pt)[#k.display]
  #v(1.5mm)
  #text(font: sans, weight: 700, size: 7.5pt, tracking: 1.5pt, fill: rgb("#00000099"))[#upper(k.label)]
  #v(1.2mm)
  #text(font: mono, weight: 700, size: 8pt, fill: if k.good { pos } else { neg })[#arrow(k) #k.delta]
]

// vertical bars; heights from `value`, labels from `display`
#let barchart(points, col: accent, h: 44mm) = {
  let mx = calc.max(..points.map(p => p.value))
  grid(columns: (1fr,) * points.len(), column-gutter: 4mm, align: center,
    ..points.map(p => box(width: 100%)[
      #box(width: 100%, height: h + 7mm)[
        #place(bottom + center)[
          #align(center, text(font: mono, size: 7.5pt, fill: col)[#p.display])
          #v(1.2mm)
          #rect(width: 55%, height: p.value / mx * h, fill: col, radius: (top-left: 1.5pt, top-right: 1.5pt))
        ]
      ]
      #v(1.6mm)
      #text(font: sans, weight: 700, size: 7.5pt)[#p.label]
    ]))
}

// segment mix: widths from `revenue`, legend text = label + display.share (never recomputed)
#let mixbar(items, h: 11mm) = block(width: 100%)[
  #grid(columns: items.map(it => it.revenue * 1fr), rows: h,
    ..items.map(it => rect(width: 100%, height: 100%, fill: C(it.color))))
  #v(3mm)
  #grid(columns: (1fr,) * calc.min(items.len(), 4), column-gutter: 4mm, row-gutter: 2.5mm,
    ..items.map(it => grid(columns: (4.5mm, 1fr), column-gutter: 2mm, align: horizon,
      rect(width: 3.4mm, height: 3.4mm, fill: C(it.color), radius: 0.5pt),
      text(font: mono, size: 7.5pt)[#it.label #text(weight: 700)[#it.display.share]])))
]

// waterfall: start bar, floating steps, end bar. The axis is truncated (a bridge's steps
// are small next to its totals), and the start/end bars carry a break mark to say so.
#let waterfall(b, h: 70mm) = {
  let running = (b.start.value,)
  for s in b.steps { running.push(running.last() + s.value) }
  let lo = calc.min(..running, b.end.value)
  let hi = calc.max(..running, b.end.value)
  let floor = lo - (hi - lo) * 0.9
  let y(v) = (v - floor) / (hi - floor) * h
  let cols = (b.start,) + b.steps + (b.end,)
  let bar(v0, v1, fill, label, lbl-col, brk: false) = box(width: 100%, height: h + 8mm)[
    #place(bottom + center, dy: -y(v0))[
      #align(center, text(font: mono, weight: 700, size: 8pt, fill: lbl-col)[#label])
      #v(1.2mm)
      #box(width: 62%, height: calc.max(y(v1) - y(v0), 0.6pt))[
        #rect(width: 100%, height: 100%, fill: fill)
        #if brk { place(bottom + center, dy: -7mm, rect(width: 110%, height: 1.6mm, fill: paper)) }
      ]
    ]
  ]
  grid(columns: (1fr,) * cols.len(), column-gutter: 3mm, row-gutter: 3mm, align: center,
    bar(floor, b.start.value, accent, b.start.display, accent, brk: true),
    ..b.steps.enumerate().map(((i, s)) => {
      let base = running.at(i)
      let top = running.at(i + 1)
      let (lo2, hi2) = if s.value >= 0 { (base, top) } else { (top, base) }
      bar(lo2, hi2, if s.value >= 0 { pos } else { neg }, s.display, if s.value >= 0 { pos } else { neg })
    }),
    bar(floor, b.end.value, accent, b.end.display, accent, brk: true),
    ..cols.map(c => text(font: sans, weight: 700, size: 7.5pt)[#c.label]))
}

#let cell(t, bold: false, col: ink, num: true) = {
  let a = if num { right + horizon } else { left + horizon }
  align(a, text(font: if num { mono } else { sans }, weight: if bold { 700 } else { 400 }, size: 8.5pt, fill: col)[#t])
}
#let headcell(t, num: true) = align(if num { right } else { left },
  text(font: mono, weight: 700, size: 7pt, tracking: 1pt, fill: accent)[#upper(t)])

// ==================================================================== PAGE 1 ==
#leaf("Highlights", 1)[
  #kicker("Performance highlights")
  #v(4mm)
  #ftitle(M.period + " in numbers")
  #v(9mm)
  #grid(columns: (1fr, 1fr, 1fr), column-gutter: 5mm, row-gutter: 5mm, ..r.kpis.map(kpicard))
  #v(11mm)
  #grid(columns: (1.15fr, 1fr), column-gutter: 10mm,
    [
      #h3(r.revenue_history.title)
      #v(4mm)
      #barchart(r.revenue_history.points)
    ],
    [
      #h3("Revenue mix, " + M.period)
      #v(5mm)
      #mixbar(r.segments.items)
      #v(8mm)
      #set par(justify: true, leading: 0.6em)
      #text(font: bodyfont, size: 9.5pt)[Segment shares of group revenue. Every figure on this page is
        drawn from the same validated data file that drives the animated and interactive editions
        of this report.]
    ])
  #v(1fr)
  #sourceline("Source: " + M.source + ". " + M.units + ".")
]

// ==================================================================== PAGE 2 ==
#leaf("Growth bridge", 2)[
  #kicker("Where the growth came from")
  #v(4mm)
  #ftitle("Revenue bridge")
  #v(8mm)
  #h3(r.bridge.title)
  #v(4mm)
  #waterfall(r.bridge)
  #v(12mm)
  #h3(r.segments.title)
  #v(3mm)
  #let S = r.segments
  #table(columns: (1fr, auto, auto, auto, auto, auto), inset: (x: 3mm, y: 2.6mm), stroke: none,
    table.hline(stroke: 0.8pt + ink),
    headcell("Segment", num: false), headcell(M.period), headcell(M.prior_period),
    headcell("Growth"), headcell("Op. profit"), headcell("Margin"),
    table.hline(stroke: 0.4pt + rgb("#00000044")),
    ..S.items.map(it => (cell(it.label, num: false), cell(it.display.revenue), cell(it.display.revenue_prior, col: rgb("#00000099")),
      cell(it.display.growth), cell(it.display.op_profit), cell(it.display.margin))).flatten(),
    table.hline(stroke: 0.4pt + rgb("#00000044")),
    cell(S.total.label, bold: true, num: false), cell(S.total.display.revenue, bold: true),
    cell(S.total.display.revenue_prior, bold: true, col: rgb("#00000099")), cell(S.total.display.growth, bold: true),
    cell(S.total.display.op_profit, bold: true), cell(S.total.display.margin, bold: true),
    table.hline(stroke: 0.8pt + ink))
  #v(1fr)
  #sourceline("Source: " + M.source + ". " + M.units + ".")
]

// ==================================================================== PAGE 3 ==
#leaf("Financial statements", 3)[
  #kicker("Consolidated")
  #v(4mm)
  #ftitle("Income statement")
  #v(9mm)
  #let I = r.income_statement
  #h3(I.title)
  #v(3mm)
  #table(columns: (1fr,) + (32mm,) * I.columns.len(), inset: (x: 3mm, y: 3.6mm), stroke: none,
    table.hline(stroke: 0.8pt + ink),
    headcell(M.units, num: false), ..I.columns.map(c => headcell(c)),
    table.hline(stroke: 0.4pt + rgb("#00000044")),
    ..I.rows.map(row => {
      let b = row.at("total", default: false)
      let cells = (cell(row.label, bold: b, num: false), ..row.display.map(d => cell(d, bold: b)))
      if b { (table.hline(stroke: 0.4pt + rgb("#00000044")),) + cells } else { cells }
    }).flatten(),
    table.hline(stroke: 0.8pt + ink))
  #v(1fr)
  #sourceline("Source: " + M.source + ". " + M.units + ". Negative figures in parentheses.")
]
