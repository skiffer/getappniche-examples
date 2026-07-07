#!/usr/bin/env bash
#
# Top 10 apps in a category by estimated monthly revenue — curl + jq only.
#
# Usage:
#   export GETAPPNICHE_API_KEY="getappniche_..."
#   ./02_top_categories.sh "Health & Fitness" [min_revenue]
#
# Uses GET /api/v1/apps (1 credit per call). Category names match what you see
# in the GetAppNiche Explore view. Revenue figures are ESTIMATES (directional
# ranges from a transparent review/rating-velocity heuristic).
#
# Docs: https://getappniche.com/docs/api-quickstart
set -euo pipefail

CATEGORY="${1:-Health & Fitness}"
MIN_REVENUE="${2:-1000}"

if [[ -z "${GETAPPNICHE_API_KEY:-}" ]]; then
  echo "Set GETAPPNICHE_API_KEY first: https://app.getappniche.com/settings/api-keys" >&2
  exit 1
fi
command -v jq >/dev/null || { echo "This example needs jq (brew install jq)" >&2; exit 1; }

# -G turns --data-urlencode pairs into query parameters. limit max is 100.
response="$(curl -sS -G "https://api.getappniche.com/api/v1/apps" \
  -H "Authorization: Bearer ${GETAPPNICHE_API_KEY}" \
  --data-urlencode "category=${CATEGORY}" \
  --data-urlencode "min_revenue=${MIN_REVENUE}" \
  --data-urlencode "limit=100" \
  -w '\n%{http_code}')"

status="$(tail -n1 <<<"$response")"
body="$(sed '$d' <<<"$response")"

case "$status" in
  200) ;;
  401) echo "401: invalid API key — check the Bearer header." >&2; exit 1 ;;
  402) echo "402: out of credits or no API access — https://app.getappniche.com/settings" >&2; exit 1 ;;
  422) echo "422: invalid parameters — check category/min_revenue values." >&2; exit 1 ;;
  429) echo "429: rate limited (60 req/min) — respect Retry-After and retry." >&2; exit 1 ;;
  *)   echo "HTTP ${status}: ${body:0:200}" >&2; exit 1 ;;
esac

echo
echo "Top 10 \"${CATEGORY}\" apps by est. monthly revenue (min \$${MIN_REVENUE}/mo):"
echo

jq -r '
  .items
  | sort_by(.revenue_est_monthly // 0) | reverse | .[:10]
  | to_entries[]
  | "\(.key + 1)\t\(.value.title)\t$\(.value.revenue_est_monthly // 0)/mo (est.)"
' <<<"$body" | column -t -s $'\t'

echo
jq -r '"credits_charged: \(.credits_charged // "?")  |  figures are estimates, not accounting data"' <<<"$body"
