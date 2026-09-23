#!/usr/bin/env python3
"""Read-back OCR check: does the page a reader SEES match the text the PDF CONTAINS?

The text-layer checks (PyMuPDF get_text) read what the PDF *contains*. They cannot see
what a reader *sees*. A figure can sit in the text layer and still be invisible: white on
white, covered by a box drawn later, pushed off the page, overprinted by a placed element.
And a figure baked into an image (a chart PNG, a screenshot) is visible but absent from
the text layer, so no text check can audit it.

This script renders every page, OCRs the pixels with GLM-OCR (0.9B, MIT, #1 on
OmniDocBench v1.5), and diffs the numbers on each page. Whole-page OCR skips chart labels
and legends, so every number it misses is re-read from a zoomed 300 dpi crop of its own
box before it is reported:

  HIDDEN     in the text layer, NOT visible on the rendered page  -> FAIL
             (white-on-white, covered, off-page, overprinted; or an OCR miss: check zoomed)
  OCR-ONLY   visible on the page, NOT in the text layer           -> REVIEW
             (rasterised figure that no text check can audit, or an OCR misread)
  EXPECTED   a required string (--expect) not visible anywhere   -> FAIL
             (the clipping case: overflow:hidden deletes text from BOTH layers)

Exit code 1 on any FAIL. Run --selftest first on a new machine: it builds a PDF with one
of each defect and confirms the checker fires (a checker that never fires and a clean
document produce identical output).

Backends
  local (default)  transformers on CUDA / Apple MPS / CPU. Nothing leaves the machine.
                   ~2 GB download on first run; ~15-20 s/page on an M1 Pro.
  space            a free public Hugging Face Space (no GPU needed locally, ~10 s/page).
                   SENDS PAGE IMAGES TO A THIRD-PARTY SERVER. Only for public or fictional
                   documents, never for confidential client material.

Setup (a venv is recommended):
  pip install pymupdf pillow torch torchvision "transformers>=5.17" accelerate   # local
  pip install pymupdf pillow gradio_client                                       # space

Usage:
  python readback_ocr.py report.pdf
  python readback_ocr.py report.pdf --expect must_appear.txt --pages 1-3,7
  python readback_ocr.py report.pdf --backend space --json out.json
  python readback_ocr.py --selftest
"""
import argparse, base64, io, json, re, sys, tempfile, time
from collections import Counter

import fitz  # PyMuPDF

MODEL = "zai-org/GLM-OCR"
SPACE = "prithivMLmods/GLM-OCR-Demo"
NOCLIP = fitz.INFINITE_RECT()  # get_text clips to the page by default; off-page text is a defect we want
NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")


def norm_num(tok):
    """'4,820' -> '4820', '27.20' stays '27.20' (a changed decimal is a real difference)."""
    return tok.replace(",", "")


def numbers(text, min_digits):
    out = Counter()
    for m in NUM.finditer(text):
        n = norm_num(m.group()).rstrip(".")
        if sum(c.isdigit() for c in n) >= min_digits:
            out[n] += 1
    return out


def squash(s):
    return re.sub(r"\s+", " ", s.replace("’", "'").replace("–", "-").replace("—", "-")).strip().lower()


def parse_pages(spec, n):
    if not spec:
        return list(range(n))
    pages = []
    for part in spec.split(","):
        a, _, b = part.partition("-")
        pages += range(int(a) - 1, int(b or a))
    return [p for p in pages if 0 <= p < n]


class LocalOCR:
    def __init__(self):
        import torch
        from transformers import AutoProcessor, AutoModelForImageTextToText
        self.torch = torch
        self.dev = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        dtype = torch.float32 if self.dev == "cpu" else torch.bfloat16
        self.proc = AutoProcessor.from_pretrained(MODEL)
        self.model = AutoModelForImageTextToText.from_pretrained(MODEL, dtype=dtype).to(self.dev).eval()

    def __call__(self, png_bytes):
        with tempfile.NamedTemporaryFile(suffix=".png") as f:
            f.write(png_bytes); f.flush()
            msgs = [{"role": "user", "content": [{"type": "image", "url": f.name},
                                                 {"type": "text", "text": "Text Recognition:"}]}]
            inp = self.proc.apply_chat_template(msgs, tokenize=True, add_generation_prompt=True,
                                                return_dict=True, return_tensors="pt").to(self.dev)
            inp.pop("token_type_ids", None)
            with self.torch.inference_mode():
                out = self.model.generate(**inp, max_new_tokens=4096, do_sample=False)
        return self.proc.decode(out[0][inp["input_ids"].shape[1]:], skip_special_tokens=True)


class SpaceOCR:
    def __init__(self):
        from gradio_client import Client
        print(f"!! backend=space: page images are sent to the public Space {SPACE}", file=sys.stderr)
        self.client = Client(SPACE, verbose=False)

    def __call__(self, png_bytes):
        b64 = "data:image/png;base64," + base64.b64encode(png_bytes).decode()
        return self.client.predict("Text", b64, 4096, 60, api_name="/run_router")


def check(pdf_path, backend="local", pages=None, dpi=150, expect=(), min_digits=2, verbose=True):
    doc = fitz.open(pdf_path)
    ocr = LocalOCR() if backend == "local" else SpaceOCR()
    report = {"pdf": str(pdf_path), "backend": backend, "pages": [], "expected_missing": [], "fail": False}
    seen_all = ""
    for i in parse_pages(pages, len(doc)):
        pg = doc[i]
        t0 = time.time()
        seen = ocr(pg.get_pixmap(dpi=dpi).tobytes("png"))
        seen_all += "\n" + seen
        layer = pg.get_text("text", clip=NOCLIP)  # include text placed outside the page
        L, S = numbers(layer, min_digits), numbers(seen, min_digits)
        ocr_only = sorted((S - L).elements())
        words = pg.get_text("words", clip=NOCLIP)
        off_page = [w[4] for w in words if NUM.search(w[4]) and not fitz.Rect(w[:4]).intersects(pg.rect)]
        # Pass 2 (zoom): whole-page OCR skips chart labels, legends and small furniture. Re-read
        # each missing number from a tight crop at 300 dpi; only what is STILL unseen is hidden.
        missing, hidden = L - S, []
        for tok in sorted(missing):
            rects = [fitz.Rect(w[:4]) for w in words
                     if tok in (norm_num(m.group()).rstrip(".") for m in NUM.finditer(w[4]))]
            for r in rects[:missing[tok]]:
                crop = fitz.Rect(r.x0 - 60, r.y0 - 20, r.x1 + 60, r.y1 + 20) & pg.rect
                if crop.is_empty or tok not in numbers(ocr(pg.get_pixmap(dpi=300, clip=crop).tobytes("png")), 1):
                    hidden.append(tok)
            hidden += [tok] * max(0, missing[tok] - len(rects))  # in the text layer but no word box found
        row = {"page": i + 1, "secs": round(time.time() - t0, 1), "numbers_in_layer": sum(L.values()),
               "hidden": hidden, "off_page": off_page, "ocr_only": ocr_only}
        report["pages"].append(row)
        if hidden:
            report["fail"] = True
        if verbose:
            flag = "FAIL" if hidden else ("REVIEW" if ocr_only else "ok")
            print(f"p{i+1:>3}  {flag:<6} {row['numbers_in_layer']:>3} numbers  {row['secs']}s"
                  + (f"\n      HIDDEN   (in PDF, not visible): {hidden}" if hidden else "")
                  + (f"\n      off-page words: {off_page}" if off_page else "")
                  + (f"\n      OCR-ONLY (visible, not in text layer): {ocr_only}" if ocr_only else ""))
    blob = squash(seen_all)
    report["expected_missing"] = [e for e in expect if squash(e) not in blob]
    if report["expected_missing"]:
        report["fail"] = True
        if verbose:
            print(f"EXPECTED strings not visible anywhere: {report['expected_missing']}")
    if verbose:
        print("RESULT:", "FAIL" if report["fail"] else "PASS")
    return report


def selftest(backend):
    """Positive control: one PDF with each defect. Every one must be reported."""
    doc = fitz.open()
    pg = doc.new_page(width=595, height=842)
    ok = "Revenue rose 11.4% to 4,820 million. Operating margin was 27.2%."
    pg.insert_text((60, 100), ok, fontsize=12)
    pg.insert_text((60, 140), "Net debt fell to 1,975 million.", fontsize=12, color=(1, 1, 1))  # white on white
    pg.insert_text((60, 180), "EBITDA reached 3,310 million.", fontsize=12)
    pg.draw_rect(fitz.Rect(150, 165, 260, 186), color=(0.9, 0.9, 0.9), fill=(0.9, 0.9, 0.9))  # covered
    pg.insert_text((700, 220), "Capex was 6,140 million.", fontsize=12)                      # off page
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False).name
    doc.save(tmp)
    rep = check(tmp, backend, expect=["Dividend per share 1.28"], verbose=True)  # clipped: absent everywhere
    hidden = set(rep["pages"][0]["hidden"])
    want = {"1975", "3310", "6140"}
    good = want <= hidden and "Dividend per share 1.28" in rep["expected_missing"] \
        and not ({"4820", "11.4", "27.2"} & hidden)
    print("\nSELFTEST", "PASSED: every planted defect was caught" if good
          else f"FAILED: expected hidden {sorted(want)}, got {sorted(hidden)}")
    return good


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pdf", nargs="?")
    ap.add_argument("--backend", choices=["local", "space"], default="local")
    ap.add_argument("--pages", help="e.g. 1-3,7 (1-based)")
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--expect", help="file: one string per line that must be visible somewhere")
    ap.add_argument("--min-digits", type=int, default=2, help="ignore numbers with fewer digits (folios, footnote marks)")
    ap.add_argument("--json", help="write the full report here")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest(a.backend) else 1)
    if not a.pdf:
        ap.error("pdf is required (or --selftest)")
    exp = [l.strip() for l in open(a.expect, encoding="utf-8") if l.strip()] if a.expect else []
    rep = check(a.pdf, a.backend, a.pages, a.dpi, exp, a.min_digits)
    if a.json:
        json.dump(rep, open(a.json, "w"), indent=2)
    sys.exit(1 if rep["fail"] else 0)
