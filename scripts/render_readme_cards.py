#!/usr/bin/env python3
"""Render the seven animated, self-contained SVG cards used by the profile README."""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cards"
DATA = json.loads((ROOT / "data" / "contributions.json").read_text(encoding="utf-8"))

BG = "#0b0d12"
PANEL = "#11141b"
TEXT = "#f1f3f5"
MUTED = "#9299a5"
DIM = "#59616e"
RED = "#f04452"
EDGE = "#292e38"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def shell(title: str, eyebrow: str, body: str, height: int = 220) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="{height}" viewBox="0 0 720 {height}" role="img" aria-labelledby="title desc">
<title id="title">{esc(title)}</title><desc id="desc">{esc(eyebrow)} — a profile card for Vaibhav Tripathi.</desc>
<defs><linearGradient id="wash" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#17121a"/><stop offset="1" stop-color="{BG}"/></linearGradient><linearGradient id="rule"><stop stop-color="{RED}" stop-opacity=".95"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></linearGradient></defs>
<style>
text{{font-family:{MONO}}}.enter{{opacity:0;animation:enter .75s cubic-bezier(.2,.7,.2,1) forwards}}.pulse{{transform-box:fill-box;transform-origin:center;animation:pulse 3.2s ease-in-out infinite}}.glint{{animation:glint 7s ease-in-out infinite}}@keyframes enter{{from{{opacity:0;transform:translateY(9px)}}to{{opacity:1;transform:translateY(0)}}}}@keyframes pulse{{0%,100%{{opacity:.55;transform:scale(.92)}}50%{{opacity:1;transform:scale(1.08)}}}}@keyframes glint{{0%,72%,100%{{opacity:.18}}76%{{opacity:.7}}80%{{opacity:.18}}}}@media(prefers-reduced-motion:reduce){{.enter,.pulse,.glint{{animation:none!important;opacity:1;transform:none}}}}
</style>
<rect x=".5" y=".5" width="719" height="{height-1}" rx="13" fill="url(#wash)" stroke="{EDGE}"/><path d="M14 1h120" stroke="url(#rule)" stroke-width="2"/>
<text x="24" y="32" fill="{RED}" font-size="11" letter-spacing="2.4">{esc(eyebrow.upper())}</text><text x="696" y="32" fill="{DIM}" font-size="10" text-anchor="end">INDEEDVAIBHAV / PROFILE</text>
{body}</svg>'''


def general_card(name: str, subtitle: str, items: list[tuple[str, str]], index: int) -> str:
    rows = []
    for i, (label, detail) in enumerate(items):
        y = 91 + i * 28
        rows.append(f'<g class="enter" style="animation-delay:{.12 + i*.09:.2f}s"><circle cx="31" cy="{y-4}" r="3" fill="{RED}"/><text x="46" y="{y}" fill="{TEXT}" font-size="14" font-weight="650">{esc(label)}</text><text x="696" y="{y}" fill="{MUTED}" font-size="11" text-anchor="end">{esc(detail)}</text></g>')
    body = f'<text class="enter" x="24" y="63" fill="{TEXT}" font-size="19" font-weight="700" style="animation-delay:.05s">{esc(name)}</text><text x="696" y="63" fill="{MUTED}" font-size="11" text-anchor="end">{esc(subtitle)}</text><line x1="24" y1="73" x2="696" y2="73" stroke="{EDGE}"/>' + ''.join(rows)
    return shell(name, f"0{index} / profile", body, 220)


def activity_card() -> str:
    total = int(DATA["total_contributions"])
    active = int(DATA["active_days"])
    streak = int(DATA["current_streak"])
    months = DATA.get("monthly", [])[-12:]
    max_month = max((int(m["total"]) for m in months), default=1) or 1
    bars = []
    for i, month in enumerate(months):
        x = 35 + i * 54
        val = int(month["total"])
        bar_h = max(3, round(58 * val / max_month))
        bars.append(f'<g class="enter" style="animation-delay:{.1+i*.045:.2f}s"><rect x="{x}" y="{151-bar_h}" width="24" height="{bar_h}" rx="3" fill="{RED}" opacity="{.38 + .62*val/max_month:.2f}"/><text x="{x+12}" y="171" fill="{DIM}" font-size="8" text-anchor="middle">{esc(month["month"][5:])}</text></g>')
    body = f'''<g class="enter" style="animation-delay:.08s"><text x="26" y="91" fill="{TEXT}" font-size="29" font-weight="700">{total:,}</text><text x="26" y="110" fill="{MUTED}" font-size="10">CONTRIBUTIONS / 12 MONTHS</text><text x="264" y="91" fill="{TEXT}" font-size="29" font-weight="700">{active}</text><text x="264" y="110" fill="{MUTED}" font-size="10">ACTIVE DAYS</text><text x="454" y="91" fill="{RED}" font-size="29" font-weight="700">{streak}</text><text x="454" y="110" fill="{MUTED}" font-size="10">CURRENT STREAK / DAYS</text></g>
<text x="26" y="136" fill="{MUTED}" font-size="9" letter-spacing="1.4">MONTHLY CONTRIBUTIONS · REPOSITORY DATA</text>{''.join(bars)}<text x="694" y="201" fill="{DIM}" font-size="9" text-anchor="end">UPDATED {esc(DATA.get('generated_at','')[:10])}</text>'''
    return shell("Activity", "04 / telemetry", body, 220)


def focus_areas_card() -> str:
    width, height = 1080, 282
    groups = [
        ("01", "BUILD", "Java + DSA", "Spring Boot + REST APIs", "Backend engineering", "React + Next.js"),
        ("02", "SYSTEMS", "Service + API design", "PostgreSQL + JPA", "Relational data modeling", "Maps + dashboards"),
        ("03", "INTELLIGENCE", "Machine learning", "LLM-powered applications", "RAG concepts", "Civic decision support"),
    ]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Build, Systems, and Intelligence</title><desc id="desc">Three readable profile focus panels for Java and backend engineering, data systems, and applied AI.</desc>',
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#17131a"/><stop offset="1" stop-color="#0b0d12"/></linearGradient><linearGradient id="line"><stop stop-color="#f04452"/><stop offset="1" stop-color="#f04452" stop-opacity="0"/></linearGradient></defs>',
        f'<style>text{{font-family:{MONO}}}.panel{{opacity:0;animation:up .65s ease-out forwards}}@keyframes up{{from{{opacity:0;transform:translateY(9px)}}to{{opacity:1;transform:translateY(0)}}}}@media(prefers-reduced-motion:reduce){{.panel{{animation:none;opacity:1;transform:none}}}}</style>',
        f'<rect x=".5" y=".5" width="1079" height="281" rx="14" fill="url(#bg)" stroke="{EDGE}"/><path d="M18 1h210" stroke="url(#line)" stroke-width="2"/>',
        f'<text x="26" y="35" fill="{RED}" font-size="11" letter-spacing="2.5">PROFILE / ENGINEERING FOCUS</text><text x="1054" y="35" fill="{DIM}" font-size="10" text-anchor="end">BUILD → SYSTEMS → INTELLIGENCE</text>',
    ]
    for index, (number, name, *items) in enumerate(groups):
        x = 20 + index * 352
        delay = .08 + index * .13
        parts.append(f'<g class="panel" style="animation-delay:{delay:.2f}s"><rect x="{x}" y="55" width="332" height="207" rx="11" fill="{PANEL}" stroke="{EDGE}"/><text x="{x+18}" y="84" fill="{RED}" font-size="10" letter-spacing="1.4">{number} / FOCUS</text><text x="{x+18}" y="112" fill="{TEXT}" font-size="20" font-weight="700">{esc(name)}</text><line x1="{x+18}" y1="126" x2="{x+314}" y2="126" stroke="{EDGE}"/>')
        for row, item in enumerate(items):
            y = 153 + row * 25
            parts.append(f'<circle cx="{x+22}" cy="{y-4}" r="2.5" fill="{RED}"/><text x="{x+33}" y="{y}" fill="{MUTED}" font-size="13">{esc(item)}</text>')
        parts.append('</g>')
    parts.append('</svg>')
    return ''.join(parts)


def toolchain_card() -> str:
    width, height = 1080, 374
    modules = [
        (24, 70, 326, "01", "LANGUAGES", "Java · Python", "JavaScript · TypeScript", "DSA / problem solving"),
        (377, 70, 326, "02", "PRODUCT UI", "React · Next.js", "Vite · Tailwind CSS", "Interfaces / web apps"),
        (730, 70, 326, "03", "SERVICES", "Spring Boot · Node.js", "Express · FastAPI", "REST APIs / backend"),
        (24, 218, 510, "04", "DATA + PERSISTENCE", "PostgreSQL · MySQL · SQL", "JPA / Hibernate", "Relational modeling"),
        (546, 218, 510, "05", "APPLIED INTELLIGENCE", "Machine learning · LLM APIs", "RAG concepts · maps · Leaflet", "Geospatial / data-led tools"),
    ]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Engineering Toolchain</title><desc id="desc">A connected map of Vaibhav Tripathi’s languages, product UI, backend services, data systems, and applied intelligence technologies.</desc>',
        f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#17131a"/><stop offset="1" stop-color="{BG}"/></linearGradient><linearGradient id="wire"><stop stop-color="{RED}" stop-opacity=".8"/><stop offset="1" stop-color="#58a6ff" stop-opacity=".55"/></linearGradient></defs>',
        f'<style>text{{font-family:{MONO}}}.mod{{opacity:0;animation:up .55s ease-out forwards}}.trace{{stroke-dasharray:7 8;animation:flow 8s linear infinite}}@keyframes up{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:translateY(0)}}}}@keyframes flow{{to{{stroke-dashoffset:-120}}}}@media(prefers-reduced-motion:reduce){{.mod{{animation:none;opacity:1;transform:none}}.trace{{animation:none}}}}</style>',
        f'<rect x=".5" y=".5" width="1079" height="373" rx="14" fill="url(#bg)" stroke="{EDGE}"/><path d="M18 1h210" stroke="{RED}" stroke-width="2"/>',
        f'<text x="26" y="35" fill="{RED}" font-size="11" letter-spacing="2.5">TOOLCHAIN / SYSTEM MAP</text><text x="1054" y="35" fill="{DIM}" font-size="10" text-anchor="end">CODE → PRODUCT → DECISIONS</text>',
        f'<path class="trace" d="M350 133h27m326 0h27M187 194v11q0 14 14 14h78M893 194v11q0 14-14 14h-78M534 280h12" fill="none" stroke="url(#wire)" stroke-width="1.5"/>',
    ]
    for index, (x, y, w, number, label, line1, line2, caption) in enumerate(modules):
        delay = .08 + index * .08
        parts.append(f'<g class="mod" style="animation-delay:{delay:.2f}s"><rect x="{x}" y="{y}" width="{w}" height="124" rx="10" fill="{PANEL}" stroke="{EDGE}"/><text x="{x+17}" y="{y+25}" fill="{RED}" font-size="10" letter-spacing="1.2">{number} / {esc(label)}</text><text x="{x+17}" y="{y+56}" fill="{TEXT}" font-size="14" font-weight="650">{esc(line1)}</text><text x="{x+17}" y="{y+79}" fill="{TEXT}" font-size="14" font-weight="650">{esc(line2)}</text><text x="{x+17}" y="{y+105}" fill="{MUTED}" font-size="10">{esc(caption)}</text><circle cx="{x+w-17}" cy="{y+23}" r="3" fill="{RED}"/></g>')
    parts.append(f'<text x="26" y="362" fill="{DIM}" font-size="9" letter-spacing="1.4">FOUNDATIONS IN JAVA + DSA · BUILT THROUGH BACKEND, WEB, DATA, AND APPLIED AI</text><text x="1054" y="362" fill="{DIM}" font-size="9" text-anchor="end">CURRENT STACK / CURATED</text></svg>')
    return ''.join(parts)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    cards = {
        "focus-areas.svg": focus_areas_card(),
        "activity.svg": activity_card(),
        "toolchain.svg": toolchain_card(),
    }
    for filename, svg in cards.items():
        (OUT / filename).write_text(svg + "\n", encoding="utf-8")
    print(f"Rendered {len(cards)} profile SVG cards to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
