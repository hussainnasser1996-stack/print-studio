import React from "react";
import {useCurrentFrame, interpolate} from "remotion";
import {Report} from "./types";
import {DISPLAY, MONO, SANS, SERIF} from "./fonts";
import {countUp, prog} from "./anim";
import {Frame, colorOf} from "./ui";

// RULE: every figure a viewer can read on a held frame is a `display` string from report.json.
// Numeric `value`s are used only for geometry (bar heights, widths) and count-up in-betweens.

export const Title: React.FC<{r: Report}> = ({r}) => {
  const f = useCurrentFrame();
  const t = r.meta.theme;
  const a = prog(f, 4, 30), b = prog(f, 16, 44), c = prog(f, 28, 56);
  return (
    <div style={{position: "absolute", inset: 0, background: t.ink, color: t.paper, padding: 96,
                 display: "flex", flexDirection: "column", justifyContent: "flex-end"}}>
      <div style={{position: "absolute", top: 96, left: 96, right: 96, display: "flex", justifyContent: "space-between",
                   fontFamily: MONO, fontSize: 22, letterSpacing: 6, fontWeight: 700, color: t.gold}}>
        <span>ANNUAL RESULTS</span><span>{r.meta.period}</span>
      </div>
      <div style={{height: 4, width: `${a * 100}%`, background: t.gold, marginBottom: 48}} />
      <div style={{fontFamily: DISPLAY, fontSize: 168, lineHeight: 0.98, textTransform: "uppercase",
                   opacity: b, transform: `translateY(${(1 - b) * 40}px)`}}>{r.meta.company}</div>
      <div style={{fontFamily: SERIF, fontStyle: "italic", fontSize: 46, marginTop: 36, opacity: c,
                   color: "rgba(255,255,255,0.82)"}}>{r.meta.period} annual results, in motion.</div>
      <div style={{fontFamily: MONO, fontSize: 20, letterSpacing: 3, marginTop: 120, opacity: c, color: "rgba(255,255,255,0.55)"}}>
        {r.meta.fictional ? "FICTIONAL SAMPLE · " : ""}{r.meta.units || ""}
      </div>
    </div>
  );
};

export const Kpis: React.FC<{r: Report; holdFrom: number}> = ({r, holdFrom}) => {
  const f = useCurrentFrame();
  const t = r.meta.theme;
  return (
    <Frame r={r} kicker="Performance highlights" title="The year in numbers">
      <div style={{display: "grid", gridTemplateColumns: "1fr 1fr", gap: 30}}>
        {r.kpis.map((k, i) => {
          const s = 14 + i * 9;
          const inP = prog(f, s, s + 24);
          // count-up must finish (p = 1 exactly) well before the hold starts
          const cu = interpolate(f, [s + 6, holdFrom - 18], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
          const dP = prog(f, holdFrom - 22, holdFrom - 6);
          const col = k.good ? t.pos : t.neg;
          return (
            <div key={k.id} style={{background: t.panel, borderLeft: `6px solid ${t.accent}`, height: 250,
                                    padding: "30px 34px", boxSizing: "border-box", opacity: inP,
                                    transform: `translateY(${(1 - inP) * 30}px)`}}>
              <div style={{fontFamily: DISPLAY, fontSize: 96, lineHeight: 1, color: t.ink}}>{countUp(k.display, cu)}</div>
              <div style={{fontFamily: MONO, fontSize: 20, letterSpacing: 3, marginTop: 22, color: t.muted,
                           textTransform: "uppercase", fontWeight: 700}}>{k.label}</div>
              <div style={{fontFamily: MONO, fontSize: 26, marginTop: 14, color: col, fontWeight: 700, opacity: dP}}>
                {k.direction === "up" ? "▲" : "▼"} {k.delta}
              </div>
            </div>
          );
        })}
      </div>
    </Frame>
  );
};

export const RevenueHistory: React.FC<{r: Report}> = ({r}) => {
  const f = useCurrentFrame();
  const t = r.meta.theme;
  const pts = r.revenue_history.points;
  const max = Math.max(...pts.map((p) => p.value));
  const CH = 560;
  return (
    <Frame r={r} kicker="Five-year record" title="Revenue keeps compounding">
      <div style={{fontFamily: MONO, fontSize: 22, letterSpacing: 3, color: t.accent, fontWeight: 700,
                   textTransform: "uppercase"}}>{r.revenue_history.title}</div>
      <div style={{display: "flex", alignItems: "flex-end", justifyContent: "space-between", height: CH + 80,
                   marginTop: 20, borderBottom: `2px solid ${t.ink}`}}>
        {pts.map((p, i) => {
          const g = prog(f, 12 + i * 8, 52 + i * 8);
          const last = i === pts.length - 1;
          return (
            <div key={p.label} style={{width: 132, display: "flex", flexDirection: "column", alignItems: "center"}}>
              <div style={{fontFamily: DISPLAY, fontSize: 50, color: last ? t.accent : t.ink, opacity: prog(f, 40 + i * 8, 56 + i * 8),
                           marginBottom: 12}}>{p.display}</div>
              <div style={{width: "100%", height: (p.value / max) * CH * g, background: last ? t.accent : t.gold}} />
            </div>
          );
        })}
      </div>
      <div style={{display: "flex", justifyContent: "space-between", marginTop: 16}}>
        {pts.map((p) => (
          <div key={p.label} style={{width: 132, textAlign: "center", fontFamily: MONO, fontSize: 26, fontWeight: 700,
                                     color: t.ink}}>{p.label}</div>
        ))}
      </div>
    </Frame>
  );
};

export const Segments: React.FC<{r: Report}> = ({r}) => {
  const f = useCurrentFrame();
  const t = r.meta.theme;
  const items = r.segments.items;
  const total = items.reduce((s, x) => s + x.revenue, 0);
  const grow = prog(f, 12, 60);
  let acc = 0;
  return (
    <Frame r={r} kicker="Revenue by segment" title="A broader base">
      <div style={{fontFamily: MONO, fontSize: 22, letterSpacing: 3, color: t.accent, fontWeight: 700,
                   textTransform: "uppercase"}}>{r.segments.title}</div>
      <div style={{position: "relative", height: 120, marginTop: 24, background: t.panel}}>
        {items.map((it) => {
          const x0 = acc / total; acc += it.revenue;
          const w = it.revenue / total;
          const vis = Math.max(0, Math.min(w, grow - x0));
          return <div key={it.label} style={{position: "absolute", top: 0, bottom: 0, left: `${x0 * 100}%`,
                                              width: `${vis * 100}%`, background: colorOf(t, it.color || "accent"),
                                              borderRight: vis > 0 ? `3px solid ${t.paper}` : "none"}} />;
        })}
      </div>
      <div style={{marginTop: 50}}>
        {items.map((it, i) => {
          const p = prog(f, 40 + i * 9, 62 + i * 9);
          return (
            <div key={it.label} style={{display: "flex", alignItems: "center", height: 116,
                                        borderTop: `1px solid ${t.ink}22`, opacity: p,
                                        transform: `translateX(${(1 - p) * 40}px)`}}>
              <div style={{width: 30, height: 30, background: colorOf(t, it.color || "accent"), marginRight: 28}} />
              <div style={{flex: 1, fontFamily: SANS, fontSize: 40, fontWeight: 700, color: t.ink}}>{it.label}</div>
              <div style={{fontFamily: MONO, fontSize: 28, color: t.muted, marginRight: 56}}>{it.display.revenue}</div>
              <div style={{fontFamily: DISPLAY, fontSize: 72, color: t.ink, width: 150, textAlign: "right"}}>{it.display.share}</div>
            </div>
          );
        })}
      </div>
    </Frame>
  );
};

export const Bridge: React.FC<{r: Report}> = ({r}) => {
  const f = useCurrentFrame();
  const t = r.meta.theme;
  const b = r.bridge;
  // running levels for geometry only
  const bars: {label: string; display: string; lo: number; hi: number; kind: "total" | "pos" | "neg"}[] = [];
  bars.push({label: b.start.label, display: b.start.display, lo: 0, hi: b.start.value, kind: "total"});
  let lvl = b.start.value;
  for (const s of b.steps) {
    bars.push({label: s.label, display: s.display, lo: Math.min(lvl, lvl + s.value), hi: Math.max(lvl, lvl + s.value),
               kind: s.value >= 0 ? "pos" : "neg"});
    lvl += s.value;
  }
  bars.push({label: b.end.label, display: b.end.display, lo: 0, hi: b.end.value, kind: "total"});
  const top = Math.max(...bars.map((x) => x.hi));
  const floor = Math.min(...bars.filter((x) => x.kind !== "total").map((x) => x.lo), b.start.value);
  const base = floor - (top - floor) * 1.1; // truncated axis so the steps are readable
  const CH = 540;
  const y = (v: number) => ((Math.max(v, base) - base) / (top - base)) * CH;
  const n = bars.length;
  const BW = 112, GAP = (912 - n * BW) / (n - 1);
  return (
    <Frame r={r} kicker="Revenue bridge" title="What added the growth">
      <div style={{fontFamily: MONO, fontSize: 22, letterSpacing: 3, color: t.accent, fontWeight: 700,
                   textTransform: "uppercase"}}>{b.title}</div>
      <div style={{position: "relative", height: CH + 90, marginTop: 20, borderBottom: `2px solid ${t.ink}`}}>
        {bars.map((x, i) => {
          const g = prog(f, 12 + i * 12, 40 + i * 12);
          const left = i * (BW + GAP);
          const h = Math.max(8, y(x.hi) - y(x.lo));
          const col = x.kind === "total" ? t.accent : x.kind === "pos" ? t.pos : t.neg;
          const bottom = y(x.lo);
          return (
            <React.Fragment key={x.label + i}>
              <div style={{position: "absolute", left, width: BW, bottom, height: h * g, background: col}}>
                {x.kind === "total" && (
                  <div style={{position: "absolute", left: -4, right: -4, bottom: 26, height: 14,
                               borderTop: `4px solid ${t.paper}`, borderBottom: `4px solid ${t.paper}`,
                               transform: "skewY(-8deg)", opacity: g}} />
                )}
              </div>
              {i < n - 1 && (
                <div style={{position: "absolute", left: left + BW, width: GAP, bottom: y(x.kind === "neg" ? x.lo : x.hi) - 1,
                             borderTop: `2px dashed ${t.ink}55`, opacity: prog(f, 40 + i * 12, 52 + i * 12)}} />
              )}
              <div style={{position: "absolute", left: left - 30, width: BW + 60, bottom: bottom + h + 12, textAlign: "center",
                           fontFamily: DISPLAY, fontSize: x.kind === "total" ? 46 : 40,
                           color: x.kind === "total" ? t.ink : col, opacity: prog(f, 36 + i * 12, 50 + i * 12)}}>{x.display}</div>
            </React.Fragment>
          );
        })}
      </div>
      <div style={{position: "relative", height: 50, marginTop: 16}}>
        {bars.map((x, i) => (
          <div key={x.label + i} style={{position: "absolute", left: i * (BW + GAP) - 30, width: BW + 60, textAlign: "center",
                                          fontFamily: MONO, fontSize: 22, fontWeight: 700, color: t.ink}}>{x.label}</div>
        ))}
      </div>
      <div style={{fontFamily: MONO, fontSize: 17, color: t.muted, marginTop: 10}}>Axis truncated to show the steps.</div>
    </Frame>
  );
};

export const IncomeStatement: React.FC<{r: Report}> = ({r}) => {
  const f = useCurrentFrame();
  const t = r.meta.theme;
  const inc = r.income_statement;
  return (
    <Frame r={r} kicker="Income statement" title="From revenue to profit">
      <div style={{display: "flex", fontFamily: MONO, fontSize: 22, fontWeight: 700, letterSpacing: 2,
                   color: t.accent, borderBottom: `2px solid ${t.ink}`, padding: "0 12px 14px 0"}}>
        <div style={{flex: 1, textTransform: "uppercase"}}>{inc.title}</div>
        {inc.columns.map((c) => <div key={c} style={{width: 190, textAlign: "right"}}>{c}</div>)}
      </div>
      {inc.rows.map((row, i) => {
        const p = prog(f, 14 + i * 8, 36 + i * 8);
        return (
          <div key={row.label} style={{display: "flex", alignItems: "center", height: 80,
                                       borderTop: row.total ? `2px solid ${t.ink}` : `1px solid ${t.ink}1f`,
                                       background: row.total ? t.panel : "transparent", padding: "0 12px",
                                       opacity: p, transform: `translateX(${(1 - p) * 50}px)`}}>
            <div style={{flex: 1, fontFamily: SANS, fontSize: 31, fontWeight: row.total ? 800 : 500, color: t.ink}}>{row.label}</div>
            {row.display.map((d, j) => (
              <div key={j} style={{width: 190, textAlign: "right", fontFamily: MONO, fontSize: 31,
                                   fontWeight: row.total ? 700 : 400, color: j === 0 ? t.ink : t.muted}}>{d}</div>
            ))}
          </div>
        );
      })}
    </Frame>
  );
};

export const End: React.FC<{r: Report}> = ({r}) => {
  const f = useCurrentFrame();
  const t = r.meta.theme;
  const a = prog(f, 4, 30), b = prog(f, 18, 46);
  return (
    <div style={{position: "absolute", inset: 0, background: t.ink, color: t.paper, padding: 96,
                 display: "flex", flexDirection: "column", justifyContent: "center"}}>
      <div style={{fontFamily: MONO, fontSize: 22, letterSpacing: 6, fontWeight: 700, color: t.gold, opacity: a}}>SOURCE</div>
      <div style={{fontFamily: SERIF, fontStyle: "italic", fontSize: 44, lineHeight: 1.3, marginTop: 20, opacity: a,
                   color: "rgba(255,255,255,0.85)"}}>{r.meta.source}</div>
      <div style={{height: 4, width: `${b * 100}%`, background: t.gold, margin: "64px 0"}} />
      <div style={{fontFamily: DISPLAY, fontSize: 104, lineHeight: 1.02, textTransform: "uppercase", opacity: b}}>
        Every figure ties to report.json
      </div>
      <div style={{fontFamily: MONO, fontSize: 20, marginTop: 48, color: "rgba(255,255,255,0.55)", opacity: b}}>
        {r.meta.company} · {r.meta.period}{r.meta.fictional ? " · FICTIONAL SAMPLE" : ""}
      </div>
    </div>
  );
};
