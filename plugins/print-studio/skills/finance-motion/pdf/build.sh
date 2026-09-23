#!/usr/bin/env bash
# finance-motion PRINT output: report.json -> A4 PDF (3 pages) + <out>.manifest.json
#   bash pdf/build.sh <report.json> <out.pdf>
# Fonts: Archivo, Anton, Newsreader, Space Mono. Default path is the sibling magazine-builder
# skill's bundled fonts; set FM_FONTS=/path/to/fonts to use another folder.
set -euo pipefail
[[ $# -eq 2 ]] || { echo "usage: build.sh <report.json> <out.pdf>" >&2; exit 2; }
HERE="$(cd "$(dirname "$0")" && pwd)"
DATA="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
OUT="$2"; mkdir -p "$(dirname "$OUT")"
FONTS="${FM_FONTS:-$HERE/../../magazine-builder/assets/fonts-ttf}"
[[ -d "$FONTS" ]] || echo "warning: font folder $FONTS not found; Typst will fall back to system fonts" >&2
python3 "$HERE/../scripts/validate_report.py" "$DATA" >/dev/null \
  || { echo "✘ $1 failed validation — run scripts/validate_report.py for details" >&2; exit 1; }
# --root / lets Typst read the data file wherever it lives (the path is passed absolute).
typst compile "$HERE/report_pages.typ" "$OUT" --root / --input "data=$DATA" --font-path "$FONTS"
# Which page carries which section (the output checker uses this to look in the right place).
cat > "${OUT}.manifest.json" <<'JSON'
[
  {"section": "kpis",             "page": 1},
  {"section": "revenue_history",  "page": 1},
  {"section": "segments",         "page": 1},
  {"section": "bridge",           "page": 2},
  {"section": "income_statement", "page": 3}
]
JSON
echo "✔ $OUT (+ ${OUT}.manifest.json)"
