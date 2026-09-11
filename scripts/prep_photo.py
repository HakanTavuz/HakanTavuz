#!/usr/bin/env python3
"""Fotoğrafı ASCII'ye hazırla: bg sil, CLAHE, beyaz zemin."""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.jpg")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")


def main() -> None:
    import cv2
    import numpy as np
    from PIL import Image
    from rembg import remove

    if not os.path.isfile(INP):
        raise SystemExit(f"kaynak yok: {INP}\nKullanım: python scripts/prep_photo.py source-photo.jpg")

    cut = remove(Image.open(INP).convert("RGBA"))
    rgb = np.array(cut.convert("RGB"))
    alpha = np.array(cut.split()[-1])

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.6, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    gray = cv2.convertScaleAbs(gray, alpha=1.05, beta=18)

    mask = alpha.astype(np.float32) / 255.0
    mask = cv2.GaussianBlur(mask, (0, 0), 1.0)
    out = gray.astype(np.float32) * mask + 255.0 * (1.0 - mask)
    out = np.clip(out, 0, 255).astype(np.uint8)

    Image.fromarray(out, mode="L").save(OUT)
    print("wrote", OUT, out.shape)


if __name__ == "__main__":
    main()
