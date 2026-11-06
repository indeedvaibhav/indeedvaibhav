#!/usr/bin/env python3
"""Fetch the public contribution calendar and write normalized yearly data."""
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
USERNAME = "indeedvaibhav"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUTPUT = ROOT / "data" / "contributions.json"


def fetch_days() -> list[dict]:
    response = requests.get(
        URL,
        headers={"User-Agent": "indeedvaibhav-profile-art/1.0"},
        timeout=30,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    cells = soup.select("td.ContributionCalendar-day[data-date]")
    if not cells:
        cells = soup.select("[data-date][data-level]")
    if not cells:
        raise RuntimeError("GitHub contribution calendar markup was not found.")

    days = []
    for cell in cells:
        date = cell.get("data-date")
        if not date:
            continue
        cell_id = cell.get("id")
        tooltip = soup.find("tool-tip", attrs={"for": cell_id}) if cell_id else None
        text = tooltip.get_text(" ", strip=True) if tooltip else ""
        if re.search(r"no contributions", text, re.I):
            count = 0
        else:
            match = re.search(r"([\d,]+)\s+contributions?", text, re.I)
            if not match:
                raise RuntimeError(f"Could not read contribution count for {date}.")
            count = int(match.group(1).replace(",", ""))
        days.append({"date": date, "count": count})

    days.sort(key=lambda item: item["date"])
    if len(days) < 350:
        raise RuntimeError(f"Expected a full contribution year, got {len(days)} days.")
    return days


def longest_streak(days: list[dict]) -> int:
    best = run = 0
    previous = None
    for item in days:
        date = dt.date.fromisoformat(item["date"])
        if item["count"] and (previous is None or (date - previous).days == 1):
            run += 1
            best = max(best, run)
        else:
            run = 1 if item["count"] else 0
        previous = date
    return best


def build_data(days: list[dict]) -> dict:
    today = dt.date.today().isoformat()
    total = sum(item["count"] for item in days)
    active = sum(item["count"] > 0 for item in days)
    best_day = max(days, key=lambda item: item["count"])
    streak_days = days[:]
    if streak_days and streak_days[-1]["date"] == today and streak_days[-1]["count"] == 0:
        streak_days = streak_days[:-1]
    current = 0
    for item in reversed(streak_days):
        if item["count"] <= 0:
            break
        current += 1

    monthly: dict[str, int] = {}
    for item in days:
        month = item["date"][:7]
        monthly[month] = monthly.get(month, 0) + item["count"]

    return {
        "username": USERNAME,
        "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "total_contributions": total,
        "active_days": active,
        "current_streak": current,
        "longest_streak": longest_streak(days),
        "best_day": best_day,
        "monthly": [{"month": key, "total": value} for key, value in sorted(monthly.items())],
        "days": days,
    }


if __name__ == "__main__":
    data = build_data(fetch_days())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {OUTPUT.name}: {data['total_contributions']:,} contributions")

