#!/usr/bin/env python3
"""Neofetch tarzı info kartı — satır satır fade + slide."""

from __future__ import annotations

import html
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from config import DISPLAY_NAME, INFO_ROWS, LOCATION, ROLE, prompt_user  # noqa: E402

OUT = os.path.join(HERE, "..", "info-card.svg")

SVG_W = 490
SVG_H = 360
BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
LABEL = "#7ee787"
VALUE = "#c9d1d9"
MUTED = "#7d8590"
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

TITLEBAR_H = 36
LINE_H = 28
STAGGER = 0.22
FADE_DUR = 0.38
STATIC = os.environ.get("STATIC", "").strip().lower() in {"1", "true", "yes"}


def rows() -> list[tuple[str, str]]:
    return [
        ("Name", DISPLAY_NAME),
        ("Role", ROLE),
        ("Location", LOCATION),
        *INFO_ROWS,
    ]


def build_svg() -> str:
    user = prompt_user()
    title = f"{user}@github:~"
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{SVG_H}" '
        f'viewBox="0 0 {SVG_W} {SVG_H}">',
        f'<rect width="{SVG_W}" height="{SVG_H}" rx="10" fill="{BG}"/>',
        f'<rect x="1" y="1" width="{SVG_W - 2}" height="{SVG_H - 2}" rx="9" fill="none" stroke="{FRAME}"/>',
        f'<rect width="{SVG_W}" height="{TITLEBAR_H}" rx="10" fill="{BG2}"/>',
        f'<rect y="{TITLEBAR_H - 10}" width="{SVG_W}" height="10" fill="{BG2}"/>',
    ]
    for i, color in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        parts.append(f'<circle cx="{20 + i * 20}" cy="{TITLEBAR_H / 2 + 1}" r="6" fill="{color}"/>')
    parts.append(
        f'<text x="88" y="{TITLEBAR_H / 2 + 5}" fill="{MUTED}" font-size="13" font-family="{FONT}">'
        f"{html.escape(title)}</text>"
    )
    parts.append(f'<line x1="0" y1="{TITLEBAR_H + 1}" x2="{SVG_W}" y2="{TITLEBAR_H + 1}" stroke="{FRAME}"/>')

    content_y = TITLEBAR_H + 32
    for i, (label, value) in enumerate(rows()):
        y = content_y + i * LINE_H
        begin = f"{i * STAGGER:.2f}s"
        if STATIC:
            parts.append(f'<g transform="translate(28 {y})">')
        else:
            parts.append(f'<g transform="translate(28 {y})" opacity="0">')
            parts.append(
                f'<animate attributeName="opacity" from="0" to="1" dur="{FADE_DUR}s" begin="{begin}" fill="freeze"/>'
            )
            parts.append(
                '<animateTransform attributeName="transform" type="translate" '
                f'from="42 {y}" to="28 {y}" dur="{FADE_DUR}s" begin="{begin}" fill="freeze"/>'
            )
        parts.append(
            f'<text font-family="{FONT}" font-size="13">'
            f'<tspan fill="{LABEL}">{html.escape(label)}</tspan>'
            f'<tspan fill="{MUTED}">  │  </tspan>'
            f'<tspan fill="{VALUE}">{html.escape(value)}</tspan>'
            f"</text>"
        )
        parts.append("</g>")

    accent_y = SVG_H - 18
    colors = ["#ff5f57", "#febc2e", "#28c840", "#2ea5ff", "#a06cd5", "#ff6ac1"]
    seg_w = (SVG_W - 56) / len(colors)
    for i, c in enumerate(colors):
        x = 28 + i * seg_w
        parts.append(f'<rect x="{x:.2f}" y="{accent_y}" width="{seg_w - 4:.2f}" height="4" rx="1" fill="{c}"/>')
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    svg = build_svg()
    try:
        ET.fromstring(svg)
    except ET.ParseError as exc:
        raise SystemExit(f"bozuk SVG: {exc}") from exc
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", OUT, len(svg), "bytes")


if __name__ == "__main__":
    main()
