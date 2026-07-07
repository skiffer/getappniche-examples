#!/usr/bin/env python3
"""Mini niche scan: search a niche, pull estimates, count who clears $1k/mo.

Usage:
    export GETAPPNICHE_API_KEY="getappniche_..."
    python 05_niche_scan.py "habit tracker"
    python 05_niche_scan.py "plant identifier" --bar 2000

Uses GET /api/v1/apps (1 credit): search the niche, take the top results, and
answer the only question that matters before you build — how many apps in this
niche actually clear an estimated $1,000/month?

All figures are ESTIMATES from a transparent review/rating-velocity heuristic —
directional ranges, not accounting data. Full methodology:
https://getappniche.com/docs/explore-and-analytics

Docs: https://getappniche.com/docs/api-quickstart
"""

import argparse
import os
import sys

import requests

BASE_URL = "https://api.getappniche.com/api/v1"

ERROR_FIXES = {
    401: "Invalid API key — check the Authorization: Bearer header.",
    402: "Out of credits / no API access — https://app.getappniche.com/settings",
    422: "Invalid parameters — check values (limit max is 100).",
    429: "Rate limited (60 req/min) — respect the Retry-After header.",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Mini niche scan via the GetAppNiche API")
    parser.add_argument("query", help='niche search query, e.g. "habit tracker"')
    parser.add_argument("--bar", type=int, default=1000,
                        help="est. monthly revenue bar in USD (default: 1000)")
    parser.add_argument("--limit", type=int, default=50,
                        help="how many top results to scan, max 100 (default: 50)")
    args = parser.parse_args()

    api_key = os.environ.get("GETAPPNICHE_API_KEY", "")
    if not api_key:
        sys.exit(
            "Set GETAPPNICHE_API_KEY first (create a key at "
            "https://app.getappniche.com/settings/api-keys)"
        )

    resp = requests.get(
        f"{BASE_URL}/apps",
        headers={"Authorization": f"Bearer {api_key}"},
        params={"search": args.query, "limit": min(args.limit, 100)},
        timeout=30,
    )
    if resp.status_code != 200:
        sys.exit(f"[{resp.status_code}] {ERROR_FIXES.get(resp.status_code, resp.text[:200])}")

    data = resp.json()
    apps = data.get("items", [])
    if not apps:
        sys.exit(f'No results for "{args.query}" — try a broader query.')

    def revenue(app: dict) -> float:
        value = app.get("revenue_est_monthly")
        return float(value) if isinstance(value, (int, float)) else 0.0

    apps.sort(key=revenue, reverse=True)
    winners = [a for a in apps if revenue(a) >= args.bar]

    print(f'\nNiche scan: "{args.query}" — top {len(apps)} results\n')
    print(f"{'#':>3}  {'APP':<34} {'EST. REVENUE/MO':>16}")
    print("-" * 58)
    for i, app in enumerate(apps[:15], 1):
        marker = "*" if revenue(app) >= args.bar else " "
        title = str(app.get("title", "?"))[:34]
        print(f"{i:>3}{marker} {title:<34} {'$' + format(int(revenue(app)), ','):>16}")
    if len(apps) > 15:
        print(f"     ... and {len(apps) - 15} more")
    print("-" * 58)

    share = 100 * len(winners) / len(apps)
    print(f"\n=> {len(winners)} of {len(apps)} apps ({share:.0f}%) clear an est. "
          f"${args.bar:,}/month (* marked)")
    print(f"credits_charged: {data.get('credits_charged', '?')}")
    print("\nEstimates are directional ranges (review/rating-velocity heuristic), "
          "not accounting data.")
    print("Store-wide context: only ~3.2% of all iOS apps clear an est. $1k/mo — "
          "see https://getappniche.com/answers/how-many-apps-make-money")


if __name__ == "__main__":
    main()
