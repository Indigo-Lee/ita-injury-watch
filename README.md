# 🎾 ita-injury-watch

A tiny, zero-dependency Python CLI that searches recent X posts for college (ITA) tennis
injury and lineup chatter, and tags each hit as `OUT`, `QUESTIONABLE`, or `RETURNING`.

## Quick start

```bash
git clone https://github.com/Indigo-Lee/ita-injury-watch.git
cd ita-injury-watch
pip install -e .

ita-injury-watch --demo        # works instantly, no token needed
```

## Live mode

Uses the official X API v2 recent-search endpoint (scraping x.com directly requires a login
and violates their terms). You need a bearer token from the [X developer portal](https://developer.x.com).

```bash
export X_BEARER_TOKEN=your_token_here
ita-injury-watch -n 100 --csv injuries.csv
```

Example output:

```
[OUT         ] Jordan Smith       Jordan Smith is out for the season after wrist surgery...
               https://x.com/i/status/1
[QUESTIONABLE] Alex Rivera        Alex Rivera day-to-day with a tweaked ankle...
```

Note: API access tiers and rate limits change; the free tier may not include search.

## How it works

1. `core.QUERY` searches for ITA / college-tennis terms alongside injury terms.
2. `core.STATUS_RULES` regexes bucket each post.
3. `core.guess_player` grabs the first capitalized "First Last" in the text.

Tweak the query and regexes in [`ita_injury_watch/core.py`](ita_injury_watch/core.py).

## Dev

```bash
pip install -e ".[dev]"
pytest
```

## Ideas

- Follow specific team/coach accounts instead of keyword search
- Cross-check against ITA lineup pages
- Dedupe by player, keep latest status

## License

MIT
