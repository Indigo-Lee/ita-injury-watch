from ita_injury_watch.core import classify, guess_player, load_demo, parse_tweets


def test_classify():
    assert classify("Sam Lee returns to lineup") == "RETURNING"
    assert classify("Jordan Smith is out for the season") == "OUT"
    assert classify("Alex Rivera day-to-day") == "QUESTIONABLE"
    assert classify("Great crowd today") is None


def test_guess_player():
    assert guess_player("Jordan Smith is out for the season") == "Jordan Smith"


def test_demo_parses():
    reports = parse_tweets(load_demo())
    assert len(reports) == 4
