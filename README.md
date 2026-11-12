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
ita-injury-watch                       # latest status per player
ita-injury-watch --status OUT          # only players ruled out
ita-injury-watch --all --csv out.csv   # every matching post, saved to CSV
```

Example output:

```
Scanned 8 posts, 4 injury reports.

[OUT         ] Taylor Brooks      (knee)       2026-02-11
               Taylor Brooks retired in the second set with an apparent knee injury at ITA indoors
               https://x.com/i/status/5

[RETURNING   ] Sam Lee                         2026-02-11
               Good news: Sam Lee returns to lineup at #1 singles after missing three matches
               https://x.com/i/status/4
```

API access tiers and rate limits change; the free tier may not include search.

## How it works

1. **Search:** `QUERY` asks X for posts that mention tennis plus college/ITA terms and injury
   terms, and excludes other sports.
2. **Filter:** posts that aren't about tennis, mention another sport, or say a player is
   healthy ("no injury", "injury-free") are dropped.
3. **Classify:** each post is tagged `OUT`, `QUESTIONABLE`, or `RETURNING`.
4. **Extract:** the player is the name closest before the injury phrase, skipping filler like
   "Good news" or "Coach". The body part (wrist, ankle, knee...) is pulled out too.
5. **Dedupe:** by default only the newest report per player is shown, so a "returns to lineup"
   post replaces an older "out" post.

Tweak the query and rules in [`ita_injury_watch/core.py`](ita_injury_watch/core.py).

## Dev

```bash
pip install -e ".[dev]"
pytest
```

## Ideas

- Follow specific team/coach accounts instead of keyword search
- Cross-check against ITA lineup pages
- Map players to schools using team rosters

## License

MIT
