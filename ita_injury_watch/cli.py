import argparse
import csv
import os
import sys

from . import __version__
from .core import fetch_tweets, latest_by_player, load_demo, parse_tweets


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="ita-injury-watch", description="Scan X for ITA college tennis injury reports.")
    p.add_argument("--demo", action="store_true", help="use bundled sample posts (no X token needed)")
    p.add_argument("-n", "--max-results", type=int, default=100, help="posts to fetch (10-100)")
    p.add_argument("--all", action="store_true", help="show every matching post, not just the latest per player")
    p.add_argument("--status", choices=["OUT", "QUESTIONABLE", "RETURNING"], help="only show this status")
    p.add_argument("--csv", metavar="FILE", help="also write results to a CSV file")
    p.add_argument("--version", action="version", version=__version__)
    args = p.parse_args(argv)

    if args.demo:
        tweets = load_demo()
    else:
        token = os.environ.get("X_BEARER_TOKEN")
        if not token:
            print("Set X_BEARER_TOKEN (see README) or run with --demo.", file=sys.stderr)
            return 1
        try:
            tweets = fetch_tweets(token, args.max_results)
        except Exception as e:  # noqa: BLE001
            print(f"X API error: {e}", file=sys.stderr)
            return 2

    reports = parse_tweets(tweets)
    if not args.all:
        reports = latest_by_player(reports)
    if args.status:
        reports = [r for r in reports if r.status == args.status]

    print(f"Scanned {len(tweets)} posts, {len(reports)} injury reports.\n")
    for r in reports:
        injury = f"({r.injury})" if r.injury else ""
        print(f"[{r.status:<12}] {r.player:<18} {injury:<12} {r.created_at[:10]}")
        print(f"{'':15}{r.text[:100]}")
        print(f"{'':15}{r.url}\n")

    if args.csv:
        with open(args.csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["status", "player", "injury", "created_at", "text", "url"])
            w.writerows([r.status, r.player, r.injury, r.created_at, r.text, r.url] for r in reports)
        print(f"Wrote {len(reports)} rows to {args.csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
