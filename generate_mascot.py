#!/usr/bin/env python3
"""Premium mascot generator.

Generates N square, cute, personified mascot candidates in a soft claymorphism
art direction, saves PNGs, and writes an HTML preview page. Uses an
OpenRouter-hosted image model; configure the API key via the OPENROUTER_API_KEY
environment variable (see .env.example).

Usage:
    export OPENROUTER_API_KEY=sk-or-...
    python3 generate_mascot.py --subject "rounded owl" --count 3
    python3 generate_mascot.py --subject "chubby fox" --ip1 "#FF6B35" --ip2 "#FFE0C2" --bg "#141821" --style clay
"""
import os
import json
import base64
import random
import colorsys
import argparse
import urllib.request
import urllib.error
from datetime import datetime

def _load_dotenv():
    """Minimal .env loader (no dependency): populate os.environ from ./.env,
    without overwriting variables already set in the environment."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v
    except FileNotFoundError:
        pass


_load_dotenv()

# --- Backend: OpenRouter ---
# OpenRouter routes to image models. Set OPENROUTER_API_KEY in the environment
# (or a local .env). IMAGE_PROXY is optional (only needed if the image model is
# region-locked for you), e.g. IMAGE_PROXY=http://127.0.0.1:7897
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = os.environ.get("OPENROUTER_IMAGE_MODEL", "google/gemini-3.1-flash-image")
PROXY = os.environ.get("IMAGE_PROXY", "")


def _openrouter_image(prompt):
    """Return raw PNG bytes for one image via OpenRouter, or raise."""
    if not OPENROUTER_KEY:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Export it or add it to a local .env "
            "(see .env.example). Get a key at https://openrouter.ai/keys"
        )
    body = json.dumps({
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "modalities": ["image", "text"],
    }).encode()
    req = urllib.request.Request(
        OPENROUTER_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
        },
    )
    handlers = []
    if PROXY:
        handlers.append(urllib.request.ProxyHandler({"http": PROXY, "https": PROXY}))
    opener = urllib.request.build_opener(*handlers)
    try:
        with opener.open(req, timeout=150) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            msg = json.loads(body).get("error", {}).get("message", body)
        except Exception:
            msg = body
        raise RuntimeError(f"HTTP {e.code}: {msg[:300]}")
    if "error" in data:
        raise RuntimeError(data["error"].get("message", json.dumps(data["error"]))[:300])
    imgs = data["choices"][0]["message"].get("images") or []
    if not imgs:
        txt = (data["choices"][0]["message"].get("content") or "")[:200]
        raise RuntimeError(f"no image returned. model said: {txt}")
    url = imgs[0]["image_url"]["url"]
    return base64.b64decode(url.split(",", 1)[1])


BACKENDS = {"openrouter": _openrouter_image}

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUT_DIR, exist_ok=True)

# --- contrast-background rule ---
# The subject keeps its recognizable local color; the background is ONE bright,
# moderately-saturated color whose hue strongly CONTRASTS with the subject
# (roughly near-complementary). That contrast is what makes the mascots read as
# vibrant and eye-catching. Background candidates live in palettes.json.
def _hue(hexs):
    r = int(hexs[1:3], 16) / 255; g = int(hexs[3:5], 16) / 255; b = int(hexs[5:7], 16) / 255
    return colorsys.rgb_to_hsv(r, g, b)[0]


def _load_backgrounds():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "palettes.json")
    try:
        return json.load(open(p)).get("backgrounds", [])
    except Exception:
        return []


BACKGROUNDS = _load_backgrounds()


def contrast_bg(subject_hex, seed=None):
    """Pick a background whose hue strongly contrasts (100-180 deg) with the
    subject's local color -- a vibrant near-complementary pop."""
    sh = _hue(subject_hex)

    def gap(bg):
        d = abs(_hue(bg) - sh)
        return min(d, 1 - d) * 360

    cands = [b for b in BACKGROUNDS if 100 <= gap(b) <= 180]
    if not cands:
        cands = BACKGROUNDS or [subject_hex]
    rnd = random.Random(seed if seed is not None else subject_hex)
    return rnd.choice(cands)

# --- Premium art directions (NOT the flat 2-3 color look) ---
STYLES = {
    "clay": (
        "Soft matte claymorphism: the character looks gently sculpted from smooth "
        "modeling clay, with soft rounded volume. Light it with soft, even, almost frontal "
        "light — only a whisper of gentle shading and no strong directional shadow — and "
        "keep the whole image bright, warm, clean, and vivid. Tactile, premium, "
        "toy-studio quality."
    ),
    "glass": (
        "Refined liquid-glass finish: the character reads as translucent frosted glass "
        "with soft internal light, gentle rim light on the edges, delicate specular "
        "highlights, and a smooth premium gradient in the body. Clean, high-end, "
        "Apple-like material feel, not flat."
    ),
    "gradient": (
        "Premium smooth-gradient finish: rich two-tone body gradient with soft "
        "dimensional shading, a whisper of rim light, gentle floor shadow, refined "
        "and modern. Editorial-grade polish, not a flat sticker."
    ),
}


# ============================================================================
# BASELINE (FROZEN 2026-08-21) — do not change the style; vary only content
# (subject/meme + ip1/ip2 colors). Locked rules baked into build_prompt below:
#   - Style     : soft-matte claymorphism, gentle EVEN near-frontal light, no
#                 strong directional shadow, bright/warm/clean/vivid, low 3D.
#   - Form      : young/baby proportions, one soft rounded body with only a
#                 TINY hint of neck (not an adult head-ball, not a neckless blob).
#   - Eyes      : small, simple, matte, no glossy specular highlights.
#   - Crop      : close upper-body portrait, head large, ears may be top-cropped,
#                 never a full standing body.
#   - Color     : 3-4 colors; subject keeps its local color; background from
#                 --palette contrast (a high-saturation, contrasting hue).
# ============================================================================
def build_prompt(subject, ip1, ip2, bg, style_text, corner):
    return (
        "Create one complete full-bleed 1:1 square image. "
        f"Background: fill the entire square with a smooth solid {bg}, kept clearly "
        "visible in all four square corners and every open area around the character. "
        f"Subject: one extremely simplified, cute, endearing {subject} character, "
        "reduced to one soft rounded continuous silhouette plus one defining feature. "
        "Complexity: only 4-7 large basic shapes, two small simple matte eyes with no "
        "glossy specular highlights (never big round shiny cartoon eyes), and one tiny mouth "
        "only if it helps the expression. Remove every nonessential line, outline, "
        "anatomical detail, and decoration. The character must stay recognizable at 32x32. "
        f"Color: build the character mainly from {ip1} and {ip2}, organized into broad "
        "purposeful masses, reused for the tiny facial marks. Keep the character and the "
        "background clearly separated. "
        f"Composition: frame every character identically as a close portrait, upright, "
        f"emerging from the {corner} and filling 75-85% of the square. The head and body read "
        "as one soft rounded form, joined by only a very slight, barely-there narrowing where "
        "the head meets the body — just a tiny hint of a neck. Avoid both extremes: not a "
        "distinct head-ball sitting on shoulders (too adult), and not a perfectly seamless "
        "neckless blob. The face is set low, cheeks soft, and the head-to-body transition "
        "stays gentle and subtle. Keep it a close crop; do not zoom out to show a small full "
        "standing body. The top of the head or ears may be lightly cropped by the upper edge. "
        f"Style: {style_text} Make simplification, cuteness, and lovable baby-like appeal "
        "the strongest qualities: large soft forms, compact proportions, thick rounded "
        "contours. The character must look YOUNG and baby-like — a chubby-cheeked infant "
        "puppy/kitten, not an adult: soft rounded body lines everywhere, rounded and plump "
        "but never skinny and never fat. Prefer one clear shape over explanatory detail. Keep "
        "the finish clean and soft-matte with gentle even volume — not glossy, wet-looking, "
        "or hyper-3D. "
        "Finish: only the character on the full-canvas background, with normal square outer corners. "
        "Constraints: no text, no watermark, no borders, frames, cards, or presentation "
        "masks. One character only, no extra subjects or scenery. No sharp tips, no fragile "
        "lines, no busy tiny details. Keep the background solid and uniform with no texture, "
        "vignette, or scenery."
    )


def generate(subject, ip1, ip2, bg, style, count, backend):
    style_text = STYLES.get(style, STYLES["clay"])
    corners = ["lower-left corner", "lower-right corner", "lower-center"]
    make_image = BACKENDS[backend]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = []
    for i in range(count):
        corner = corners[i % len(corners)]
        prompt = build_prompt(subject, ip1, ip2, bg, style_text, corner)
        label = f"{style}_{i+1}"
        print(f"\n=== generating {label} ({corner}) via {backend} ===")
        try:
            png = make_image(prompt)
            fname = f"mascot_{subject.replace(' ', '-')}_{style}_{i+1}_{ts}.png"
            fpath = os.path.join(OUT_DIR, fname)
            with open(fpath, "wb") as f:
                f.write(png)
            print(f"[OK] {fpath}")
            results.append((label, fname, prompt))
        except Exception as e:
            print(f"[FAIL] {label}: {e}")
    return ts, results


def write_preview(subject, ip1, ip2, bg, style, ts, results):
    if not results:
        return None
    cards = ""
    for label, fname, _ in results:
        cards += (
            f'<figure><img src="{fname}" alt="{label}"/>'
            f'<figcaption>{label}</figcaption></figure>'
        )
    html = f"""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<title>Mascot preview — {subject}</title>
<style>
 body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
   background:#0e0e11;color:#e8e8ea;padding:32px}}
 h1{{font-weight:600;font-size:18px;margin:0 0 4px}}
 .meta{{color:#8a8a90;font-size:13px;margin-bottom:24px}}
 .grid{{display:flex;flex-wrap:wrap;gap:20px}}
 figure{{margin:0;background:#17171b;border-radius:16px;padding:12px;width:280px}}
 img{{width:256px;height:256px;border-radius:12px;display:block;background:{bg}}}
 figcaption{{text-align:center;color:#a8a8 b0;font-size:12px;margin-top:8px;letter-spacing:.08em;text-transform:uppercase}}
 .sw{{display:inline-block;width:12px;height:12px;border-radius:3px;vertical-align:middle;margin-right:4px;border:1px solid #333}}
</style></head><body>
<h1>Mascot preview — {subject} · style: {style}</h1>
<div class="meta">
 <span class="sw" style="background:{ip1}"></span>{ip1}
 &nbsp;<span class="sw" style="background:{ip2}"></span>{ip2}
 &nbsp;<span class="sw" style="background:{bg}"></span>{bg} (bg)
 &nbsp;· {ts}
</div>
<div class="grid">{cards}</div>
</body></html>"""
    path = os.path.join(OUT_DIR, f"preview_{ts}.html")
    with open(path, "w") as f:
        f.write(html)
    return path


def main():
    global OUT_DIR
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=None, help="output directory (default: ./output)")
    ap.add_argument("--subject", default="rounded owl")
    ap.add_argument("--ip1", default="#5B8DEF")
    ap.add_argument("--ip2", default="#EAF1FF")
    ap.add_argument("--bg", default="#111621")
    ap.add_argument("--style", default="clay", choices=list(STYLES.keys()))
    ap.add_argument("--count", type=int, default=3)
    ap.add_argument("--backend", default="openrouter", choices=list(BACKENDS.keys()))
    ap.add_argument("--palette", default="manual", choices=["manual", "contrast"],
                    help="contrast = keep the subject's local color and auto-pick a "
                         "contrasting bright background from palettes.json")
    args = ap.parse_args()

    if args.outdir:
        OUT_DIR = os.path.abspath(args.outdir)
        os.makedirs(OUT_DIR, exist_ok=True)

    if args.palette == "contrast":
        args.bg = contrast_bg(args.ip1, seed=args.subject)
        print(f"[palette=contrast] subject color {args.ip1} -> contrasting bg {args.bg}")

    print(f"backend={args.backend} subject={args.subject} style={args.style} count={args.count}")
    print(f"colors: ip1={args.ip1} ip2={args.ip2} bg={args.bg}")
    ts, results = generate(args.subject, args.ip1, args.ip2, args.bg, args.style, args.count, args.backend)
    preview = write_preview(args.subject, args.ip1, args.ip2, args.bg, args.style, ts, results)
    print(f"\nGenerated {len(results)} image(s) in {OUT_DIR}")
    if preview:
        print(f"Preview page: {preview}")


if __name__ == "__main__":
    main()
