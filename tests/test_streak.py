from datetime import date, timedelta

from BOOKzMA.services.streak import compute_streak, longest_streak, week_strip, weekly_summary

TODAY = date(2026, 10, 21)


def ago(n):
    return TODAY - timedelta(days=n)


def test_empty():
    assert compute_streak([], TODAY) == 0


def test_today_and_before():
    assert compute_streak([ago(0), ago(1), ago(2)], TODAY) == 3


def test_only_yesterday_keeps_streak():
    assert compute_streak([ago(1), ago(2)], TODAY) == 2


def test_missed_a_day_resets():
    assert compute_streak([ago(2), ago(3)], TODAY) == 0


def test_gap_stops_the_count():
    assert compute_streak([ago(0), ago(1), ago(3), ago(4)], TODAY) == 2


def test_duplicates_ignored():
    assert compute_streak([ago(0), ago(0), ago(1)], TODAY) == 2


def test_longest():
    assert longest_streak([]) == 0
    assert longest_streak([ago(0), ago(1), ago(5), ago(6), ago(7), ago(8)]) == 4


def test_week_strip():
    assert week_strip([ago(0), ago(1)], TODAY) == "▫️ ▫️ ▫️ ▫️ ▫️ ✅ ✅"
    assert week_strip([ago(1)], TODAY) == "▫️ ▫️ ▫️ ▫️ ▫️ ✅ 🟡"


def test_weekly_summary_counts_only_the_last_seven_days():
    summary = weekly_summary([ago(0), ago(2), ago(6), ago(7)], TODAY)

    assert summary["start"] == ago(6)
    assert summary["end"] == TODAY
    assert summary["days_read"] == 3
    assert summary["streak"] == 1
    assert len(summary["days"]) == 7
