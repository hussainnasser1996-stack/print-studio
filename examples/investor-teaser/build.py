#!/usr/bin/env python3
"""Build the Halcyon Cold Chain sample teaser (pdf-builder, editorial-magazine direction).

Halcyon is a FICTIONAL company. Every figure below is invented for the demo, but the
figures agree with each other: the charts, tables and text all read from DATA.

    python3 build.py            # writes teaser.html + Halcyon-Series-B-Teaser.pdf
"""
import base64, pathlib, platform, shutil, subprocess

HERE = pathlib.Path(__file__).resolve().parent
FONTS = HERE.parents[1] / "plugins/print-studio/skills/magazine-builder/assets/fonts-ttf"
PDF = HERE / "Halcyon-Series-B-Teaser.pdf"

# ---- single source of truth (US$ millions) --------------------------------------
REV = [("FY22", 18.0), ("FY23", 29.5), ("FY24", 44.2), ("FY25E", 63.0)]
MARGIN = {"FY22": -6, "FY23": 4, "FY24": 11, "FY25E": 15}          # EBITDA margin, %
USES = [("New facilities (Riyadh, Dammam, Jeddah)", 22.0),
        ("Fleet electrification", 10.0),
        ("Tracking & forecasting platform", 4.8),
        ("Working capital", 3.2)]
RAISE, PRE = 40.0, 160.0

assert abs(sum(u[1] for u in USES) - RAISE) < 1e-9, "use of funds must foot to the raise"
POST = PRE + RAISE


def ebitda(y, r): return round(r * MARGIN[y] / 100, 1)
def growth(i): return (REV[i][1] / REV[i - 1][1] - 1) * 100
def money(x): return f"({abs(x):.1f})" if x < 0 else f"{x:.1f}"


CAGR = ((REV[-1][1] / REV[0][1]) ** (1 / (len(REV) - 1)) - 1) * 100


def font_face(family, file, weight="100 900", style="normal"):
    b64 = base64.b64encode((FONTS / file).read_bytes()).decode()
    return (f"@font-face{{font-family:'{family}';src:url(data:font/ttf;base64,{b64}) format('truetype');"
            f"font-weight:{weight};font-style:{style};}}")


def revenue_chart():
    """Hand-authored SVG: revenue bars + EBITDA-margin labels. No chart library."""
    w, h, base, top = 300, 150, 122, 18
    mx = max(r for _, r in REV)
    bw, gap = 44, (w - 4 * 44) / 5
    out = [f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="Revenue FY22 to FY25E">']
    for i, (y, r) in enumerate(REV):
        x = gap + i * (bw + gap)
        bh = r / mx * (base - top - 14)
        fill = "var(--accent)" if y.endswith("E") else "var(--ink)"
        op = ' fill-opacity="0.85"' if y.endswith("E") else ""
        out.append(f'<rect x="{x:.1f}" y="{base-bh:.1f}" width="{bw}" height="{bh:.1f}" fill="{fill}"{op}/>')
        out.append(f'<text x="{x+bw/2:.1f}" y="{base-bh-4:.1f}" class="v">{r:.1f}</text>')
        out.append(f'<text x="{x+bw/2:.1f}" y="{base+11}" class="l">{y}</text>')
        out.append(f'<text x="{x+bw/2:.1f}" y="{base+22}" class="m">{MARGIN[y]:+d}%</text>')
    out.append(f'<line x1="0" x2="{w}" y1="{base}" y2="{base}" stroke="var(--rule)" stroke-width="0.6"/>')
    out.append("</svg>")
    return "\n".join(out)


def uses_chart():
    rows = []
    for label, amt in USES:
        pct = amt / RAISE * 100
        rows.append(f'''<div class="use"><div class="use-l"><span>{label}</span><span class="num">{amt:.1f} · {pct:.0f}%</span></div>
<div class="track"><div class="fillbar" style="width:{pct:.1f}%"></div></div></div>''')
    return "\n".join(rows)


def fin_rows():
    out = []
    for i, (y, r) in enumerate(REV):
        g = "—" if i == 0 else f"{growth(i):.1f}%"
        cls = ' class="est"' if y.endswith("E") else ""
        out.append(f"<tr{cls}><td>{y}</td><td class=num>{r:.1f}</td><td class=num>{g}</td>"
                   f"<td class=num>{money(ebitda(y, r))}</td><td class=num>{MARGIN[y]:d}%</td></tr>".replace(">-", ">−"))
    return "\n".join(out)


HTML = (HERE / "teaser.template.html").read_text()
subs = {
    "{{FONTS}}": "".join([
        font_face("Newsreader", "Newsreader.ttf", "200 800"),
        font_face("Newsreader", "Newsreader-Italic.ttf", "200 800", "italic"),
        font_face("Space Mono", "SpaceMono-Regular.ttf", "400"),
        font_face("Space Mono", "SpaceMono-Bold.ttf", "700"),
        font_face("Archivo", "Archivo.ttf", "100 900"),
    ]),
    "{{REV_CHART}}": revenue_chart(),
    "{{USES}}": uses_chart(),
    "{{FIN_ROWS}}": fin_rows(),
    "{{RAISE}}": f"{RAISE:.0f}",
    "{{PRE}}": f"{PRE:.0f}",
    "{{POST}}": f"{POST:.0f}",
    "{{STAKE}}": f"{RAISE / POST * 100:.0f}",
    "{{PRE_MULT}}": f"{PRE / REV[-1][1]:.1f}",
    "{{CAGR}}": f"{CAGR:.1f}",
    "{{REV_LAST}}": f"{REV[-1][1]:.1f}",
    "{{REV_FY24}}": f"{REV[-2][1]:.1f}",
    "{{G_FY24}}": f"{growth(len(REV) - 2):.1f}",
}
for k, v in subs.items():
    HTML = HTML.replace(k, v)
assert "{{" not in HTML, "unfilled placeholder"
(HERE / "teaser.html").write_text(HTML)


def browser():
    if platform.system() == "Darwin":
        return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if platform.system() == "Windows":
        return r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    return shutil.which("chromium") or shutil.which("google-chrome")


subprocess.run([browser(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={PDF}", (HERE / "teaser.html").as_uri()],
               check=True, capture_output=True)
print("wrote", PDF.name)
