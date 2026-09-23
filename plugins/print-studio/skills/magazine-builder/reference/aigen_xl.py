#!/usr/bin/env python3
"""ANIMA image engine — Animagine XL 4.0 on Apple MPS.

The quality jump over the old SD1.5 (Counterfeit) pipeline. Every image is
ORIGINAL and ownable: no copyrighted characters, no real-franchise names in
prompts. Original anime-style heroes, environments, and motifs only.

Gotchas baked in:
  * MPS + SDXL fp16 VAE -> NaN -> black images. Fix = madebyollin/sdxl-vae-fp16-fix.
  * Animagine 4.0 wants Euler-a + its quality-tag template.
  * 16GB unified RAM -> attention/vae slicing, one image at a time.

Usage:  python aigen_xl.py jobs.json
        jobs.json = [{"name","prompt","neg"?,"w","h","seed","steps"?,"cfg"?}, ...]
"""
import sys, os, json, gc, pathlib
import torch
from diffusers import StableDiffusionXLPipeline, EulerAncestralDiscreteScheduler
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
IMG = HERE.parent / "img"
IMG.mkdir(exist_ok=True)

MODEL = "cagliostrolab/animagine-xl-4.0"
# Apple MPS recipe (hard-won): fp16 UNet/encoders + VAE upcast to fp32
# (pipe.upcast_vae()) + NO attention slicing. ~3 min/img, fits 16GB, full colour.
#   * The all-black/NaN bug is caused by enable_attention_slicing() on MPS fp16
#     (it NaNs the UNet latents), NOT by the dtype and NOT by the VAE. Leave
#     slicing OFF. upcast_vae() prevents the separate fp16-VAE overflow.
#   * float32-everywhere is also correct but the ~14GB model swap-thrashes a
#     16GB Mac -> ~50 min/img. Only use ANIMA_DTYPE=fp32 as a fallback.
DTYPE = torch.float32 if os.environ.get("ANIMA_DTYPE") == "fp32" else torch.float16
UPSCALE = float(os.environ.get("ANIMA_UPSCALE", "1.7"))

# Animagine 4.0 recommended template
QUALITY = "masterpiece, high score, great score, absurdres, "
NEG = ("lowres, bad anatomy, bad hands, text, error, missing finger, extra digits, "
       "fewer digits, cropped, worst quality, low quality, low score, bad score, "
       "average score, signature, watermark, username, blurry, jpeg artifacts, "
       "ugly, deformed, photo, 3d render")

_pipe = None
def pipe():
    global _pipe
    if _pipe is None:
        print(f"loading Animagine XL 4.0 ({DTYPE})…", flush=True)
        p = StableDiffusionXLPipeline.from_pretrained(
            MODEL, torch_dtype=DTYPE, use_safetensors=True, add_watermarker=False)
        p.scheduler = EulerAncestralDiscreteScheduler.from_config(p.scheduler.config)
        p = p.to("mps")
        if DTYPE == torch.float16:
            p.upcast_vae()          # VAE in fp32 -> no NaN/black, UNet stays fast fp16
        if os.environ.get("ANIMA_SLICE") == "1":
            p.enable_attention_slicing()
        _pipe = p
    return _pipe

def gen(job):
    name = job["name"]
    out = IMG / f"{name}.png"
    prompt = QUALITY + job["prompt"]
    neg = job.get("neg", "") + (", " if job.get("neg") else "") + NEG
    w, h = job["w"], job["h"]
    steps = job.get("steps", 30)
    cfg = job.get("cfg", 6.0)
    seed = job.get("seed", 0)
    g = torch.Generator(device="mps").manual_seed(seed)
    print(f"[{name}] {w}x{h} steps={steps} cfg={cfg} seed={seed}", flush=True)
    img = pipe()(prompt=prompt, negative_prompt=neg, width=w, height=h,
                 num_inference_steps=steps, guidance_scale=cfg, generator=g).images[0]
    ex = img.getextrema()
    flat = all(lo == hi for lo, hi in ex) if isinstance(ex[0], tuple) else (ex[0] == ex[1])
    if flat:
        print(f"[{name}] !! flat/black image — NaN", flush=True)
    if UPSCALE > 1.01:
        img = img.resize((int(w * UPSCALE), int(h * UPSCALE)), Image.LANCZOS)
    img.save(out)
    print(f"[{name}] saved {out} {img.size}  extrema={ex}", flush=True)
    gc.collect()
    return out

if __name__ == "__main__":
    jobs = json.load(open(sys.argv[1]))
    if len(sys.argv) > 2:  # optional name filter
        only = set(sys.argv[2].split(","))
        jobs = [j for j in jobs if j["name"] in only]
    for j in jobs:
        gen(j)
    print("ALL DONE", flush=True)
