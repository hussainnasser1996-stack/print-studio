#!/usr/bin/env python3
"""Self-healing batch driver for ANIMA art generation.

Each image runs in its OWN subprocess (so MPS memory is fully freed between
images — the persistent-pipe approach swap-thrashes a 16GB Mac and stalls).
Per-image HARD TIMEOUT + retry on stall/black/wrong-size. Logs with timestamps.

Usage: python src/driver.py name1 name2 ...   (default: all not-yet-real)
"""
import sys, os, json, time, subprocess, pathlib
from datetime import datetime
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
IMG = ROOT / "img"
JOBS = {j["name"]: j for j in json.load(open(HERE / "jobs.json"))}
UPSCALE = 1.7
TIMEOUT = 480          # 8 min hard cap per image
RETRIES = 3

def ts():
    return datetime.now().strftime("%H:%M:%S")

def is_real(name):
    """Real = generated at the upscaled size and not flat/black."""
    p = IMG / f"{name}.png"
    if not p.exists():
        return False
    j = JOBS[name]
    want_w = int(j["w"] * UPSCALE)
    im = Image.open(p)
    if abs(im.size[0] - want_w) > 4:
        return False                       # still a placeholder / wrong size
    ex = im.getextrema()
    return not all(lo == hi for lo, hi in ex[:3])   # not black/flat

def gen_one(name):
    env = dict(os.environ, ANIMA_UPSCALE=str(UPSCALE))
    try:
        subprocess.run(
            [sys.executable, str(HERE / "aigen_xl.py"), str(HERE / "jobs.json"), name],
            env=env, timeout=TIMEOUT,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        print(f"[{ts()}] {name} TIMEOUT after {TIMEOUT}s — killed", flush=True)

def main():
    names = sys.argv[1:] or list(JOBS.keys())
    todo = [n for n in names if not is_real(n)]
    print(f"[{ts()}] driver start — {len(todo)}/{len(names)} need generating: {todo}", flush=True)
    for i, name in enumerate(todo, 1):
        for attempt in range(1, RETRIES + 1):
            t0 = time.time()
            print(f"[{ts()}] ({i}/{len(todo)}) {name} attempt {attempt}…", flush=True)
            gen_one(name)
            if is_real(name):
                print(f"[{ts()}] ({i}/{len(todo)}) {name} OK  ({int(time.time()-t0)}s)", flush=True)
                break
            print(f"[{ts()}] {name} FAILED verify (attempt {attempt})", flush=True)
        else:
            print(f"[{ts()}] {name} GIVING UP after {RETRIES} tries", flush=True)
    remaining = [n for n in names if not is_real(n)]
    print(f"[{ts()}] BATCH COMPLETE — still missing: {remaining or 'none'}", flush=True)

if __name__ == "__main__":
    main()
