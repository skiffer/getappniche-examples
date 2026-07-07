# Claude Code + GetAppNiche MCP

Give Claude Code direct tools to query live iOS App Store data — app search with revenue and
download **estimates**, keyword difficulty, and reviews. No code, no CSV copy-pasting.

## 1. Get an API key

Create one at [app.getappniche.com/settings/api-keys](https://app.getappniche.com/settings/api-keys)
(shown once; looks like `getappniche_...`).

## 2. Add the server — one command

```bash
claude mcp add --transport http getappniche https://api.getappniche.com/mcp --header "Authorization: Bearer YOUR_API_KEY"
```

## 3. Ask questions

Claude picks the right tool automatically — you never call tools by name:

- *"Which meditation apps grew fastest last month?"*
- *"Pull the details for Calm and summarize how it monetizes."*
- *"How hard is it to rank for 'habit tracker' in the US?"*
- *"Score these 8 keyword ideas and rank them by opportunity."*
- *"What do users complain about most in this sleep app's reviews?"*

## Available tools and credit costs

| Tool | Credits | What it does |
| --- | ---: | --- |
| `search_apps` | 1 | Search/filter iOS apps by category, keyword, revenue, downloads, rating, growth. |
| `get_app_detail` | 1 | Full profile of one app: estimates, ratings, keywords, metadata. |
| `get_app_historicals` | 1 | Historical metric points for one app over time. |
| `get_keyword_difficulty` | 10 | Score one ASO keyword for difficulty and opportunity. |
| `batch_keyword_difficulty` | 10 per keyword | Score up to 10 keywords in one call. |
| `get_app_reviews` | 1 | Review rows with sentiment and topic signals. |
| `get_supported_countries` | 0 | List supported country codes. |

Every call reports `credits_charged`. Plans include 5,000 credits/month; rate limit is
60 requests/minute per key (429 responses include `Retry-After`).

## Troubleshooting

- `401` — key missing/mistyped; check it starts with `getappniche_` and the header reads
  `Authorization: Bearer ...`.
- `402` — out of credits or plan lacks API access; check
  [app.getappniche.com/settings](https://app.getappniche.com/settings).
- Tools don't appear — re-run the command and confirm the URL is exactly
  `https://api.getappniche.com/mcp`.

Full guide: [getappniche.com/docs/mcp-setup](https://getappniche.com/docs/mcp-setup)
