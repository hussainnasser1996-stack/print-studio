# finance-motion / video

An animated annual-results reel (Remotion 4), driven entirely by one `report.json`.

```bash
bash render.sh ../examples/meridian/report.json ../examples/meridian/out/meridian-reel.mp4            # 1080x1350 (4:5)
bash render.sh ../examples/meridian/report.json ../examples/meridian/out/meridian-reel-9x16.mp4 --format 9x16
npm run studio    # live preview of the sample
```

`render.sh` refuses to render a report that doesn't foot (it runs `../scripts/validate_report.py`
first). It renders with Remotion, then re-encodes to H.264 yuv420p with faststart and no audio,
and writes `<out>.manifest.json`: one timestamp per data scene, taken inside that scene's static hold.

**Scenes** (timing in `src/timing.json`): title → KPI grid (count-ups) → revenue history bars →
segment mix → revenue bridge (waterfall, truncated axis marked) → income statement → source card.
34.7 s at 30 fps. Each data scene animates in and then holds, fully static, for about 2 s.

**The rule:** code never formats a final figure. Every number a viewer can read on a held frame is a
`display` string from `report.json`. Numeric `value`s drive only geometry (bar heights, widths)
and the in-between frames of a count-up, which lands exactly on the display string (`src/anim.ts`).
Delta arrows follow `direction`; their colour follows `good`, never the sign.

**Formats:** `4x5` (default), `9x16`, `16x9`. The design is a 1080x1350 stage scaled to fit, so 9x16
and 16x9 show paper margins around it.

**Licence note:** Remotion is free for individuals and for companies with up to 3 employees
(commercial use included). Larger companies need a Remotion company licence; see remotion.dev/license.
Fonts (Anton, Archivo, Newsreader, Space Mono) load from Google Fonts via `@remotion/google-fonts`
and are all SIL OFL.
