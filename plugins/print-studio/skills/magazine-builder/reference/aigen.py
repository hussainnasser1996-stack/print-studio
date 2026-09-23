#!/usr/bin/env python3
"""magazine-builder — local, free, original AI illustration recipe.

Generates ORIGINAL anime/style illustrations locally (no cloud, no cost) for magazine
imagery. Prompt original scenes ONLY — never named characters/series/IP.

Setup (one-time): python3 -m pip install torch diffusers transformers accelerate safetensors

KEY GOTCHAS baked in below:
- Apple-Silicon (MPS) + fp16 -> ALL-BLACK images (VAE NaN). Use torch.float32.
- Always check img.getextrema(): near (0,0,0) means black -> regenerate.
- Verify the model id still exists first:
    curl -s -o /dev/null -w "%{http_code}" https://huggingface.co/api/models/<id>   # want 200
- SD1.5 anime models (~2GB) run on 16GB easily. SDXL (e.g. cagliostrolab/animagine-xl-3.1)
  is higher fidelity but heavier/slower -> add pipe.enable_model_cpu_offload().
"""
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler

OUT = "publishing/<proj>/img"            # <- set to your project's img dir
MODEL = "gsdf/Counterfeit-V2.5"          # reliable SD1.5 anime; confirm 200 before running
dev = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
print("[AI] device", dev, "(fp32 to avoid the MPS black-image bug)")

pipe = StableDiffusionPipeline.from_pretrained(MODEL, torch_dtype=torch.float32, safety_checker=None)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
pipe = pipe.to(dev); pipe.enable_attention_slicing()

NEG = ("lowres, worst quality, bad anatomy, bad hands, extra fingers, watermark, signature, "
       "text, jpeg artifacts, blurry, deformed")

# (name, prompt[ORIGINAL scenes only], width, height, seed)
JOBS = [
    ("hero",     "masterpiece, best quality, ultra detailed, a lone swordsman in a long dark coat, "
                 "standing on a cliff at dusk, dramatic rim light, wind, cinematic anime key visual", 512, 768, 11),
    ("desk",     "masterpiece, best quality, an animator's wooden desk, pencils, stacked drawing "
                 "paper, glowing lightbox, warm desk lamp, anime background illustration, no humans", 768, 512, 22),
    ("portrait", "masterpiece, best quality, anime character portrait, long hair, calm cool "
                 "expression, dusk backlight, detailed eyes, upper body", 512, 768, 33),
    ("action",   "masterpiece, best quality, dynamic running pose, motion blur, speed lines, "
                 "dramatic low angle, anime action cut, dusk", 768, 512, 44),
]

import os
os.makedirs(OUT, exist_ok=True)
for name, prompt, w, h, seed in JOBS:
    g = torch.Generator(dev).manual_seed(seed)
    img = pipe(prompt, negative_prompt=NEG, num_inference_steps=26, guidance_scale=7.0,
               width=w, height=h, generator=g).images[0]
    ex = img.getextrema()
    print(f"[AI] {name} extrema={ex}")           # near (0,0,0) -> BLACK, regenerate
    img.save(f"{OUT}/ai_{name}.png")
print("[AI] DONE")
