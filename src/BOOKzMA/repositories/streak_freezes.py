from datetime import date

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from BOOKzMA.db.models import StreakFreeze


async def balance(session: AsyncSession, user_id: int) -> int:
    earned, used = (
        await session.execute(
            select(
                func.count().filter(StreakFreeze.kind == "earned"),
                func.count().filter(StreakFreeze.kind == "used"),
            ).where(StreakFreeze.user_id == user_id)
        )
    ).one()
    return max(0, earned - used)


async def used_days(session: AsyncSession, user_id: int) -> list[date]:
    result = await session.scalars(
        select(StreakFreeze.day).where(
            StreakFreeze.user_id == user_id, StreakFreeze.kind == "used"
        )
    )
    return list(result)


async def add_event(session: AsyncSession, user_id: int, kind: str, day: date) -> bool:
    if kind not in {"earned", "used"}:
        raise ValueError("invalid streak freeze event")
    stmt = (
        insert(StreakFreeze)
        .values(user_id=user_id, kind=kind, day=day)
        .on_conflict_do_nothing(index_elements=["user_id", "kind", "day"])
        .returning(StreakFreeze.id)
    )
    return (await session.execute(stmt)).first() is not None