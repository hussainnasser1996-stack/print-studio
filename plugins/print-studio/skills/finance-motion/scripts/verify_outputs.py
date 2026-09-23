#!/usr/bin/env python3
"""Tie every output back to report.json: is each figure actually VISIBLE where it should be?

validate_report.py proves the data foots. This proves the renders didn't lose, clip, round or
hide it. Each renderer writes `<output>.manifest.json` saying where each section lives
(PDF page, MP4 timestamp inside the scene's static hold, HTML section selector). For each
entry, the canonical strings for that section (below) must be found:

  PDF   text layer (always) + OCR of the rendered page (unless --no-ocr)
  MP4   OCR of the held frame (video has no text layer)
  HTML  DOM text of the section (always) + OCR of a static-mode screenshot (unless --no-ocr)

Whole-image OCR skips small chart labels (bar values, waterfall steps). Anything it misses gets
a zoomed second pass before it counts as missing: a 300 dpi crop around the string's own box
for PDFs, and overlapping 2x-upscaled tiles for video frames and screenshots.

Canonical strings per section, taken from report.json (never typed here):
  kpis              every kpi display + delta
  revenue_history   every point display
  segments          every item label + display.share
  bridge            start, every step, end display
  income_statement  every row display, all columns

Usage:
  python verify_outputs.py report.json --pdf out.pdf --mp4 out.mp4 --html out.html
  python verify_outputs.py report.json --pdf out.pdf --no-ocr        # fast, text layer only
Exit 1 if any string is missing anywhere.
"""
import argparse, json, pathlib, re, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def canonical(r):
    s = {}
    s["kpis"] = [x for k in r.get("kpis", []) for x in (k["display"], k["delta"])]
    s["revenue_history"] = [p["display"] for p in r.get("revenue_history", {}).get("points", [])]
    seg = r.get("segments", {}).get("items", [])
    s["segments"] = [x for it in seg for x in (it["label"], it["display"]["share"])]
    br = r.get("bridge")
    s["bridge"] = [br["start"]["display"], *[st["display"] for st in br["steps"]], br["end"]["display"]] if br else []
    s["income_statement"] = [d for row in r.get("income_statement", {}).get("rows", []) for d in row["display"]]
    return s


def norm(t):
    """Compare glyph-insensitively: minus/dash variants, spaces, case, thin spaces."""
    t = t.replace("−", "-").replace("–", "-").replace("—", "-").replace(" ", "").replace(" ", "")
    return re.sub(r"\s+", "", t).lower()


def missing(strings, text):
    n = norm(text)
    return [s for s in strings if norm(s) not in n]


class OCR:
    _impl = None

    @classmethod
    def read(cls, png_bytes):
        if cls._impl is None:
            sys.path.insert(0, str(HERE))
            from readback_ocr import LocalOCR
            cls._impl = LocalOCR()
        return cls._impl(png_bytes)


def zoom_tiles(im, rows=3, cols=2, scale=2):
    """OCR overlapping, upscaled tiles of a PIL image: recovers small chart labels."""
    import io
    from PIL import Image
    W, H, out = im.width, im.height, []
    tw, th = W // cols, H // rows
    for r in range(rows):
        for c in range(cols):
            box = (max(0, c * tw - tw // 4), max(0, r * th - th // 4), min(W, (c + 1) * tw + tw // 4), min(H, (r + 1) * th + th // 4))
            t = im.crop(box)
            t = t.resize((t.width * scale, t.height * scale), Image.LANCZOS)
            buf = io.BytesIO(); t.save(buf, "PNG"); out.append(OCR.read(buf.getvalue()))
    return "\n".join(out)


def ocr_image_missing(want, im):
    """Full-image OCR, then zoomed tiles for whatever it missed."""
    import io
    buf = io.BytesIO(); im.save(buf, "PNG")
    miss = missing(want, OCR.read(buf.getvalue()))
    return missing(miss, zoom_tiles(im)) if miss else miss


def ocr_tall(png_path, tile=1400, overlap=200):
    """OCR a tall screenshot in overlapping tiles (one huge image loses small text)."""
    from PIL import Image
    import io
    im = Image.open(png_path).convert("RGB")
    out, y = [], 0
    while y < im.height:
        buf = io.BytesIO()
        im.crop((0, y, im.width, min(im.height, y + tile))).save(buf, "PNG")
        out.append(OCR.read(buf.getvalue()))
        y += tile - overlap
    return "\n".join(out)


def manifest(path):
    m = pathlib.Path(str(path) + ".manifest.json")  # full filename: report.pdf and report.html can share a stem
    if not m.exists():
        sys.exit(f"no manifest next to {path} (expected {m.name}); the renderer must write one")
    return json.loads(m.read_text())


def entries(path, canon):
    """Manifest entries for sections that carry canonical figures (skips e.g. a hero banner)."""
    return [e for e in manifest(path) if canon.get(e["section"])]


def check_pdf(path, canon, use_ocr):
    import fitz
    doc, rows = fitz.open(path), []
    for e in entries(path, canon):
        pg = doc[e["page"] - 1]
        want = canon[e["section"]]
        rows.append((f"pdf p{e['page']}", e["section"], "text layer", missing(want, pg.get_text("text", clip=fitz.INFINITE_RECT()))))
        if use_ocr:
            miss = missing(want, OCR.read(pg.get_pixmap(dpi=150).tobytes("png")))
            still = []
            for s_ in miss:  # zoom pass: re-read each miss from a 300 dpi crop of its own box
                rects = pg.search_for(s_) or pg.search_for(s_.replace("\u2212", "-"))
                crops = [fitz.Rect(r.x0 - 40, r.y0 - 15, r.x1 + 40, r.y1 + 15) & pg.rect for r in rects]
                seen = any(norm(s_) in norm(OCR.read(pg.get_pixmap(dpi=300, clip=c).tobytes("png"))) for c in crops)
                if not seen:
                    still.append(s_)
            rows.append((f"pdf p{e['page']}", e["section"], "ocr", still))
    return rows


def check_mp4(path, canon, use_ocr):
    rows = []
    if not use_ocr:
        return [("mp4", "-", "skipped", [])]
    for e in entries(path, canon):
        with tempfile.NamedTemporaryFile(suffix=".png") as f:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(e["t"]), "-i", str(path), "-frames:v", "1", f.name], check=True)
            from PIL import Image
            rows.append((f"mp4 t={e['t']}s", e["section"], "ocr", ocr_image_missing(canon[e["section"]], Image.open(f.name).convert("RGB"))))
    return rows


def check_html(path, canon, use_ocr):
    url = pathlib.Path(path).resolve().as_uri() + "?static=1"
    dom = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--virtual-time-budget=8000", "--dump-dom", url],
                         capture_output=True, text=True, timeout=120).stdout
    from html.parser import HTMLParser

    class Sections(HTMLParser):
        def __init__(self):
            super().__init__(); self.stack, self.text = [], {}
        def handle_starttag(self, tag, attrs):
            sec = dict(attrs).get("data-section")
            self.stack.append((tag, sec))
        def handle_endtag(self, tag):
            while self.stack:
                t, _ = self.stack.pop()
                if t == tag:
                    break
        def handle_data(self, d):
            for _, sec in self.stack:
                if sec:
                    self.text[sec] = self.text.get(sec, "") + " " + d

    p = Sections(); p.feed(dom)
    rows = []
    for e in entries(path, canon):
        sec = re.search(r"data-section=['\"]?([\w-]+)", e["selector"]).group(1)
        rows.append(("html", e["section"], "dom", missing(canon[e["section"]], p.text.get(sec, ""))))
    if use_ocr:
        with tempfile.TemporaryDirectory() as td:
            shot = pathlib.Path(td) / "shot.png"
            subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--virtual-time-budget=8000",
                            f"--screenshot={shot}", "--window-size=1280,7000", url], capture_output=True, timeout=120)
            seen = ocr_tall(shot)
            miss_all = sorted({x for e in entries(path, canon) for x in missing(canon[e["section"]], seen)})
            if miss_all:
                from PIL import Image
                im = Image.open(shot).convert("RGB")
                seen += "\n" + zoom_tiles(im, rows=max(1, im.height // 700), cols=2)
        for e in entries(path, canon):
            rows.append(("html", e["section"], "ocr", missing(canon[e["section"]], seen)))
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Tie PDF / MP4 / HTML outputs back to report.json")
    ap.add_argument("report")
    ap.add_argument("--pdf"); ap.add_argument("--mp4"); ap.add_argument("--html")
    ap.add_argument("--no-ocr", action="store_true", help="text layer / DOM only (fast, can't see hidden text)")
    a = ap.parse_args()
    canon = canonical(json.load(open(a.report)))
    rows = []
    if a.pdf: rows += check_pdf(a.pdf, canon, not a.no_ocr)
    if a.mp4: rows += check_mp4(a.mp4, canon, not a.no_ocr)
    if a.html: rows += check_html(a.html, canon, not a.no_ocr)
    bad = 0
    for where, sec, how, miss in rows:
        print(f"{'ok  ' if not miss else 'FAIL'}  {where:<12} {sec:<17} {how:<10}" + (f"  missing: {miss}" if miss else ""))
        bad += bool(miss)
    print("RESULT:", "FAIL" if bad else "PASS — every figure is visible in every output")
    sys.exit(1 if bad else 0)
