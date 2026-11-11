"""Fetch recent X posts about college (ITA) tennis and flag injury/availability chatter.

Deliberately naive: keyword matching + a rough name guess. Not accurate. Have fun.
"""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass

SEARCH_URL = "https://api.x.com/2/tweets/search/recent"

QUERY = (
    '(ITA OR "college tennis" OR #collegetennis OR "dual match") '
    '(injury OR injured OR withdrew OR withdraws OR retired OR "out for" '
    'OR "not playing" OR "out of lineup" OR "day-to-day" OR "returns to lineup" OR "back in lineup") '
    "-is:retweet lang:en"
)

# Order matters: first match wins.
STATUS_RULES = [
    ("RETURNING", re.compile(r"returns? to (the )?lineup|back in (the )?lineup|cleared to play|\bis back\b", re.I)),
    ("OUT", re.compile(r"\bout for\b|season[- ]ending|\bwithdr(ew|aws?)\b|\bretired\b|not playing|out of (the )?lineup|\bsurgery\b", re.I)),
    ("QUESTIONABLE", re.compile(r"day-to-day|questionable|game[- ]time decision|\binjur(y|ed)\b|\bminor\b", re.I)),
]

NAME_RE = re.compile(r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,2})\b")
STOP_NAMES = {"College Tennis", "Dual Match", "Big Ten", "Big East", "Ohio State", "Wake Forest", "North Carolina"}


@dataclass
class Report:
    status: str
    player: str
    text: str
    url: str
    created_at: str


def classify(text: str) -> str | None:
    for status, rx in STATUS_RULES:
        if rx.search(text):
            return status
    return None


def guess_player(text: str) -> str:
    for m in NAME_RE.finditer(text):
        if m.group(1) not in STOP_NAMES:
            return m.group(1)
    return "?"


def parse_tweets(tweets: list[dict]) -> list[Report]:
    out = []
    for t in tweets:
        status = classify(t["text"])
        if status:
            out.append(Report(
                status=status,
                player=guess_player(t["text"]),
                text=" ".join(t["text"].split()),
                url=f"https://x.com/i/status/{t['id']}",
                created_at=t.get("created_at", ""),
            ))
    return out


def fetch_tweets(bearer_token: str, max_results: int = 50) -> list[dict]:
    params = urllib.parse.urlencode({
        "query": QUERY,
        "max_results": max(10, min(max_results, 100)),
        "tweet.fields": "created_at",
    })
    req = urllib.request.Request(
        f"{SEARCH_URL}?{params}", headers={"Authorization": f"Bearer {bearer_token}"}
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp).get("data", [])


def load_demo() -> list[dict]:
    import importlib.resources as res
    with res.files("ita_injury_watch").joinpath("sample_tweets.json").open() as f:
        return json.load(f)
