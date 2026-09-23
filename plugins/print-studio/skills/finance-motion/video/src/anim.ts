import {Easing, interpolate} from "remotion";

export const ease = Easing.bezier(0.22, 1, 0.36, 1);

/** 0→1 progress between frames a and b, eased and clamped. */
export const prog = (f: number, a: number, b: number) =>
  interpolate(f, [a, b], [0, 1], {easing: ease, extrapolateLeft: "clamp", extrapolateRight: "clamp"});

/**
 * Count-up that LANDS ON THE DISPLAY STRING. Intermediate frames interpolate the numeric part,
 * formatted like the target (same decimals, same thousands grouping, same prefix/suffix).
 * At p >= 1 the exact display string from report.json is returned verbatim — code never
 * formats the final figure.
 */
export const countUp = (display: string, p: number): string => {
  if (p >= 1) return display;
  const m = display.match(/^(.*?)(\d[\d,]*(?:\.\d+)?)(.*)$/);
  if (!m) return display;
  const [, pre, num, post] = m;
  const target = parseFloat(num.replace(/,/g, ""));
  const dec = (num.split(".")[1] || "").length;
  const v = target * p;
  let s = v.toFixed(dec);
  if (num.includes(",")) {
    const [i, d] = s.split(".");
    s = i.replace(/\B(?=(\d{3})+(?!\d))/g, ",") + (d ? "." + d : "");
  }
  return pre + s + post;
};
