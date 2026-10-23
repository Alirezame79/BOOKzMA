from datetime import time

import pytest
from pydantic import SecretStr

from BOOKzMA.config import Settings
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


def test_admin_ids_parse_multiple_numeric_ids():
    settings = Settings(bot_token=SecretStr("test"), admin_telegram_ids="123, 456,,")

    assert settings.admin_ids == frozenset({123, 456})


def test_admin_ids_reject_invalid_values():
    settings = Settings(bot_token=SecretStr("test"), admin_telegram_ids="123,not-an-id")

    with pytest.raises(ValueError, match="ADMIN_TELEGRAM_IDS"):
        _ = settings.admin_ids


def test_admin_ids_reject_non_ascii_digits():
    settings = Settings(bot_token=SecretStr("test"), admin_telegram_ids="۱۲۳۴۵")

    with pytest.raises(ValueError, match="ADMIN_TELEGRAM_IDS"):
        _ = settings.admin_ids
