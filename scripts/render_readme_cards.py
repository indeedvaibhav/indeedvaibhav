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


def project_card(name: str, mark: str, summary: str, stack: str, link: str, index: int) -> str:
    body = f'''<g class="enter" style="animation-delay:.12s"><circle class="pulse" cx="672" cy="61" r="4" fill="{RED}"/><text x="24" y="87" fill="{TEXT}" font-size="22" font-weight="700">{esc(mark)}  {esc(name)}</text><line x1="24" y1="101" x2="696" y2="101" stroke="{EDGE}"/><text x="24" y="130" fill="{MUTED}" font-size="12">{esc(summary)}</text><text x="24" y="160" fill="{TEXT}" font-size="10">{esc(stack)}</text><text x="24" y="193" fill="{RED}" font-size="10">OPEN PROJECT  ↗</text><text x="696" y="193" fill="{DIM}" font-size="9" text-anchor="end">{esc(link)}</text></g>'''
    return shell(name, f"0{index} / field system", body, 220)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    cards = {
        "build.svg": general_card("BUILD", "Java → shipped software", [("Java + Data Structures & Algorithms", "CORE PRACTICE"), ("Spring Boot + REST APIs", "BACKEND"), ("Backend engineering + data modeling", "SYSTEMS"), ("React + Next.js", "PRODUCT UI")], 1),
        "systems.svg": general_card("SYSTEMS", "Make the boundaries clear", [("Spring Boot · PostgreSQL · JPA/Hibernate", "SERVICES"), ("REST APIs · Node.js · Express", "INTEGRATION"), ("Relational modeling · persistence", "DATA"), ("Geospatial maps · operational dashboards", "CONTEXT")], 2),
        "intelligence.svg": general_card("INTELLIGENCE", "AI that can explain its work", [("Machine learning + AI-powered applications", "EXPLORING"), ("LLM APIs · retrieval-augmented generation", "RETRIEVAL"), ("Civic workflows · location-aware decisions", "CIVIC TECH"), ("Human-readable operator reasoning", "APPLIED AI")], 3),
        "activity.svg": activity_card(),
        "railsage-ai.svg": project_card("RailSage AI", "↗", "Railway operations dashboard with live maps and AI reasoning.", "React 19 · Vite · Express · Leaflet · Claude API", "FAR AWAY HACKATHON 2026", 5),
        "civicsentinel.svg": project_card("CivicSentinel", "⌖", "Civic intelligence for complaints and administrative workflows.", "AI-assisted classification · RAG concepts · Geospatial data", "CITIZEN + ADMIN WORKFLOWS", 6),
        "bloodflow.svg": project_card("BloodFlow", "+", "Healthcare backend coordinating donors, hospitals, and requests.", "Spring Boot · PostgreSQL · JPA/Hibernate", "RELATIONAL DOMAIN MODEL", 7),
    }
    for filename, svg in cards.items():
        (OUT / filename).write_text(svg + "\n", encoding="utf-8")
    print(f"Rendered {len(cards)} animated SVG cards to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
