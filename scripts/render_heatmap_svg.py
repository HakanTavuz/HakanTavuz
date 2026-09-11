#!/usr/bin/env python3
"""contributions.json → animasyonlu 53 haftalık heatmap SVG."""

from __future__ import annotations

import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from config import prompt_user  # noqa: E402

IN_PATH = os.path.join(HERE, "..", "data", "contributions.json")
OUT_PATH = os.path.join(HERE, "..", "contrib-heatmap.svg")

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL = 12
GAP = 3
STEP = CELL + GAP
PAD = 22
LEFT_LABEL_W = 30
TOP_LABEL_H = 20
TITLEBAR_H = 30

BG = "#0a0e14"
BG2 = "#0d1420"
FRAME = "#30363d"
MUTED = "#7d8590"
TEXT = "#e6edf3"
GREEN = "#39d353"
GOLD = "#f2cc60"
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

COL_T = 0.018
ROW_T = 0.045
CELL_DUR = 0.42


def level_for(count: int, max_count: int) -> int:
    if count == 0 or max_count <= 0:
        return 0
    ratio = count / max_count
    if ratio <= 0.15:
        return 1
    if ratio <= 0.35:
        return 2
    if ratio <= 0.55:
        return 3
    if ratio <= 0.80:
        return 4
    return 5


def build_grid(days: list[dict]) -> list[list]:
    max_count = max((d["count"] for d in days), default=0)
    first = datetime.date.fromisoformat(days[0]["date"])
    lead_pad = (first.weekday() + 1) % 7
    grid: list[list] = []
    col: list = [None] * lead_pad
    for d in days:
        date = datetime.date.fromisoformat(d["date"])
        weekday = (date.weekday() + 1) % 7
        while len(col) < weekday:
            col.append(None)
        col.append((d["date"], d["count"], level_for(d["count"], max_count)))
        if len(col) == 7:
            grid.append(col)
            col = []
    if col:
        while len(col) < 7:
            col.append(None)
        grid.append(col)
    return grid


def render(data: dict) -> str:
    days = data["days"]
    grid = build_grid(days)
    n_cols = len(grid)
    art_w = n_cols * STEP
    art_h = 7 * STEP

    month_labels: list[tuple[int, str]] = []
    seen_months: set[tuple[int, int]] = set()
    for ci, column in enumerate(grid):
        for cell in column:
            if cell is None:
                continue
            date = datetime.date.fromisoformat(cell[0])
            key = (date.year, date.month)
            if key not in seen_months and date.day <= 7:
                seen_months.add(key)
                month_labels.append((ci, date.strftime("%b")))
            break

    canvas_w = PAD + LEFT_LABEL_W + art_w + PAD
    stats_h = 88
    canvas_h = TITLEBAR_H + TOP_LABEL_H + art_h + stats_h + PAD
    user = data.get("username") or prompt_user()

    css = f"""
@keyframes cell {{
  0% {{ opacity: 0; transform: translateY(-6px); }}
  100% {{ opacity: 1; transform: translateY(0); }}
}}
.c {{ opacity: 0; animation: cell {CELL_DUR:.2f}s cubic-bezier(.2,.8,.2,1) both; }}
@media (prefers-reduced-motion: reduce) {{
  .c {{ opacity: 1; animation: none; }}
}}
""".strip()

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
        f'viewBox="0 0 {canvas_w} {canvas_h}">',
        f"<style>{css}</style>",
        f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="{BG}"/>',
        f'<rect x="1" y="1" width="{canvas_w - 2}" height="{canvas_h - 2}" rx="11" fill="none" stroke="{FRAME}"/>',
        f'<rect width="{canvas_w}" height="{TITLEBAR_H}" rx="12" fill="{BG2}"/>',
        f'<rect y="{TITLEBAR_H - 12}" width="{canvas_w}" height="12" fill="{BG2}"/>',
    ]
    for i, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        parts.append(f'<circle cx="{18 + i * 16}" cy="{TITLEBAR_H / 2}" r="5" fill="{color}"/>')
    parts.append(
        f'<text x="72" y="{TITLEBAR_H / 2 + 4}" fill="{MUTED}" font-size="12" font-family="{FONT}">'
        f"{user}@github: ~/contributions --graph</text>"
    )

    grid_top = TITLEBAR_H + TOP_LABEL_H
    grid_left = PAD + LEFT_LABEL_W

    for ci, label in month_labels:
        x = grid_left + ci * STEP
        parts.append(
            f'<text x="{x}" y="{TITLEBAR_H + 16}" fill="{MUTED}" font-size="10" font-family="{FONT}">{label}</text>'
        )

    for wi, wname in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        y = grid_top + wi * STEP + CELL * 0.78
        parts.append(
            f'<text x="{PAD}" y="{y:.1f}" fill="{MUTED}" font-size="10" font-family="{FONT}">{wname}</text>'
        )

    for ci, column in enumerate(grid):
        gx = grid_left + ci * STEP
        for ri, cell in enumerate(column):
            if cell is None:
                continue
            date_s, count, lvl = cell
            gy = grid_top + ri * STEP
            delay = ci * COL_T + ri * ROW_T
            plural = "s" if count != 1 else ""
            parts.append(
                f'<rect class="c" x="{gx}" y="{gy}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{PALETTE[lvl]}" style="animation-delay:{delay:.3f}s">'
                f"<title>{date_s}: {count} contribution{plural}</title></rect>"
            )

    leg_y = grid_top + art_h + 6
    leg_x = canvas_w - PAD - (len(PALETTE) * (CELL - 1) + 70)
    parts.append(
        f'<text x="{leg_x - 28}" y="{leg_y + 10}" fill="{MUTED}" font-size="10" font-family="{FONT}">Less</text>'
    )
    lx = leg_x + 8
    for color in PALETTE:
        parts.append(f'<rect x="{lx}" y="{leg_y}" width="{CELL - 2}" height="{CELL - 2}" rx="2" fill="{color}"/>')
        lx += CELL
    parts.append(
        f'<text x="{lx + 4}" y="{leg_y + 10}" fill="{MUTED}" font-size="10" font-family="{FONT}">More</text>'
    )

    sep_y = leg_y + CELL + 14
    parts.append(f'<line x1="{PAD}" y1="{sep_y}" x2="{canvas_w - PAD}" y2="{sep_y}" stroke="{FRAME}"/>')

    cs = data["current_streak"]["length"]
    ls = data["longest_streak"]["length"]
    total = data["total_contributions"]
    best = data["best_day"]
    rng = data["range"]
    ly = sep_y + 24

    parts.append(
        f'<text x="{PAD}" y="{ly}" font-family="{FONT}" font-size="13">'
        f'<tspan fill="{GREEN}" font-weight="700">{total:,}</tspan>'
        f'<tspan fill="{TEXT}"> contributions in the last year</tspan></text>'
    )
    parts.append(
        f'<text x="{canvas_w - PAD}" y="{ly}" text-anchor="end" fill="{MUTED}" font-size="11" font-family="{FONT}">'
        f'{rng["start"]} → {rng["end"]}</text>'
    )
    ly += 24
    parts.append(
        f'<text x="{PAD}" y="{ly}" font-family="{FONT}" font-size="12" fill="{MUTED}">'
        f'current streak <tspan fill="{GOLD}">{cs} days</tspan>'
        f'  ·  longest <tspan fill="{TEXT}">{ls} days</tspan></text>'
    )
    parts.append(
        f'<text x="{canvas_w - PAD}" y="{ly}" text-anchor="end" fill="{MUTED}" font-size="11" font-family="{FONT}">'
        f'best day {best["count"]} on {best["date"]}</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


def demo_data() -> dict:
    """Username yokken README'nin boş kalmaması için sahte takvim."""
    today = datetime.date.today()
    start = today - datetime.timedelta(days=370)
    days = []
    total = 0
    seed = 1337
    d = start
    while d <= today:
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        count = 0 if (seed % 7) < 3 else (seed % 18)
        days.append({"date": d.isoformat(), "count": count})
        total += count
        d += datetime.timedelta(days=1)
    return {
        "username": prompt_user(),
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "total_contributions": total,
        "active_days": sum(1 for x in days if x["count"]),
        "avg_per_active_day": 0,
        "current_streak": {"length": 3, "start": days[-3]["date"], "end": days[-1]["date"]},
        "longest_streak": {"length": 12, "start": days[40]["date"], "end": days[51]["date"]},
        "best_day": max(days, key=lambda x: x["count"]),
        "monthly": [],
        "days": days,
        "placeholder": True,
    }


def main() -> None:
    if os.path.isfile(IN_PATH):
        with open(IN_PATH, encoding="utf-8") as f:
            data = json.load(f)
    else:
        print("data/contributions.json yok — placeholder heatmap")
        data = demo_data()
    svg = render(data)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {OUT_PATH} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
