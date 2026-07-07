#!/usr/bin/env python3
"""Compare two competing apps side by side, then score the keywords you both fight over.

Usage:
    export GETAPPNICHE_API_KEY="getappniche_..."
    python 04_competitor_compare.py 1052240851 1179624268 "habit tracker" "daily habits"
    #                                ^ app A      ^ app B    ^ shared candidate keywords

NOTE ON SCOPE: the public REST API documents app detail records and per-keyword
difficulty scoring, but NOT a per-app keyword list or keyword-gap endpoint — so a
true "keywords app B ranks for that app A doesn't" diff isn't possible from the
API alone. This example does the documented version: a head-to-head snapshot from
GET /api/v1/apps/{app_id} (1 credit each) plus scoring of a shared candidate
keyword list via GET /api/v1/keywords/difficulty (10 credits each). Full
competitor keyword-gap analysis is available in the GetAppNiche web app:
https://getappniche.com/docs/aso-keywords

Docs: https://getappniche.com/docs/api-quickstart
"""

import os
import sys
import time

import requests

BASE_URL = "https://api.getappniche.com/api/v1"

ERROR_FIXES = {
    401: "Invalid API key — check the Authorization: Bearer header.",
    402: "Out of credits / no API access — https://app.getappniche.com/settings",
    404: "App not found — app_id must be '{store}:{store_id}', e.g. 'apple:284882215'.",
    422: "Invalid parameters — check values against the docs.",
    429: "Rate limited (60 req/min) — respect the Retry-After header.",
}


def get_session() -> requests.Session:
    key = os.environ.get("GETAPPNICHE_API_KEY", "")
    if not key:
        sys.exit(
            "Set GETAPPNICHE_API_KEY first (create a key at "
            "https://app.getappniche.com/settings/api-keys)"
        )
    session = requests.Session()
    session.headers["Authorization"] = f"Bearer {key}"
    return session


def get_json(session: requests.Session, url: str, params: dict | None = None) -> dict:
    resp = session.get(url, params=params, timeout=30)
    if resp.status_code != 200:
        fix = ERROR_FIXES.get(resp.status_code, resp.text[:200])
        sys.exit(f"[{resp.status_code}] {url.rsplit('/', 1)[-1]}: {fix}")
    return resp.json()


def field(app: dict, *names):
    for name in names:
        if app.get(name) is not None:
            return app[name]
    return "n/a"


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit(
            "Usage: python 04_competitor_compare.py <store_id_a> <store_id_b> "
            "[keyword ...]"
        )
    id_a, id_b = sys.argv[1], sys.argv[2]
    keywords = [k.strip() for k in sys.argv[3:] if k.strip()]

    session = get_session()
    app_a = get_json(session, f"{BASE_URL}/apps/apple:{id_a}")
    app_b = get_json(session, f"{BASE_URL}/apps/apple:{id_b}")

    name_a = str(field(app_a, "title"))[:22]
    name_b = str(field(app_b, "title"))[:22]

    print(f"\n{'':<26} {name_a:>22}   {name_b:>22}")
    print("-" * 76)
    for label, keys in [
        ("Est. monthly revenue", ("revenue_est_monthly",)),
        ("Est. monthly downloads", ("downloads_est_monthly",)),
        ("Rating", ("rating",)),
        ("Reviews", ("review_count",)),
        ("Category", ("category",)),
        ("Price model", ("price_model",)),
    ]:
        print(f"{label:<26} {field(app_a, *keys)!s:>22}   {field(app_b, *keys)!s:>22}")
    print("-" * 76)
    print("Revenue/download figures are estimates (directional ranges), not accounting data.")

    if not keywords:
        print("\nTip: pass shared keywords to score the terms you both compete on, e.g.")
        print(f'  python 04_competitor_compare.py {id_a} {id_b} "habit tracker" "streaks"')
        return

    print(f"\nScoring {len(keywords)} shared keywords (10 credits each) ...\n")
    print(f"{'KEYWORD':<24} {'DIFFICULTY':>10} {'OPPORTUNITY':>11}")
    print("-" * 48)
    for keyword in keywords:
        data = get_json(
            session,
            f"{BASE_URL}/keywords/difficulty",
            params={"keyword": keyword, "store": "apple", "country": "US", "language": "en"},
        )
        diff = field(data, "difficulty", "difficulty_score")
        opp = field(data, "opportunity", "opportunity_score")
        print(f"{keyword:<24} {diff!s:>10} {opp!s:>11}")
        time.sleep(1.1)  # stay under 60 requests/minute

    print("-" * 48)
    print("Low difficulty + high opportunity = terms where the smaller app can still win.")


if __name__ == "__main__":
    main()
