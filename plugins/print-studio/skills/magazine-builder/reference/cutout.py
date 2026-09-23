#!/usr/bin/env python3
"""Background removal for cutout figures (the Welcome leaping hero, etc.).
Writes a transparent PNG in place. Usage: python cutout.py welcome_portrait ..."""
import sys, pathlib
from rembg import remove, new_session
from PIL import Image

IMG = pathlib.Path(__file__).resolve().parent.parent / "img"
sess = new_session("isnet-anime")  # anime-tuned matting model

for name in sys.argv[1:]:
    p = IMG / f"{name}.png"
    im = Image.open(p).convert("RGBA")
    out = remove(im, session=sess)
    out.save(p)
    print(f"cut {name} -> transparent {out.size}")
