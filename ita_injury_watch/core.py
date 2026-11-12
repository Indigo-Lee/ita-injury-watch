"""Scan recent X posts for college (ITA) tennis injury and availability reports."""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

SEARCH_URL = "https://api.x.com/2/tweets/search/recent"

QUERY = (
    'tennis (college OR NCAA OR ITA OR #collegetennis OR "dual match" OR singles OR doubles) '
    '(injury OR injured OR withdrew OR withdraws OR retired OR "out for" OR "not playing" '
    'OR "out of lineup" OR "day-to-day" OR "returns to lineup" OR "back in lineup" OR "cleared to play" OR surgery) '
    "-is:retweet lang:en -NFL -NBA -football -basketball -baseball -soccer"
)

# Posts must look like tennis to count (the API query can still leak other sports).
TENNIS_RE = re.compile(r"tennis|#collegetennis|\bITA\b|\bsingles\b|\bdoubles\b|dual match|\bset\b|lineup", re.I)
OTHER_SPORT_RE = re.compile(r"\b(NFL|NBA|MLB|NHL|football|basketball|baseball|soccer|quarterback|hockey)\b", re.I)
NEGATION_RE = re.compile(r"\b(no|not|without|zero)\s+(injur\w*|issues?)\b|injury[- ]free|healthy", re.I)

# Order matters: first match wins.
STATUS_RULES = [
    ("RETURNING", re.compile(r"returns? to (the )?lineup|back in (the )?lineup|cleared to (play|return)|\bis back\b|return(s|ing)? from injury", re.I)),
    ("OUT", re.compile(r"\bout for\b|season[- ]ending|\bwithdr(ew|aws?)\b|\bretired\b|not playing|out of (the )?lineup|\bsurgery\b|\bwill miss\b|\bsidelined\b", re.I)),
    ("QUESTIONABLE", re.compile(r"day-to-day|questionable|game[- ]time decision|\binjur(y|ed)\b|\btweaked\b|\bbanged up\b|\bsore\b", re.I)),
]

BODY_PARTS = [
    "wrist", "ankle", "knee", "shoulder", "elbow", "back", "hamstring", "hip",
    "abdominal", "ab", "calf", "foot", "hand", "groin", "illness", "concussion",
]
BODY_RE = re.compile(r"\b(" + "|".join(BODY_PARTS) + r")\b", re.I)

NAME_RE = re.compile(r"\b([A-Z][a-z'\-]+(?:\s[A-Z][a-z'\-]+){1,2})\b")
HANDLE_RE = re.compile(r"@(\w{2,15})")
STOP_WORDS = {
    "Good", "Great", "Big", "Huge", "Update", "Injury", "News", "Breaking", "College", "Tennis",
    "Dual", "Match", "Head", "Coach", "Ohio", "Wake", "North", "South", "Texas", "Florida",
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    "January", "February", "March", "April", "May", "June", "July", "August",
    "September", "October", "November", "December", "The", "Our", "Sources", "Per",
}


@dataclass
class Report:
    status: str
    player: str
    injury: str
    text: str
    url: str
    created_at: str


def is_relevant(text: str) -> bool:
    return bool(TENNIS_RE.search(text)) and not OTHER_SPORT_RE.search(text) and not NEGATION_RE.search(text)


def classify(text: str) -> str | None:
    for status, rx in STATUS_RULES:
        if rx.search(text):
            return status
    return None


def guess_injury(text: str) -> str:
    m = BODY_RE.search(text)
    return m.group(1).lower() if m else ""


def guess_player(text: str) -> str:
    """Pick the name closest *before* the status phrase, falling back to the first name/handle."""
    candidates = [
        (m.start(), m.group(1)) for m in NAME_RE.finditer(text)
        if m.group(1).split()[0] not in STOP_WORDS
    ]
    status_pos = min((m.start() for _, rx in STATUS_RULES if (m := rx.search(text))), default=len(text))
    before = [c for c in candidates if c[0] < status_pos]
    if before:
        return before[-1][1]
    if candidates:
        return candidates[0][1]
    h = HANDLE_RE.search(text)
    return f"@{h.group(1)}" if h else "?"


def parse_tweets(tweets: list[dict]) -> list[Report]:
    out = []
    for t in tweets:
        text = " ".join(t["text"].split())
        if not is_relevant(text):
            continue
        status = classify(text)
        if not status:
            continue
        out.append(Report(
            status=status,
            player=guess_player(text),
            injury=guess_injury(text),
            text=text,
            url=f"https://x.com/i/status/{t['id']}",
            created_at=t.get("created_at", ""),
        ))
    return out


def latest_by_player(reports: list[Report]) -> list[Report]:
    """Keep only the most recent report for each player."""
    best: dict[str, Report] = {}
    for r in reports:
        key = r.player.lower()
        if key == "?" or key not in best or r.created_at > best[key].created_at:
            best[key if key != "?" else r.url] = r
    return sorted(best.values(), key=lambda r: r.created_at, reverse=True)


def fetch_tweets(bearer_token: str, max_results: int = 100) -> list[dict]:
    params = urllib.parse.urlencode({
        "query": QUERY,
        "max_results": max(10, min(max_results, 100)),
        "tweet.fields": "created_at",
    })
    req = urllib.request.Request(
        f"{SEARCH_URL}?{params}", headers={"Authorization": f"Bearer {bearer_token}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.load(resp).get("data", [])
    except urllib.error.HTTPError as e:
        hints = {
            401: "token is invalid",
            403: "your X API plan doesn't include search",
            429: "rate limited, wait ~15 minutes",
        }
        raise RuntimeError(f"HTTP {e.code}: {hints.get(e.code, e.reason)}") from e


def load_demo() -> list[dict]:
    import importlib.resources as res
    with res.files("ita_injury_watch").joinpath("sample_tweets.json").open() as f:
        return json.load(f)
