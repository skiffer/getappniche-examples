#!/usr/bin/env python3
"""Score a list of ASO keywords and print an opportunity table.

Usage:
    export GETAPPNICHE_API_KEY="getappniche_..."
    python 03_keyword_scores.py "habit tracker" "sleep sounds" "budget planner"
    python 03_keyword_scores.py            # uses a demo keyword list

Uses GET /api/v1/keywords/difficulty (10 credits PER KEYWORD — a 10-keyword run
costs 100 of your 5,000 monthly credits). Stays politely under the 60 req/min
rate limit and honors Retry-After on 429.

Docs: https://getappniche.com/docs/api-quickstart
"""

import os
import sys
import time

import requests

BASE_URL = "https://api.getappniche.com/api/v1"
COUNTRY = "US"
LANGUAGE = "en"

DEMO_KEYWORDS = [
    "habit tracker",
    "sleep sounds",
    "budget planner",
    "interval timer",
    "plant identifier",
]


def get_api_key() -> str:
    key = os.environ.get("GETAPPNICHE_API_KEY", "")
    if not key:
        sys.exit(
            "Set GETAPPNICHE_API_KEY first (create a key at "
            "https://app.getappniche.com/settings/api-keys)"
        )
    return key


def score_keyword(session: requests.Session, keyword: str) -> dict:
    """One call = 10 credits. Retries once on 429 using Retry-After."""
    for attempt in (1, 2):
        resp = session.get(
            f"{BASE_URL}/keywords/difficulty",
            params={
                "keyword": keyword,
                "store": "apple",
                "country": COUNTRY,
                "language": LANGUAGE,
            },
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 429 and attempt == 1:
            wait = int(resp.headers.get("Retry-After", "10"))
            print(f"  429 rate limited — sleeping {wait}s ...", file=sys.stderr)
            time.sleep(wait)
            continue
        if resp.status_code == 401:
            sys.exit("401: invalid API key — check the Authorization: Bearer header.")
        if resp.status_code == 402:
            sys.exit(
                "402: out of credits or no API access — check "
                "https://app.getappniche.com/settings (keyword scoring costs 10 credits each)."
            )
        sys.exit(f"HTTP {resp.status_code} for '{keyword}': {resp.text[:200]}")
    raise RuntimeError("unreachable")


def pick(data: dict, *names):
    """Return the first present field from `names` (API field-name tolerant)."""
    for name in names:
        if data.get(name) is not None:
            return data[name]
    return "n/a"


def main() -> None:
    keywords = [k.strip() for k in sys.argv[1:] if k.strip()] or DEMO_KEYWORDS
    cost = len(keywords) * 10
    print(f"Scoring {len(keywords)} keywords ({cost} credits total, 10 per keyword)\n")

    session = requests.Session()
    session.headers["Authorization"] = f"Bearer {get_api_key()}"

    rows = []
    credits_spent = 0
    for keyword in keywords:
        data = score_keyword(session, keyword)
        credits_spent += int(data.get("credits_charged", 10))
        rows.append(
            (
                keyword,
                pick(data, "difficulty", "difficulty_score"),
                pick(data, "popularity", "popularity_score"),
                pick(data, "opportunity", "opportunity_score"),
            )
        )
        time.sleep(1.1)  # stay well under 60 requests/minute

    print(f"{'KEYWORD':<24} {'DIFFICULTY':>10} {'POPULARITY':>10} {'OPPORTUNITY':>11}")
    print("-" * 60)
    # Highest opportunity first (unscored rows sink to the bottom).
    def sort_key(row):
        return row[3] if isinstance(row[3], (int, float)) else -1

    for keyword, diff, pop, opp in sorted(rows, key=sort_key, reverse=True):
        print(f"{keyword:<24} {diff!s:>10} {pop!s:>10} {opp!s:>11}")

    print("-" * 60)
    print(f"credits_charged total: {credits_spent}")
    print("Rule of thumb: high opportunity + low difficulty = keywords worth targeting.")


if __name__ == "__main__":
    main()
