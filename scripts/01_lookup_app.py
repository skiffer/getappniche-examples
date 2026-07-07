#!/usr/bin/env python3
"""Look up one iOS app's estimated revenue and downloads by App Store id.

Usage:
    export GETAPPNICHE_API_KEY="getappniche_..."
    python 01_lookup_app.py 284882215

Uses GET /api/v1/apps/{app_id} (1 credit). App ids use the "{store}:{store_id}"
format, e.g. "apple:284882215". GetAppNiche covers the Apple App Store only.

Revenue/download figures are ESTIMATES — a transparent heuristic based on
review/rating velocity and store signals. Treat them as directional ranges.

Docs: https://getappniche.com/docs/api-quickstart
"""

import os
import sys

import requests

BASE_URL = "https://api.getappniche.com/api/v1"


def get_api_key() -> str:
    key = os.environ.get("GETAPPNICHE_API_KEY", "")
    if not key:
        sys.exit(
            "Set GETAPPNICHE_API_KEY first (create a key at "
            "https://app.getappniche.com/settings/api-keys)"
        )
    return key


def explain_error(resp: requests.Response) -> str:
    """Map GetAppNiche API error codes to actionable messages."""
    fixes = {
        401: "Invalid or missing API key. Check the Authorization header and that "
             "the full key (starting 'getappniche_') was pasted.",
        402: "Out of credits, or your plan doesn't include API access. Check your "
             "balance at https://app.getappniche.com/settings",
        404: "App not found. app_id must be '{store}:{store_id}', e.g. 'apple:284882215'.",
        422: "Invalid parameters — check names/values against the docs.",
        429: "Rate limited (60 requests/minute per key). Retry after "
             f"{resp.headers.get('Retry-After', '?')} seconds.",
    }
    return fixes.get(resp.status_code, f"Unexpected HTTP {resp.status_code}: {resp.text[:200]}")


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: python 01_lookup_app.py <apple_store_id>   e.g. 284882215")
    store_id = sys.argv[1].strip()
    app_id = f"apple:{store_id}"

    resp = requests.get(
        f"{BASE_URL}/apps/{app_id}",
        headers={"Authorization": f"Bearer {get_api_key()}"},
        timeout=30,
    )
    if resp.status_code != 200:
        sys.exit(f"[{resp.status_code}] {explain_error(resp)}")

    app = resp.json()

    print(f"\n{app.get('title', app_id)}")
    print("-" * 48)
    # Field names as returned by the API; unknown/missing fields print as n/a.
    rows = [
        ("Est. monthly revenue", app.get("revenue_est_monthly")),
        ("Est. monthly downloads", app.get("downloads_est_monthly")),
        ("Rating", app.get("rating")),
        ("Reviews", app.get("review_count")),
        ("Category", app.get("category")),
        ("Price model", app.get("price_model")),
    ]
    for label, value in rows:
        print(f"{label:<24} {value if value is not None else 'n/a'}")

    print("-" * 48)
    print(f"credits_charged: {app.get('credits_charged', '?')}")
    print("Note: revenue/downloads are estimates (directional ranges), not accounting data.")


if __name__ == "__main__":
    main()
