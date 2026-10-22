from collections.abc import Iterable
from datetime import date, timedelta


def compute_streak(days: Iterable[date], today: date) -> int:
    # اگه امروز هنوز نخونده ولی دیروز خونده، استریک تا آخر امروز زنده‌ست
    day_set = set(days)
    cursor = today if today in day_set else today - timedelta(days=1)
    count = 0
    while cursor in day_set:
        count += 1
        cursor -= timedelta(days=1)
    return count


def longest_streak(days: Iterable[date]) -> int:
    best = run = 0
    prev: date | None = None
    for d in sorted(set(days)):
        run = run + 1 if prev is not None and d - prev == timedelta(days=1) else 1
        best = max(best, run)
        prev = d
    return best


def week_strip(days: Iterable[date], today: date) -> str:
    # هفت روز آخر، آخری امروزه
    day_set = set(days)
    cells = []
    for offset in range(6, -1, -1):
        d = today - timedelta(days=offset)
        if d in day_set:
            cells.append("✅")
        elif d == today:
            cells.append("🟡")
        else:
            cells.append("▫️")
    return " ".join(cells)


def weekly_summary(days: Iterable[date], today: date) -> dict[str, object]:
    day_set = set(days)
    week_days = [today - timedelta(days=offset) for offset in range(6, -1, -1)]
    read_days = [day for day in week_days if day in day_set]
    return {
        "start": week_days[0],
        "end": week_days[-1],
        "days_read": len(read_days),
        "streak": compute_streak(day_set, today),
        "days": [{"date": day, "read": day in day_set} for day in week_days],
    }
