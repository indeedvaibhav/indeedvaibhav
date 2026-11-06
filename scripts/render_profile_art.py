#!/usr/bin/env python3
"""Render the contribution heatmap and terminal stats card as self-contained SVGs."""
from __future__ import annotations

import datetime as dt
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data" / "contributions.json").read_text(encoding="utf-8"))
DAYS = DATA["days"]
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
MUTED, TEXT, CYAN = "#8b949e", "#e6edf3", "#58a6ff"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def level(count: int) -> int:
    if count == 0:
        return 0
    if count <= 3:
        return 1
    if count <= 8:
        return 2
    if count <= 15:
        return 3
    return 4


def heatmap() -> str:
    first = dt.date.fromisoformat(DAYS[0]["date"])
    start = first - dt.timedelta(days=(first.weekday() + 1) % 7)
    columns = []
    for index, item in enumerate(DAYS):
        day = dt.date.fromisoformat(item["date"])
        column = (day - start).days // 7
        while len(columns) <= column:
            columns.append([])
        columns[column].append((day, item["count"]))

    width, height, cell, gap = 850, 240, 11, 4
    left, top = 34, 66
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace">',
        '<rect width="100%" height="100%" rx="12" fill="#0d1117"/>',
        '<rect x="0.5" y="0.5" width="849" height="239" rx="12" fill="none" stroke="#30363d"/>',
        '<line x1="0" y1="38" x2="850" y2="38" stroke="#30363d"/>',
        '<circle cx="18" cy="19" r="4" fill="#ff5f56"/><circle cx="32" cy="19" r="4" fill="#ffbd2e"/><circle cx="46" cy="19" r="4" fill="#27c93f"/>',
        '<text x="425" y="23" fill="#8b949e" font-size="12" text-anchor="middle">indeedvaibhav@github: ~/contributions</text>',
    ]
    seen = set()
    for ci, column in enumerate(columns):
        for day, count in column:
            x = left + ci * (cell + gap)
            y = top + ((day.weekday() + 1) % 7) * (cell + gap)
            if day.day <= 7 and day.strftime("%Y-%m") not in seen:
                seen.add(day.strftime("%Y-%m"))
                parts.append(f'<text x="{x}" y="56" fill="{MUTED}" font-size="10">{esc(day.strftime("%b"))}</text>')
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{PALETTE[level(count)]}">'
                f'<title>{esc(day.isoformat())}: {count} contribution{"s" if count != 1 else ""}</title></rect>'
            )
    for row, label in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        y = top + row * (cell + gap) + 9
        parts.append(f'<text x="4" y="{y}" fill="{MUTED}" font-size="9">{label}</text>')
    parts.extend([
        f'<text x="34" y="207" fill="{MUTED}" font-size="10">{DATA["total_contributions"]:,} contributions in the last year</text>',
        '<text x="565" y="207" fill="#8b949e" font-size="10">Less</text>',
    ])
    lx = 594
    for color in PALETTE:
        parts.append(f'<rect x="{lx}" y="198" width="11" height="11" rx="2" fill="{color}"/>')
        lx += 15
    parts.extend([
        f'<text x="{lx + 2}" y="207" fill="#8b949e" font-size="10">More</text>',
        f'<text x="34" y="225" fill="{CYAN}" font-size="10">Current streak: {DATA["current_streak"]} days</text>',
        f'<text x="245" y="225" fill="{MUTED}" font-size="10">Longest: {DATA["longest_streak"]} days</text>',
        '</svg>',
    ])
    return "".join(parts)


def stats() -> str:
    width, height = 760, 310
    total = DATA["total_contributions"]
    active = DATA["active_days"]
    current = DATA["current_streak"]
    longest = DATA["longest_streak"]
    best = DATA["best_day"]
    tiles = [
        ("$ contributions", f"{total:,}", "in the last year"),
        ("$ active days", f"{active:,}", "days with activity"),
        ("$ current streak", f"{current}", "days"),
        ("$ longest streak", f"{longest}", "days"),
    ]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace">',
        '<rect width="100%" height="100%" rx="12" fill="#0d1117"/>',
        '<rect x="0.5" y="0.5" width="759" height="309" rx="12" fill="none" stroke="#30363d"/>',
        '<line x1="0" y1="38" x2="760" y2="38" stroke="#30363d"/>',
        '<circle cx="18" cy="19" r="4" fill="#ff5f56"/><circle cx="32" cy="19" r="4" fill="#ffbd2e"/><circle cx="46" cy="19" r="4" fill="#27c93f"/>',
        '<text x="380" y="23" fill="#8b949e" font-size="12" text-anchor="middle">indeedvaibhav@github: ~/stats</text>',
    ]
    for index, (label, value, caption) in enumerate(tiles):
        col, row = index % 2, index // 2
        x, y = 20 + col * 365, 56 + row * 108
        parts.extend([
            f'<rect x="{x}" y="{y}" width="345" height="92" rx="9" fill="#161b22" stroke="#30363d"/>',
            f'<text x="{x + 16}" y="{y + 25}" fill="{MUTED}" font-size="12">{esc(label)}</text>',
            f'<text x="{x + 16}" y="{y + 59}" fill="{CYAN if index == 2 else TEXT}" font-size="24" font-weight="700">{esc(value)}</text>',
            f'<text x="{x + 16}" y="{y + 79}" fill="{MUTED}" font-size="10">{esc(caption)}</text>',
        ])
    parts.extend([
        f'<text x="20" y="288" fill="{MUTED}" font-size="11">Best day: {esc(best["count"])} contributions · {esc(best["date"])}</text>',
        f'<text x="740" y="288" fill="{MUTED}" font-size="10" text-anchor="end">Updated {esc(DATA["generated_at"][:10])}</text>',
        '</svg>',
    ])
    return "".join(parts)


if __name__ == "__main__":
    (ROOT / "contrib-heatmap.svg").write_text(heatmap(), encoding="utf-8")
    (ROOT / "stats.svg").write_text(stats(), encoding="utf-8")
    print("Rendered contrib-heatmap.svg and stats.svg")

