#!/usr/bin/env python3
"""visual_diff.py — Compara dois screenshots e mede mudança visual.

Uso:
    python3 visual_diff.py antes.png depois.png [--out diff.png] [--threshold 0.12]

Saída: porcentagem de pixels alterados e, opcionalmente, imagem com as
diferenças realçadas em vermelho. Usa apenas PIL (sem dependências extras).
Threshold 0.12 ≈ sensibilidade do pixelmatch padrão.
"""
import argparse
import json

from PIL import Image, ImageChops


def color_diff(px1, px2):
    return max(abs(a - b) for a, b in zip(px1[:3], px2[:3]))


def main(before, after, out, threshold):
    im1 = Image.open(before).convert("RGB")
    im2 = Image.open(after).convert("RGB")
    if im1.size != im2.size:
        im2 = im2.resize(im1.size)
    w, h = im1.size
    d1, d2 = im1.load(), im2.load()
    limit = int(threshold * 255)
    changed = 0
    diff_img = im1.copy() if out else None
    dd = diff_img.load() if out else None
    for y in range(h):
        for x in range(w):
            if color_diff(d1[x, y], d2[x, y]) > limit:
                changed += 1
                if out:
                    dd[x, y] = (255, 0, 64)
    pct = changed / (w * h) * 100
    if out:
        diff_img.save(out)
    print(json.dumps({
        "changed_pixels": changed,
        "total_pixels": w * h,
        "changed_pct": round(pct, 2),
        "verdict": ("sem mudança visual relevante" if pct < 0.1
                    else "mudança pequena" if pct < 2
                    else "mudança moderada" if pct < 10
                    else "mudança grande — revisar intencionalidade"),
        "diff_image": out,
    }, ensure_ascii=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("--out", default=None)
    ap.add_argument("--threshold", type=float, default=0.12)
    a = ap.parse_args()
    main(a.before, a.after, a.out, a.threshold)
