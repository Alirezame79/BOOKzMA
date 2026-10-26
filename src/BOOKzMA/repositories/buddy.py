"""Repository رفیق مطالعه (C-06): صف، جفت‌شدن قفل‌شده، تلنگر و پایان هم‌یاری."""

from datetime import date, datetime, timezone

from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from BOOKzMA.db.models import BuddyPair, BuddyQueue


async def active_pair(
    session: AsyncSession, user_id: int
) -> tuple[BuddyPair, int] | None:
    """جفت فعال کاربر به‌همراه شناسهٔ رفیق."""
    result = await session.execute(
        select(BuddyPair).where(
            BuddyPair.status == "active",
            (BuddyPair.user_a == user_id) | (BuddyPair.user_b == user_id),
        )
    )
    pair = result.scalar_one_or_none()
    if pair is None:
        return None
    return pair, pair.user_b if pair.user_a == user_id else pair.user_a


async def is_queued(session: AsyncSession, user_id: int) -> bool:
    return (
        await session.scalar(select(BuddyQueue.user_id).where(BuddyQueue.user_id == user_id))
        is not None
    )


async def join_queue(session: AsyncSession, user_id: int) -> None:
    await session.execute(
        insert(BuddyQueue).values(user_id=user_id).on_conflict_do_nothing(index_elements=["user_id"])
    )


async def leave_queue(session: AsyncSession, user_id: int) -> None:
    await session.execute(delete(BuddyQueue).where(BuddyQueue.user_id == user_id))


async def try_match(session: AsyncSession, user_id: int) -> int | None:
    """جفت‌کردن کاربر با قدیمی‌ترین نفر صف؛ باید داخل تراکنش قفل‌شده صدا زده شود.

    ردیف‌های صف row-lock می‌شوند تا دو تراکنش هم‌زمان یک نفر را دوبار جفت نکنند.
    """
    rows = await session.scalars(
        select(BuddyQueue.user_id)
        .order_by(BuddyQueue.joined_at, BuddyQueue.user_id)
        .with_for_update()
    )
    partner = next((uid for uid in rows if uid != user_id), None)
    if partner is None:
        return None
    await session.execute(
        delete(BuddyQueue).where(BuddyQueue.user_id.in_([user_id, partner]))
    )
    session.add(
        BuddyPair(user_a=min(user_id, partner), user_b=max(user_id, partner))
    )
    return partner


async def end_pair(session: AsyncSession, pair: BuddyPair, ended_by: int) -> None:
    await session.execute(
        update(BuddyPair)
        .where(BuddyPair.id == pair.id, BuddyPair.status == "active")
        .values(status="ended", ended_at=datetime.now(timezone.utc), ended_by=ended_by)
    )


async def register_nudge(session: AsyncSession, pair: BuddyPair, day: date) -> bool:
    """سقف روزانه: هر جفت حداکثر یک تلنگر در هر روز محلی."""
    result = await session.execute(
        update(BuddyPair)
        .where(
            BuddyPair.id == pair.id,
            BuddyPair.status == "active",
            (BuddyPair.last_nudge_on.is_(None)) | (BuddyPair.last_nudge_on != day),
        )
        .values(last_nudge_on=day)
        .returning(BuddyPair.id)
    )
    return result.first() is not None


async def stats(session: AsyncSession) -> dict[str, int]:
    """KPI ادمین: جفت‌های فعال و کل جفت‌های تشکیل‌شده."""
    active = (
        await session.scalar(
            select(func.count()).select_from(BuddyPair).where(BuddyPair.status == "active")
        )
        or 0
    )
    total = await session.scalar(select(func.count()).select_from(BuddyPair)) or 0
    return {"buddy_pairs_active": active, "buddy_pairs_total": total}
