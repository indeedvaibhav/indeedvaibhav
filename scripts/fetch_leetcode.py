#!/usr/bin/env python3
"""Refresh public LeetCode solved totals and earned badges.

LeetCode does not publish a stable documented public API. If its profile
endpoint is unavailable or changes shape, keep the last good snapshot so the
other profile art can still refresh.
"""
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests

ROOT = Path(__file__).resolve().parents[1]
USERNAME = "Indeedvaibhav"
GRAPHQL = "https://leetcode.com/graphql/"
OUTPUT = ROOT / "data" / "leetcode.json"
BADGE_DIR = ROOT / "assets" / "leetcode-badges"
QUERY = """
query profileStats($username: String!) {
  matchedUser(username: $username) {
    username
    submitStats {
      acSubmissionNum {
        difficulty
        count
        submissions
      }
    }
    badges {
      id
      displayName
      icon
      creationDate
    }
  }
}
"""


def badge_asset(icon: str, badge_id: str) -> tuple[str, Path]:
    url = urljoin("https://leetcode.com", icon)
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in {"assets.leetcode.com", "leetcode.com"}:
        raise ValueError(f"Unexpected badge icon host: {parsed.hostname}")
    if not parsed.path.startswith("/static_assets/"):
        raise ValueError("Unexpected badge icon path.")
    extension = Path(parsed.path).suffix.lower()
    if extension not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise ValueError(f"Unsupported badge icon format: {extension}")
    safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", badge_id)
    filename = f"{safe_id}{extension}"
    return url, BADGE_DIR / filename


def fetch_profile() -> dict:
    response = requests.post(
        GRAPHQL,
        json={"query": QUERY, "variables": {"username": USERNAME}},
        headers={
            "User-Agent": "indeedvaibhav-profile-art/1.0",
            "Referer": f"https://leetcode.com/u/{USERNAME}/",
            "Origin": "https://leetcode.com",
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("errors"):
        raise RuntimeError("LeetCode returned a GraphQL error.")
    user = (payload.get("data") or {}).get("matchedUser")
    if not user or user.get("username", "").lower() != USERNAME.lower():
        raise RuntimeError("LeetCode did not return the requested public profile.")

    raw_counts = {
        entry["difficulty"].lower(): int(entry["count"])
        for entry in user["submitStats"]["acSubmissionNum"]
    }
    if not {"all", "easy", "medium", "hard"}.issubset(raw_counts):
        raise RuntimeError("LeetCode's solved-count response is incomplete.")

    badges = []
    for badge in user.get("badges", []):
        badge_id = str(badge.get("id", "")).strip()
        icon = str(badge.get("icon", "")).strip()
        if not badge_id or not icon:
            continue
        icon_url, icon_path = badge_asset(icon, badge_id)
        if not icon_path.is_file():
            icon_response = requests.get(
                icon_url,
                headers={"User-Agent": "indeedvaibhav-profile-art/1.0"},
                timeout=30,
            )
            icon_response.raise_for_status()
            content_type = icon_response.headers.get("Content-Type", "").lower()
            if not content_type.startswith("image/") or len(icon_response.content) > 2_000_000:
                raise RuntimeError(f"Invalid image returned for LeetCode badge {badge_id}.")
            icon_path.parent.mkdir(parents=True, exist_ok=True)
            icon_path.write_bytes(icon_response.content)
        badges.append(
            {
                "id": badge_id,
                "name": str(badge.get("displayName") or "LeetCode Badge"),
                "earned_at": str(badge.get("creationDate") or ""),
                "icon_file": icon_path.name,
            }
        )

    return {
        "username": USERNAME,
        "fetched_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "solved": {
            "all": raw_counts["all"],
            "easy": raw_counts["easy"],
            "medium": raw_counts["medium"],
            "hard": raw_counts["hard"],
        },
        "badges": badges,
    }


if __name__ == "__main__":
    try:
        snapshot = fetch_profile()
    except (requests.RequestException, ValueError, KeyError, TypeError, RuntimeError) as error:
        print(f"LeetCode refresh skipped; keeping the last good snapshot: {error}")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
        print(
            f"Updated {OUTPUT.name}: {snapshot['solved']['all']} solved, "
            f"{len(snapshot['badges'])} badges"
        )
