from datetime import time

from BOOKzMA.utils import fa, local_today, parse_time, safe_zone


def test_parse_time_formats():
    assert parse_time("21:30") == time(21, 30)
    assert parse_time("۲۱:۳۰") == time(21, 30)
    assert parse_time("9.05") == time(9, 5)
    assert parse_time("21") == time(21, 0)


def test_parse_time_invalid():
    assert parse_time("24:00") is None
    assert parse_time("12:60") is None
    assert parse_time("سلام") is None
    assert parse_time("") is None


def test_fa_digits():
    assert fa(120) == "۱۲۰"


def test_bad_timezone_falls_back():
    assert str(safe_zone("Nope/Nowhere")) == "Asia/Tehran"
    assert local_today("Nope/Nowhere") == local_today("Asia/Tehran")
