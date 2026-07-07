# GetAppNiche Examples — App Store Data API & MCP Examples

Working examples for the [GetAppNiche](https://getappniche.com) **App Store data API** and
**App Store MCP server**: pull iOS app revenue and download estimates, ASO keyword difficulty
scores, and enriched reviews into your own scripts, spreadsheets, automations — or straight
into an AI assistant like Claude or Cursor via MCP.

- **REST API base:** `https://api.getappniche.com/api/v1/*`
- **MCP server:** `https://api.getappniche.com/mcp` (JSON-RPC 2.0 over Streamable HTTP)
- **Auth:** `Authorization: Bearer YOUR_API_KEY` on every request

## What is GetAppNiche?

GetAppNiche is an app market research tool for the **Apple App Store (iOS) — 745,000+ apps
tracked**. Google Play is not covered. Revenue and download figures are **estimates**: a
transparent heuristic based on observed review/rating velocity and store signals. The inputs
are shown to you, and estimates are directional ranges — treat them as "which of these apps
is in the $1k/mo club", not as accounting data.

## Quick start

1. Create an account and an API key at
   [app.getappniche.com/settings/api-keys](https://app.getappniche.com/settings/api-keys)
   (keys look like `getappniche_...` and can be rotated or revoked anytime).
2. Export it:

   ```bash
   export GETAPPNICHE_API_KEY="getappniche_..."
   ```

3. Run any example:

   ```bash
   pip install requests
   python scripts/01_lookup_app.py 284882215        # Facebook's store id, as an example
   ./scripts/02_top_categories.sh "Health & Fitness"
   ```

## Examples

| Example | What it shows | Endpoints / tools used |
| --- | --- | --- |
| [`mcp/claude-code.md`](mcp/claude-code.md) | Connect Claude Code to live App Store data in one command | MCP: all 7 tools |
| [`mcp/claude-desktop.json`](mcp/claude-desktop.json) | Claude Desktop config (via `mcp-remote`) | MCP |
| [`mcp/cursor.json`](mcp/cursor.json) | Cursor `.cursor/mcp.json` config | MCP |
| [`scripts/01_lookup_app.py`](scripts/01_lookup_app.py) | Look up one app's estimated revenue/downloads by store id, with real error handling | `GET /api/v1/apps/{app_id}` |
| [`scripts/02_top_categories.sh`](scripts/02_top_categories.sh) | curl + jq: top 10 apps in a category by estimated monthly revenue | `GET /api/v1/apps` |
| [`scripts/03_keyword_scores.py`](scripts/03_keyword_scores.py) | Score a list of ASO keywords and print an opportunity table | `GET /api/v1/keywords/difficulty` |
| [`scripts/04_competitor_compare.py`](scripts/04_competitor_compare.py) | Side-by-side competitor snapshot + score the keywords you both compete on | `GET /api/v1/apps/{app_id}`, `GET /api/v1/keywords/difficulty` |
| [`scripts/05_niche_scan.py`](scripts/05_niche_scan.py) | Mini niche scan: search → estimates → how many apps clear an est. $1k/mo | `GET /api/v1/apps` |

> **Note on `04_competitor_compare.py`:** the public REST API does not currently expose a
> per-app keyword list or a keyword-gap endpoint, so this example compares two apps' documented
> detail records and scores a *shared candidate keyword list* you provide. Full competitor
> keyword-gap analysis (terms rivals rank for that you don't) lives in the web app's
> [Keyword Explorer](https://getappniche.com/docs/aso-keywords).

## REST endpoints at a glance

| Endpoint | Credits | Use it for |
| --- | ---: | --- |
| `GET /api/v1/apps` | 1 | Search/filter apps by category, keyword, revenue, downloads, rating, growth. |
| `GET /api/v1/apps/{app_id}` | 1 | One app's full detail record. `app_id` is `{store}:{store_id}`, e.g. `apple:284882215`. |
| `GET /api/v1/keywords/difficulty` | 10 | Score one ASO keyword's difficulty and opportunity. |
| `GET /api/v1/reviews` | 1 | Enriched review rows with sentiment and topic signals. |

## Credits, rate limits, errors

- Plans include **5,000 API credits/month**, auto-refreshed; every response reports
  `credits_charged`. Extra 500-credit packs are available in the app.
- Rate limit: **60 requests/minute per key** — a 429 comes with a `Retry-After` header.
- Errors you'll see: `401` invalid key · `402` no API access / out of credits · `404` app not
  found (check the `apple:{id}` format) · `422` invalid parameters · `429` rate limited.

## MCP (for AI assistants)

Point any Streamable-HTTP MCP client at `https://api.getappniche.com/mcp` with the
`Authorization: Bearer YOUR_API_KEY` header. Seven tools are exposed: `search_apps` (1 credit),
`get_app_detail` (1), `get_app_historicals` (1), `get_keyword_difficulty` (10),
`batch_keyword_difficulty` (10/keyword), `get_app_reviews` (1), `get_supported_countries` (0).
Setup guide: [Connect AI agents (MCP)](https://getappniche.com/docs/mcp-setup).

## Docs & free tools

- [REST API quickstart](https://getappniche.com/docs/api-quickstart) ·
  [MCP setup](https://getappniche.com/docs/mcp-setup) ·
  [API & MCP overview](https://getappniche.com/docs/api-and-mcp)
- Free, no-account tools: [app revenue lookup & top charts](https://app.getappniche.com/apps) ·
  [app revenue checker](https://getappniche.com/tools/app-revenue-checker) ·
  [ASO keyword opportunity checker](https://getappniche.com/tools/app-store-keyword-tool)

## License

MIT — see [`LICENSE`](LICENSE). Use these examples in anything. GetAppNiche is an independent
product and is not affiliated with Apple or Google.
