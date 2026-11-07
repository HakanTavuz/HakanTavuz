#!/usr/bin/env python3
"""Fotoğrafı (veya prosedürel portreyi) kendini yazan monochrome ASCII SVG'ye çevir."""

from __future__ import annotations

import html
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from config import DISPLAY_NAME, prompt_user  # noqa: E402

SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.jpg")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "portrait-ascii.svg")

# Karakter hücresi dikdörtgen (dar+uzun) olduğundan sütun > satır tutulur ki yüz ezilmesin.
COLS = 92
ROWS = 64
CELL_W = 7
CELL_H = 13
# Koyu arka plana açık mürekkep: AYDINLIK piksel = yoğun karakter, karanlık = boşluk (arka plana erir).
RAMP = " .,:;irsXA253hMHGS#9B&@"

CONTRAST = 1.15
GAMMA = 0.92
WHITE_FLOOR = 0.80  # (artık kullanılmıyor; geriye dönük uyum için duruyor)

# Fotoğrafın yüzü dolduran kare kırpımı (gökyüzü/yol dışarıda kalır)
CROP_L, CROP_R = 0.20, 0.80
CROP_T, CROP_B = 0.15, 0.95

PAD = 20
TITLEBAR_H = 30
STATUS_H = 30
ART_W = COLS * CELL_W
ART_H = ROWS * CELL_H
CANVAS_W = ART_W + PAD * 2
CANVAS_H = TITLEBAR_H + ART_H + STATUS_H + PAD

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
INK = "#c9d1d9"
CURSOR = "#c9d1d9"

ROW_DUR = 0.09
STAGGER = 0.07
STATIC = bool(os.environ.get("STATIC"))


def procedural_grid() -> list[str]:
    """Fotoğraf yoksa gölgeli bir kafa + omuz bas. Boş profil olmasın diye."""
    rows: list[str] = []
    for y in range(ROWS):
        chars: list[str] = []
        ny = (y / (ROWS - 1)) * 2 - 1
        for x in range(COLS):
            nx = (x / (COLS - 1)) * 2 - 1
            lum = 1.0

            hx, hy, rx, ry = 0.02, -0.18, 0.38, 0.50
            dx = (nx - hx) / rx
            dy = (ny - hy) / ry
            d = dx * dx + dy * dy
            if d < 1.0:
                edge = max(0.0, 1.0 - d)
                light = 0.28 + 0.50 * (0.55 - dx * 0.28 - dy * 0.42)
                light *= 0.55 + 0.45 * edge
                if ny < -0.22:
                    light *= 0.32 + 0.25 * max(0.0, ny + 0.55)
                for ex, ey in ((-0.13, -0.18), (0.15, -0.18)):
                    ed = ((nx - ex) / 0.07) ** 2 + ((ny - ey) / 0.045) ** 2
                    if ed < 1.0:
                        light *= 0.22
                nd = ((nx - 0.02) / 0.035) ** 2 + ((ny - 0.02) / 0.08) ** 2
                if nd < 1.0:
                    light *= 0.55
                if -0.08 < nx < 0.12 and 0.18 < ny < 0.28:
                    light *= 0.45
                lum = max(0.04, min(0.92, light))

            sx = abs(nx) / 0.72
            sy = (ny - 0.42) / 0.55
            if sy > 0 and sx * sx + sy * sy * 0.35 < 1.0 and d >= 1.0:
                lum = 0.18 + 0.12 * sx

            if lum >= WHITE_FLOOR:
                chars.append(" ")
                continue
            idx = int((1.0 - lum) * (len(RAMP) - 1) + 0.5)
            idx = max(0, min(len(RAMP) - 1, idx))
            chars.append(RAMP[idx])
        rows.append("".join(chars))
    return rows


def image_grid(path: str) -> list[str]:
    from PIL import Image, ImageEnhance, ImageOps

    im = Image.open(path).convert("L")
    w, h = im.size
    # yüzü dolduran kare kırpım; selfie'nin gökyüzü/yolu dışarıda kalır
    im = im.crop((int(w * CROP_L), int(h * CROP_T), int(w * CROP_R), int(h * CROP_B)))
    im = ImageOps.autocontrast(im, cutoff=2)
    im = ImageEnhance.Contrast(im).enhance(CONTRAST)
    im = im.resize((COLS, ROWS), Image.LANCZOS)
    px = im.load()
    rows: list[str] = []
    for y in range(ROWS):
        ny = (y / (ROWS - 1)) * 2 - 1
        chars: list[str] = []
        for x in range(COLS):
            nx = (x / (COLS - 1)) * 2 - 1
            # oval maske: yüz/kafa ovalinin dışı arka plana (boşluk) erir
            d = (nx / 0.92) ** 2 + ((ny + 0.04) / 0.99) ** 2
            if d > 1.0:
                chars.append(" ")
                continue
            lum = math.pow(px[x, y] / 255.0, GAMMA)
            edge = min(1.0, (1.0 - d) / 0.18)   # kenarda yumuşak geçiş
            lum = lum * (0.35 + 0.65 * edge)     # kenarları karart -> boşluğa eri
            # AYDINLIK = yoğun karakter (koyu arka planda açık mürekkep)
            idx = int(lum * (len(RAMP) - 1) + 0.5)
            idx = max(0, min(len(RAMP) - 1, idx))
            chars.append(RAMP[idx])
        rows.append("".join(chars))
    return rows


def build_svg(rows_txt: list[str]) -> str:
    user = prompt_user()
    art_top = TITLEBAR_H + PAD * 0.35
    font_size = CELL_H * 0.86
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
        f'viewBox="0 0 {CANVAS_W} {CANVAS_H}">',
        f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="{BG}"/>',
        f'<rect x="1" y="1" width="{CANVAS_W - 2}" height="{CANVAS_H - 2}" rx="11" fill="none" stroke="{FRAME}"/>',
        f'<rect width="{CANVAS_W}" height="{TITLEBAR_H}" rx="12" fill="{BG2}"/>',
        f'<rect y="{TITLEBAR_H - 12}" width="{CANVAS_W}" height="12" fill="{BG2}"/>',
    ]
    for i, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        parts.append(f'<circle cx="{18 + i * 16}" cy="{TITLEBAR_H / 2}" r="5" fill="{color}"/>')
    parts.append(
        f'<text x="72" y="{TITLEBAR_H / 2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
        f"{html.escape(user)}@github: ~$ ./portrait.sh</text>"
    )

    parts.append("<defs>")
    for ry in range(len(rows_txt)):
        row_y = art_top + ry * CELL_H
        delay = ry * STAGGER
        if STATIC:
            parts.append(
                f'<clipPath id="wipe{ry}"><rect x="{PAD}" y="{row_y}" width="{ART_W}" height="{CELL_H}"/></clipPath>'
            )
        else:
            parts.append(
                f'<clipPath id="wipe{ry}">'
                f'<rect x="{PAD}" y="{row_y}" width="{ART_W}" height="{CELL_H}">'
                f'<animate attributeName="width" from="0" to="{ART_W}" dur="{ROW_DUR}s" '
                f'begin="{delay:.3f}s" fill="freeze"/>'
                f"</rect></clipPath>"
            )
    parts.append("</defs>")

    for ry, line in enumerate(rows_txt):
        y = art_top + ry * CELL_H + CELL_H * 0.74
        delay = ry * STAGGER
        safe = html.escape(line)
        parts.append(
            f'<text x="{PAD}" y="{y:.2f}" fill="{INK}" font-size="{font_size:.2f}" xml:space="preserve" '
            f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
            f'clip-path="url(#wipe{ry})">{safe}</text>'
        )
        if not STATIC:
            parts.append(
                f'<rect x="{PAD}" y="{art_top + ry * CELL_H + 2:.2f}" width="7" height="{CELL_H - 4}" fill="{CURSOR}" opacity="0">'
                f'<animate attributeName="x" from="{PAD}" to="{PAD + ART_W}" dur="{ROW_DUR}s" '
                f'begin="{delay:.3f}s" fill="freeze"/>'
                f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.08;0.88;1" dur="{ROW_DUR}s" '
                f'begin="{delay:.3f}s" fill="freeze"/>'
                f"</rect>"
            )

    status_y = TITLEBAR_H + ART_H + PAD * 0.55 + 18
    parts.append(
        f'<rect y="{TITLEBAR_H + ART_H + PAD * 0.25}" width="{CANVAS_W}" height="{STATUS_H}" fill="{BG2}"/>'
    )
    parts.append(
        f'<text x="{PAD}" y="{status_y:.2f}" fill="{TITLE_TEXT}" font-size="12" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
        f'{html.escape(user)}@github:~$ whoami  '
        f'<tspan fill="{INK}">{html.escape(DISPLAY_NAME)}</tspan></text>'
    )
    if not STATIC:
        parts.append(
            f'<rect x="{PAD + 210}" y="{status_y - 11}" width="7" height="13" fill="{INK}">'
            f'<animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>'
            f"</rect>"
        )
    parts.append("</svg>")
    return "".join(parts)


def main() -> None:
    if os.path.isfile(SRC):
        try:
            rows = image_grid(SRC)
            print("using photo", SRC)
        except Exception as exc:
            print("photo failed, fallback portrait:", exc)
            rows = procedural_grid()
    else:
        print("no source-prepped.png — procedural portrait")
        rows = procedural_grid()

    svg = build_svg(rows)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", OUT, len(svg), "bytes;", CANVAS_W, "x", CANVAS_H)


if __name__ == "__main__":
    main()
