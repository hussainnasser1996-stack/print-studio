#!/usr/bin/env bash
# Render the annual-results reel from a report.json.
#   bash render.sh <report.json> <out.mp4> [--format 4x5|9x16|16x9]
# Also writes <out.mp4>.manifest.json: one timestamp per data scene, inside its static hold,
# so a verifier can grab those frames and OCR every figure against report.json.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPORT="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
OUT="$(mkdir -p "$(dirname "$2")" && cd "$(dirname "$2")" && pwd)/$(basename "$2")"
FORMAT="4x5"
[[ "${3:-}" == "--format" ]] && FORMAT="${4:?format}"
python3 "$HERE/../scripts/validate_report.py" "$REPORT" >/dev/null || {
  echo "✘ report.json does not foot — run scripts/validate_report.py and fix it first" >&2; exit 1; }
PROPS="$HERE/.props.$$.json"
trap 'rm -f "$PROPS"' EXIT
node -e 'const fs=require("fs");fs.writeFileSync(process.argv[3],JSON.stringify({report:JSON.parse(fs.readFileSync(process.argv[1])),format:process.argv[2]}))' "$REPORT" "$FORMAT" "$PROPS"
cd "$HERE"
[[ -d node_modules ]] || npm install --silent
RAW="$OUT.raw.mp4"
npx remotion render src/index.ts FinanceReel "$RAW" --props="$PROPS" --codec=h264 --muted --log=error
# normalise for social upload: limited-range yuv420p (not yuvj), no audio track, moov atom first
ffmpeg -v error -y -i "$RAW" -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -color_range tv -an -movflags +faststart "$OUT"
rm -f "$RAW"
node -e '
const t=require(process.argv[1]); let from=0; const m=[];
for (const s of t.scenes) { if (s.hold_from!==undefined) m.push({section:s.id, t:+(((from+Math.round((s.hold_from+s.frames-t.fade)/2))/t.fps).toFixed(3))}); from+=s.frames; }
require("fs").writeFileSync(process.argv[2], JSON.stringify(m,null,2));' "$HERE/src/timing.json" "$OUT.manifest.json"
echo "✔ $OUT"; echo "✔ $OUT.manifest.json"
