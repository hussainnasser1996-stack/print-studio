#!/usr/bin/env python3
"""Download the magazine-builder fonts (all SIL Open Font License) from Google Fonts' GitHub.

The full install ships these fonts already. Use this script only when you installed a
"lite" copy of the skill without them (some skill registries cap upload size).

    python3 scripts/fetch_fonts.py          # fills assets/fonts-ttf/
"""
import pathlib, urllib.request

BASE = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
FONTS = {
    "Anton-Regular.ttf": "anton/Anton-Regular.ttf",
    "Archivo.ttf": "archivo/Archivo%5Bwdth,wght%5D.ttf",
    "ArchivoBlack-Regular.ttf": "archivoblack/ArchivoBlack-Regular.ttf",
    "Caveat.ttf": "caveat/Caveat%5Bwght%5D.ttf",
    "Newsreader.ttf": "newsreader/Newsreader%5Bopsz,wght%5D.ttf",
    "Newsreader-Italic.ttf": "newsreader/Newsreader-Italic%5Bopsz,wght%5D.ttf",
    "SpaceMono-Regular.ttf": "spacemono/SpaceMono-Regular.ttf",
    "SpaceMono-Bold.ttf": "spacemono/SpaceMono-Bold.ttf",
}
dest = pathlib.Path(__file__).resolve().parent.parent / "assets" / "fonts-ttf"
dest.mkdir(parents=True, exist_ok=True)
for name, path in FONTS.items():
    out = dest / name
    if out.exists() and out.stat().st_size > 10_000:
        print("have", name); continue
    urllib.request.urlretrieve(BASE + path, out)
    print("got ", name, out.stat().st_size, "bytes")
print("fonts ready in", dest)
