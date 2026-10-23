import asyncio
from datetime import date

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import dialect

from BOOKzMA.db.models import ReadingLog
from BOOKzMA.repositories.analytics import _utc_day, activity_series


def test_utc_day_expression_uses_sqlalchemy_date_type():
    statement = select(_utc_day(ReadingLog.created_at))

    compiled = str(statement.compile(dialect=dialect()))

    assert "CAST(timezone" in compiled
    assert "AS DATE" in compiled


def test_activity_series_converts_result_rows_to_daily_counts():
    today = date(2026, 10, 23)

    class Result:
        def all(self):
            return [(today, 3), (date(2026, 10, 21), 2)]

    class Session:
        async def execute(self, _statement):
            return Result()

    series = asyncio.run(activity_series(Session(), today, days=3))

    assert series == [
        (date(2026, 10, 21), 2),
        (date(2026, 10, 22), 0),
        (today, 3),
    ]