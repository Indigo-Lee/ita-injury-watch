import argparse
import csv
import os
import sys

from . import __version__
from .core import fetch_tweets, load_demo, parse_tweets


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="ita-injury-watch", description="Naive ITA tennis injury tracker for X.")
    p.add_argument("--demo", action="store_true", help="use bundled sample posts (no X token needed)")
    p.add_argument("-n", "--max-results", type=int, default=50, help="posts to fetch (10-100)")
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
    if not reports:
        print("Nothing injury-related found.")
        return 0

    for r in reports:
        print(f"[{r.status:<12}] {r.player:<18} {r.text[:90]}\n{'':15}{r.url}")

    if args.csv:
        with open(args.csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["status", "player", "text", "url", "created_at"])
            w.writerows([r.status, r.player, r.text, r.url, r.created_at] for r in reports)
        print(f"\nWrote {len(reports)} rows to {args.csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
