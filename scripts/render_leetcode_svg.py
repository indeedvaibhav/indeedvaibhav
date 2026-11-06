#!/usr/bin/env python3
"""Render the saved LeetCode totals and earned badges as one self-contained SVG."""
from __future__ import annotations

import html
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data" / "leetcode.json").read_text(encoding="utf-8"))
BADGE_DIR = ROOT / "assets" / "leetcode-badges"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def image_url(filename: str) -> str | None:
    path = (BADGE_DIR / filename).resolve()
    if BADGE_DIR.resolve() not in path.parents or not path.is_file():
        return None
    if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        return None
    encoded_name = quote(path.name)
    return (
        "https://raw.githubusercontent.com/indeedvaibhav/"
        f"indeedvaibhav/main/assets/leetcode-badges/{encoded_name}"
    )


def render() -> str:
    width = 850
    badges = DATA.get("badges", [])
    columns = 4
    card_w, card_h, gap = 194, 92, 10
    rows = max(1, (len(badges) + columns - 1) // columns)
    badge_top = 190
    height = badge_top + rows * card_h + (rows - 1) * gap + 44
    solved = DATA["solved"]
    colors = {"easy": "#00b8a3", "medium": "#ffc01e", "hard": "#ef4743"}

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace">',
        '<rect width="100%" height="100%" rx="12" fill="#0d1117"/>',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="none" stroke="#30363d"/>',
        f'<line x1="0" y1="38" x2="{width}" y2="38" stroke="#30363d"/>',
        '<circle cx="18" cy="19" r="4" fill="#ff5f56"/><circle cx="32" cy="19" r="4" fill="#ffbd2e"/><circle cx="46" cy="19" r="4" fill="#27c93f"/>',
        '<text x="425" y="23" fill="#8b949e" font-size="12" text-anchor="middle">indeedvaibhav@leetcode: ~/progress</text>',
        f'<text x="30" y="105" fill="#e6edf3" font-size="46" font-weight="700">{int(solved["all"]):,}</text>',
        '<text x="32" y="128" fill="#8b949e" font-size="12">problems solved</text>',
    ]

    labels = [("Easy", "easy"), ("Medium", "medium"), ("Hard", "hard")]
    start_x, panel_w, panel_gap = 245, 184, 16
    for index, (label, key) in enumerate(labels):
        x = start_x + index * (panel_w + panel_gap)
        parts.extend(
            [
                f'<rect x="{x}" y="60" width="{panel_w}" height="72" rx="9" fill="#161b22" stroke="#30363d"/>',
                f'<text x="{x + 14}" y="86" fill="#8b949e" font-size="11">{label}</text>',
                f'<text x="{x + 14}" y="116" fill="{colors[key]}" font-size="25" font-weight="700">{int(solved[key]):,}</text>',
            ]
        )

    parts.append(f'<text x="28" y="170" fill="#8b949e" font-size="11">EARNED BADGES · {len(badges)}</text>')
    if not badges:
        parts.append(f'<text x="28" y="{badge_top + 36}" fill="#8b949e" font-size="12">No profile badges yet</text>')

    for index, badge in enumerate(badges):
        column, row = index % columns, index // columns
        x = 28 + column * (card_w + gap)
        y = badge_top + row * (card_h + gap)
        parts.append(f'<rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" rx="9" fill="#161b22" stroke="#30363d"/>')
        icon = image_url(str(badge.get("icon_file", "")))
        if icon:
            parts.append(f'<image href="{esc(icon)}" x="{x + 10}" y="{y + 16}" width="60" height="60" preserveAspectRatio="xMidYMid meet"/>')
        else:
            parts.append(f'<circle cx="{x + 40}" cy="{y + 46}" r="27" fill="#21262d" stroke="#58a6ff"/>')
            parts.append(f'<text x="{x + 40}" y="{y + 50}" text-anchor="middle" fill="#58a6ff" font-size="10">LC</text>')
        name = str(badge.get("name", "LeetCode Badge"))
        if len(name) > 19:
            name = name[:18] + "…"
        parts.append(f'<text x="{x + 78}" y="{y + 39}" fill="#e6edf3" font-size="11">{esc(name)}</text>')
        if badge.get("earned_at"):
            parts.append(f'<text x="{x + 78}" y="{y + 58}" fill="#8b949e" font-size="9">{esc(badge["earned_at"])}</text>')

    parts.append(f'<text x="{width - 22}" y="{height - 15}" fill="#6e7681" font-size="9" text-anchor="end">Updated {esc(DATA["fetched_at"][:10])}</text>')
    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    (ROOT / "leetcode.svg").write_text(render(), encoding="utf-8")
    print("Rendered leetcode.svg")
