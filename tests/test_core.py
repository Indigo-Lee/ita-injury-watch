from ita_injury_watch.core import (
    classify, guess_injury, guess_player, is_relevant, latest_by_player, load_demo, parse_tweets,
)


def test_classify():
    assert classify("Sam Lee returns to lineup") == "RETURNING"
    assert classify("Jordan Smith is out for the season") == "OUT"
    assert classify("Alex Rivera day-to-day") == "QUESTIONABLE"
    assert classify("Great crowd today") is None


def test_guess_player_skips_filler_words():
    assert guess_player("Good news: Sam Lee returns to lineup") == "Sam Lee"
    assert guess_player("Jordan Smith is out for the season") == "Jordan Smith"


def test_guess_injury():
    assert guess_injury("out with a tweaked Ankle") == "ankle"
    assert guess_injury("out for the season") == ""


def test_relevance_filters():
    assert not is_relevant("Quarterback injured, out for the season, football")
    assert not is_relevant("Riley is healthy, no injury concerns, tennis")
    assert is_relevant("Taylor retired in the second set at ITA indoors")


def test_demo_end_to_end():
    reports = parse_tweets(load_demo())
    assert len(reports) == 5  # drops non-injury, football, and "healthy" posts
    latest = {r.player: r.status for r in latest_by_player(reports)}
    assert latest == {
        "Jordan Smith": "OUT",
        "Alex Rivera": "QUESTIONABLE",
        "Sam Lee": "RETURNING",  # newer post overrides the earlier OUT
        "Taylor Brooks": "OUT",
    }
