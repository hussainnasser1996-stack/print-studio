#!/usr/bin/env python3
"""Restore the binary assets a "lite" install leaves out: the fonts (all SIL Open Font
License, from Google Fonts' GitHub) and the sample cover image used by reference/template.typ.

The full install ships these already. Run this only when you installed a lite copy
(some skill registries cap file size or accept text files only).

    python3 scripts/fetch_fonts.py          # fills assets/fonts-ttf/ and reference/img/
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

cover = dest.parent.parent / "reference" / "img" / "cover.jpg"
if not cover.exists():
    cover.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve("https://raw.githubusercontent.com/hussainnasser1996-stack/print-studio/main/"
                               "plugins/print-studio/skills/magazine-builder/reference/img/cover.jpg", cover)
    print("got  sample cover", cover.stat().st_size, "bytes")
