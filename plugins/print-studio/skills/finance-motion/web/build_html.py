#!/usr/bin/env python3
"""finance-motion: report.json -> one self-contained, interactive HTML annual-report page.

    python build_html.py report.json out.html [--offline]

- The report.json is inlined as <script type="application/json">. Every visible figure is a
  "display" string from that file, printed verbatim. JS never formats a number; numeric
  "value"s only drive geometry (bar heights, slice angles). Axis tick labels are hidden for
  the same reason: a tick like "4,300" would be a number the JSON never stated.
- Charts use Apache ECharts with the SVG renderer, so chart labels are real DOM text that a
  verifier can find in the page (and OCR can read in a screenshot).
- Sections animate in on scroll. `?static=1` (or prefers-reduced-motion) renders every section
  in its final state with no animation. Use it for verification screenshots.
- Writes <out>.manifest.json: one entry per section with its CSS selector and the canonical
  strings that must be visible inside it.
- --offline downloads ECharts once (cached next to this script in vendor/) and inlines it, so
  the file works with no network. The default loads a pinned version from jsDelivr.
"""
import html, json, pathlib, sys, urllib.request

ECHARTS_VERSION = "5.6.0"
ECHARTS_URL = f"https://cdn.jsdelivr.net/npm/echarts@{ECHARTS_VERSION}/dist/echarts.min.js"
HERE = pathlib.Path(__file__).resolve().parent


def canonical(r):
    """The strings that must be visible, per section. The verifier uses this list."""
    out = {}
    if r.get("kpis"):
        out["kpis"] = [s for k in r["kpis"] for s in (k["display"], k["delta"])]
    if r.get("revenue_history"):
        out["revenue_history"] = [p["display"] for p in r["revenue_history"]["points"]]
    if r.get("segments"):
        out["segments"] = [s for it in r["segments"]["items"] for s in (it["label"], it["display"]["share"])]
    if r.get("bridge"):
        b = r["bridge"]
        out["bridge"] = [b["start"]["display"], *[s["display"] for s in b["steps"]], b["end"]["display"]]
    if r.get("income_statement"):
        out["income_statement"] = [d for row in r["income_statement"]["rows"] for d in row["display"]]
    return out


def echarts_tag(offline):
    if not offline:
        return f'<script src="{ECHARTS_URL}"></script>'
    cache = HERE / "vendor" / f"echarts-{ECHARTS_VERSION}.min.js"
    if not cache.exists():
        cache.parent.mkdir(exist_ok=True)
        urllib.request.urlretrieve(ECHARTS_URL, cache)
    return "<script>" + cache.read_text(encoding="utf-8").replace("</script", "<\\/script") + "</script>"


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Archivo:wght@400;600;800&family=Newsreader:ital,wght@0,400;1,400&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
:root {
  --ink: #14213D; --paper: #FCFCFA; --panel: #F1EFE9; --accent: #1B3A6B;
  --gold: #9A7B4F; --pos: #1C6B4A; --neg: #A33A2E; --muted: #7A7A7A;
  --rule: rgba(20,33,61,.14);
  --sans: "Archivo", system-ui, sans-serif; --display: "Anton", "Archivo", sans-serif;
  --serif: "Newsreader", Georgia, serif; --mono: "Space Mono", ui-monospace, monospace;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body { margin: 0; background: var(--paper); color: var(--ink); font-family: var(--sans); line-height: 1.5; overflow-x: hidden; }
.wrap { max-width: 1120px; margin: 0 auto; padding: 0 24px; }
section { padding: 72px 0; border-top: 1px solid var(--rule); }
.kicker { font-family: var(--mono); font-weight: 700; font-size: 12px; letter-spacing: .22em; text-transform: uppercase; color: var(--gold); margin: 0 0 12px; }
h2 { font-family: var(--display); font-weight: 400; font-size: clamp(32px, 5vw, 52px); line-height: 1.02; margin: 0 0 28px; text-transform: uppercase; letter-spacing: .01em; }
.note { font-family: var(--mono); font-size: 11px; color: var(--muted); margin-top: 12px; }

/* reveal on scroll */
.reveal { opacity: 0; transform: translateY(24px); transition: opacity .8s ease, transform .8s ease; }
.reveal.in { opacity: 1; transform: none; }
.static .reveal { opacity: 1; transform: none; transition: none; }

/* hero */
.hero { border-top: 0; padding: 96px 0 72px; background: var(--ink); color: var(--paper); }
.hero .kicker { color: var(--gold); }
.hero h1 { font-family: var(--display); font-weight: 400; font-size: clamp(48px, 10vw, 112px); line-height: .95; margin: 0 0 20px; text-transform: uppercase; }
.hero p:not(.kicker) { font-family: var(--serif); font-style: italic; font-size: clamp(18px, 2.4vw, 24px); margin: 0; opacity: .85; }
.flag { display: inline-block; margin-top: 28px; font-family: var(--mono); font-size: 11px; letter-spacing: .18em; text-transform: uppercase; border: 1px solid rgba(252,252,250,.45); padding: 6px 10px; }

/* kpis */
.kpis { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.kpi { background: var(--panel); border-left: 4px solid var(--accent); padding: 22px 22px 18px; min-width: 0; }
.kpi .v { font-family: var(--display); font-size: clamp(34px, 4.6vw, 54px); line-height: 1; white-space: nowrap; font-variant-numeric: tabular-nums; }
.kpi .l { font-weight: 600; font-size: 12px; letter-spacing: .16em; text-transform: uppercase; color: rgba(20,33,61,.65); margin-top: 14px; }
.kpi .d { font-family: var(--mono); font-weight: 700; font-size: 13px; margin-top: 8px; }
.good { color: var(--pos); } .bad { color: var(--neg); }

/* charts */
.chart { width: 100%; height: 380px; }
.grid2 { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr); gap: 32px; align-items: center; }
.legend { list-style: none; margin: 0; padding: 0; }
.legend li { display: grid; grid-template-columns: 14px 1fr auto; gap: 12px; align-items: center; padding: 12px 8px; border-bottom: 1px solid var(--rule); cursor: pointer; }
.legend li:hover, .legend li.on { background: var(--panel); }
.legend .sw { width: 14px; height: 14px; }
.legend .nm { font-weight: 600; }
.legend .sh { font-family: var(--mono); font-weight: 700; }
.detail { margin-top: 18px; background: var(--panel); padding: 16px 18px; font-size: 14px; min-height: 96px; }
.detail dl { display: grid; grid-template-columns: auto auto; gap: 6px 18px; margin: 8px 0 0; }
.detail dt { color: rgba(20,33,61,.65); } .detail dd { margin: 0; font-family: var(--mono); font-weight: 700; text-align: right; }

/* table */
table { width: 100%; border-collapse: collapse; font-size: 15px; }
th, td { padding: 11px 8px; border-bottom: 1px solid var(--rule); }
th { font-family: var(--mono); font-size: 11px; letter-spacing: .14em; text-transform: uppercase; color: rgba(20,33,61,.65); text-align: right; font-weight: 700; }
th:first-child, td:first-child { text-align: left; }
td.n { text-align: right; font-family: var(--mono); font-variant-numeric: tabular-nums; white-space: nowrap; }
tr.total td { font-weight: 700; border-top: 1.5px solid var(--ink); }

footer { background: var(--ink); color: rgba(252,252,250,.8); padding: 40px 0 56px; font-family: var(--mono); font-size: 12px; }
footer strong { color: var(--gold); font-weight: 700; }

@media (max-width: 760px) {
  section { padding: 52px 0; }
  .wrap { padding: 0 16px; }
  .kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
  .kpi { padding: 16px 14px 14px; }
  .kpi .v { font-size: 30px; }
  .kpi .l { font-size: 10px; letter-spacing: .1em; }
  .grid2 { grid-template-columns: minmax(0, 1fr); }
  .chart { height: 320px; }
  table { font-size: 13px; }
  th, td { padding: 9px 4px; }
}
@media (prefers-reduced-motion: reduce) { .reveal { opacity: 1; transform: none; transition: none; } }
</style>
__ECHARTS__
</head>
<body>
<script type="application/json" id="report">__DATA__</script>

<section class="hero" data-section="hero">
  <div class="wrap">
    <p class="kicker" id="hero-kicker"></p>
    <h1 id="hero-title"></h1>
    <p id="hero-sub"></p>
    <span class="flag" id="hero-flag" hidden>Fictional sample · not a real company</span>
  </div>
</section>

<section data-section="kpis"><div class="wrap">
  <p class="kicker">Performance highlights</p><h2>The year in numbers</h2>
  <div class="kpis reveal" id="kpis"></div>
</div></section>

<section data-section="revenue_history"><div class="wrap">
  <p class="kicker">Growth</p><h2 id="rh-title"></h2>
  <div class="chart reveal" id="rh-chart"></div>
</div></section>

<section data-section="segments"><div class="wrap">
  <p class="kicker">Mix</p><h2 id="seg-title"></h2>
  <div class="grid2 reveal">
    <div class="chart" id="seg-chart"></div>
    <div><ul class="legend" id="seg-legend"></ul><div class="detail" id="seg-detail"></div></div>
  </div>
</div></section>

<section data-section="bridge"><div class="wrap">
  <p class="kicker">Bridge</p><h2 id="br-title"></h2>
  <div class="chart reveal" id="br-chart"></div>
  <p class="note" id="br-note"></p>
</div></section>

<section data-section="income_statement"><div class="wrap">
  <p class="kicker">Financial statements</p><h2 id="is-title"></h2>
  <div class="reveal"><table id="is-table"></table></div>
</div></section>

<footer data-section="footer"><div class="wrap">
  <div id="ft-source"></div>
  <div style="margin-top:8px"><strong>Every figure ties to report.json.</strong> Figures are printed verbatim from the audited data file; nothing on this page is recomputed or rounded.</div>
</div></footer>

<script>
(() => {
  const R = JSON.parse(document.getElementById("report").textContent);
  const T = Object.assign({}, R.meta.theme || {});
  const STATIC = new URLSearchParams(location.search).has("static") ||
                 window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (STATIC) document.documentElement.classList.add("static");
  for (const [k, v] of Object.entries(T)) document.documentElement.style.setProperty("--" + k, v);
  const col = name => T[name] || name;
  const $ = id => document.getElementById(id);
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
  const FONT = { fontFamily: "Space Mono, monospace" };

  // ---------- hero
  const m = R.meta;
  $("hero-kicker").textContent = "Annual report " + m.period;
  $("hero-title").textContent = m.company;
  $("hero-sub").textContent = (m.units || "") ;
  if (m.fictional) $("hero-flag").hidden = false;
  document.title = m.company + " — " + m.period;

  // ---------- kpis: "roll" each digit, then settle on the display string verbatim
  const roll = (node, finalText) => {
    if (STATIC) { node.textContent = finalText; return; }
    const chars = [...finalText], t0 = performance.now(), dur = 1300;
    const tick = now => {
      const p = Math.min(1, (now - t0) / dur);
      node.textContent = chars.map((c, i) => /\d/.test(c) && p < (i + 1) / chars.length * .6 + .4
        ? String(Math.floor(Math.random() * 10)) : c).join("");
      if (p < 1 && !node._done) requestAnimationFrame(tick); else node.textContent = finalText;
    };
    requestAnimationFrame(tick);
    // rAF is throttled in background tabs and some headless modes: always land on the display string
    setTimeout(() => { node._done = true; node.textContent = finalText; }, dur + 250);
  };
  const kpiNodes = [];
  for (const k of R.kpis || []) {
    const card = el("div", "kpi");
    const v = el("div", "v", k.display);            // final text present in the DOM from the start
    const arrow = k.direction === "up" ? "▲ " : "▼ ";
    card.append(v, el("div", "l", k.label), el("div", "d " + (k.good ? "good" : "bad"), arrow + k.delta));
    card.title = k.label + ": " + k.display + " (" + k.delta + ")";
    $("kpis").append(card); kpiNodes.push([v, k.display]);
  }

  // ---------- charts (SVG renderer: labels are DOM text)
  const charts = [];
  const make = (id, option) => {
    const c = echarts.init($(id), null, { renderer: "svg" });
    option.animation = !STATIC;
    option.animationDuration = 1200;
    option.textStyle = Object.assign({ fontFamily: "Archivo, sans-serif", color: col("ink") }, option.textStyle || {});
    c._fm = option; charts.push(c);
    return c;
  };
  const tip = { trigger: "item", backgroundColor: "#fff", borderColor: "rgba(20,33,61,.2)", textStyle: { color: col("ink"), fontFamily: "Archivo, sans-serif" } };

  // revenue history
  const rh = R.revenue_history;
  if (rh) {
    $("rh-title").textContent = rh.title;
    make("rh-chart", {
      grid: { left: 8, right: 8, top: 40, bottom: 36 },
      tooltip: Object.assign({}, tip, { formatter: p => rh.points[p.dataIndex].label + ": " + rh.points[p.dataIndex].display + " " + (rh.unit || "") }),
      xAxis: { type: "category", data: rh.points.map(p => p.label), axisTick: { show: false },
               axisLine: { lineStyle: { color: col("ink") } }, axisLabel: Object.assign({ fontWeight: 700, color: col("ink") }, FONT) },
      yAxis: { type: "value", min: 0, axisLabel: { show: false }, splitLine: { lineStyle: { color: "rgba(20,33,61,.08)" } } },
      series: [{ type: "bar", barWidth: "46%",
        data: rh.points.map((p, i) => ({ value: p.value,
          itemStyle: { color: i === rh.points.length - 1 ? col("gold") : col("accent") } })),
        label: Object.assign({ show: true, position: "top", fontSize: 15, fontWeight: 700, color: col("ink"),
          formatter: p => rh.points[p.dataIndex].display }, FONT),
        animationDelay: i => i * 140 }]
    });
  }

  // segments: donut + DOM legend + click-for-detail
  const sg = R.segments;
  if (sg) {
    $("seg-title").textContent = sg.title;
    const detail = $("seg-detail");
    const show = i => {
      const it = sg.items[i];
      detail.replaceChildren(el("div", "nm", it.label));
      const dl = el("dl");
      for (const [k, lab] of [["revenue", "Revenue " + (R.meta.period || "")], ["revenue_prior", "Revenue " + (R.meta.prior_period || "prior")],
                              ["growth", "Growth"], ["op_profit", "Operating profit"], ["margin", "Margin"], ["share", "Share of group"]])
        if (it.display[k] != null) dl.append(el("dt", null, lab), el("dd", null, it.display[k]));
      detail.append(dl);
      [...$("seg-legend").children].forEach((li, j) => li.classList.toggle("on", j === i));
    };
    const narrow = () => $("seg-chart").clientWidth < 420;
    const segChart = make("seg-chart", {
      tooltip: Object.assign({}, tip, { formatter: p => sg.items[p.dataIndex].label + ": " + sg.items[p.dataIndex].display.revenue + " (" + sg.items[p.dataIndex].display.share + ")" }),
      series: [{ type: "pie", radius: ["48%", "74%"], center: ["50%", "50%"], avoidLabelOverlap: true,
        itemStyle: { borderColor: col("paper"), borderWidth: 3 },
        label: Object.assign({ show: !narrow(), fontSize: 13, fontWeight: 700, color: col("ink"),
          formatter: p => sg.items[p.dataIndex].display.share }, FONT),
        labelLine: { show: !narrow(), length: 10, length2: 8 },
        emphasis: { scale: true, scaleSize: 6 },
        data: sg.items.map(it => ({ name: it.label, value: it.revenue, itemStyle: { color: col(it.color) } })) }]
    });
    sg.items.forEach((it, i) => {
      const li = el("li");
      const sw = el("span", "sw"); sw.style.background = col(it.color);
      li.append(sw, el("span", "nm", it.label), el("span", "sh", it.display.share));
      li.addEventListener("click", () => { show(i); segChart.dispatchAction({ type: "highlight", dataIndex: i }); });
      li.addEventListener("mouseleave", () => segChart.dispatchAction({ type: "downplay", dataIndex: i }));
      $("seg-legend").append(li);
    });
    segChart.on("click", p => show(p.dataIndex));
    show(0);
  }

  // bridge: stacked-bar waterfall (transparent base + visible delta)
  const br = R.bridge;
  if (br) {
    $("br-title").textContent = br.title;
    const nodes = [br.start, ...br.steps, br.end];
    const base = [], vis = [];
    let run = br.start.value;
    nodes.forEach((n, i) => {
      if (i === 0 || i === nodes.length - 1) { base.push(0); vis.push(n.value); }
      else { base.push(n.value >= 0 ? run : run + n.value); vis.push(Math.abs(n.value)); run += n.value; }
    });
    // Truncated axis so the steps are visible; it is stated under the chart, never hidden.
    const lo = Math.min(br.start.value, br.end.value);
    const hi = Math.max(...nodes.map((n, i) => base[i] + vis[i]));
    const axisMin = Math.max(0, lo - (hi - lo) * 1.2);
    $("br-note").textContent = "Vertical axis does not start at zero; bar lengths show the change between " + br.start.label + " and " + br.end.label + ".";
    const brNarrow = $("br-chart").clientWidth < 560;   // category names collide on phones: angle them
    make("br-chart", {
      grid: { left: 8, right: 8, top: 40, bottom: brNarrow ? 64 : 36, containLabel: brNarrow },
      tooltip: Object.assign({}, tip, { formatter: p => nodes[p.dataIndex].label + ": " + nodes[p.dataIndex].display }),
      xAxis: { type: "category", data: nodes.map(n => n.label), axisTick: { show: false },
               axisLine: { lineStyle: { color: col("ink") } }, axisLabel: Object.assign({ fontWeight: 700, color: col("ink"), interval: 0,
                 rotate: brNarrow ? 40 : 0, fontSize: brNarrow ? 10 : 12 }, FONT) },
      yAxis: { type: "value", min: axisMin, max: hi + (hi - lo) * 0.25, axisLabel: { show: false }, splitLine: { lineStyle: { color: "rgba(20,33,61,.08)" } } },
      series: [
        { type: "bar", stack: "w", silent: true, itemStyle: { color: "transparent" }, data: base, tooltip: { show: false } },
        { type: "bar", stack: "w", barWidth: "52%",
          data: vis.map((v, i) => ({ value: v, itemStyle: { color:
            i === 0 || i === nodes.length - 1 ? col("accent") : (nodes[i].value >= 0 ? col("pos") : col("neg")) } })),
          label: Object.assign({ show: true, position: "top", fontSize: brNarrow ? 11 : 14, fontWeight: 700, color: col("ink"),
            formatter: p => nodes[p.dataIndex].display }, FONT),
          animationDelay: i => i * 220 }
      ]
    });
  }

  // income statement: real table, display strings verbatim
  const inc = R.income_statement;
  if (inc) {
    $("is-title").textContent = inc.title;
    const t = $("is-table");
    const hr = el("tr"); hr.append(el("th", null, ""), ...inc.columns.map(c => el("th", null, c)));
    const thead = el("thead"); thead.append(hr); t.append(thead);
    const tb = el("tbody");
    for (const row of inc.rows) {
      const tr = el("tr", row.total ? "total" : null);
      tr.append(el("td", null, row.label), ...row.display.map(d => el("td", "n", d)));
      tb.append(tr);
    }
    t.append(tb);
  }

  $("ft-source").textContent = "Source: " + (R.meta.source || "");

  // ---------- reveal on scroll; charts and counters start when their section enters
  const start = sec => {
    sec.querySelectorAll(".reveal").forEach(n => n.classList.add("in"));
    charts.filter(c => sec.contains(c.getDom()) && !c._started).forEach(c => { c._started = true; c.setOption(c._fm); });
    if (sec.dataset.section === "kpis" && !sec._rolled) { sec._rolled = true; kpiNodes.forEach(([n, t]) => roll(n, t)); }
  };
  const secs = [...document.querySelectorAll("section")];
  if (STATIC || !("IntersectionObserver" in window)) secs.forEach(start);
  else {
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { start(e.target); io.unobserve(e.target); } }), { threshold: 0.2 });
    secs.forEach(s => io.observe(s));
  }
  window.addEventListener("resize", () => charts.forEach(c => c.resize()));
  document.documentElement.dataset.ready = "1";
})();
</script>
</body>
</html>
"""


def build(report_path, out_path, offline=False):
    r = json.loads(pathlib.Path(report_path).read_text(encoding="utf-8"))
    data = json.dumps(r, ensure_ascii=False).replace("</", "<\\/")
    title = html.escape(f"{r['meta']['company']} — {r['meta']['period']}")
    page = PAGE.replace("__TITLE__", title).replace("__ECHARTS__", echarts_tag(offline)).replace("__DATA__", data)
    out = pathlib.Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    strings = canonical(r)
    manifest = [{"section": s, "selector": f'section[data-section="{s}"]', "strings": strings.get(s, [])}
                for s in ("hero", "kpis", "revenue_history", "segments", "bridge", "income_statement")
                if s == "hero" or s in strings]
    pathlib.Path(str(out) + ".manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size // 1024} KB) + manifest ({sum(len(m['strings']) for m in manifest)} canonical strings)")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        sys.exit(__doc__)
    build(args[0], args[1], offline="--offline" in sys.argv)
