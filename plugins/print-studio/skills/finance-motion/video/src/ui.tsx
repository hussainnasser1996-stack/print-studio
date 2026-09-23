import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate} from "remotion";
import {Report, Theme} from "./types";
import {MONO, SANS, DISPLAY} from "./fonts";
import {prog} from "./anim";

export const W = 1080, H = 1350; // logical stage; scaled to fit every output format

/** Paper background across the whole frame + a 1080x1350 stage centred and scaled to fit. */
export const Stage: React.FC<{theme: Theme; children: React.ReactNode}> = ({theme, children}) => {
  const {width, height} = useVideoConfig();
  const s = Math.min(width / W, height / H);
  return (
    <AbsoluteFill style={{background: theme.paper}}>
      <div style={{position: "absolute", left: (width - W * s) / 2, top: (height - H * s) / 2,
                   width: W, height: H, transform: `scale(${s})`, transformOrigin: "top left"}}>
        {children}
      </div>
    </AbsoluteFill>
  );
};

/** Fade a whole scene in at its start and out at its end. */
export const SceneFade: React.FC<{frames: number; fade: number; children: React.ReactNode}> = ({frames, fade, children}) => {
  const f = useCurrentFrame();
  const o = interpolate(f, [0, fade, frames - fade, frames], [0, 1, 1, 0], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

/** Running head, section title and footer shared by every data scene. */
export const Frame: React.FC<{r: Report; kicker: string; title: string; children: React.ReactNode}> = ({r, kicker, title, children}) => {
  const f = useCurrentFrame();
  const t = r.meta.theme;
  const p = prog(f, 0, 22);
  return (
    <div style={{position: "absolute", inset: 0, padding: "84px 84px 0 84px", color: t.ink, fontFamily: SANS}}>
      <div style={{display: "flex", justifyContent: "space-between", fontFamily: MONO, fontSize: 20,
                   letterSpacing: 5, fontWeight: 700, color: t.accent, textTransform: "uppercase"}}>
        <span>{r.meta.company}</span><span style={{color: t.gold}}>{r.meta.period} · Annual results</span>
      </div>
      <div style={{height: 2, background: t.ink, marginTop: 22, width: `${p * 100}%`}} />
      <div style={{marginTop: 58, opacity: p, transform: `translateY(${(1 - p) * 24}px)`}}>
        <div style={{fontFamily: MONO, fontSize: 22, letterSpacing: 6, color: t.gold, fontWeight: 700,
                     textTransform: "uppercase"}}>{kicker}</div>
        <div style={{fontFamily: DISPLAY, fontSize: 92, lineHeight: 1.02, marginTop: 14, textTransform: "uppercase",
                     color: t.ink}}>{title}</div>
      </div>
      <div style={{position: "relative", marginTop: 52}}>{children}</div>
      <div style={{position: "absolute", left: 84, right: 84, bottom: 64, display: "flex", justifyContent: "space-between",
                   fontFamily: MONO, fontSize: 17, color: t.muted, letterSpacing: 1}}>
        <span>{r.meta.units || ""}</span>
        <span>{r.meta.fictional ? "FICTIONAL SAMPLE" : ""}</span>
      </div>
    </div>
  );
};

export const colorOf = (t: Theme, key: string) => (t as unknown as Record<string, string>)[key] || key;
