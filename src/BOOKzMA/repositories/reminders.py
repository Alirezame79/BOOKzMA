from datetime import time

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from BOOKzMA.constants import MAX_REMINDERS
from BOOKzMA.db.models import Reminder, User


async def list_for_user(session: AsyncSession, user_id: int) -> list[Reminder]:
    result = await session.scalars(
        select(Reminder).where(Reminder.user_id == user_id).order_by(Reminder.remind_at)
    )
    return list(result)


async def add(session: AsyncSession, user_id: int, at: time) -> str:
    """نتیجه: ok / limit / dup"""
    count = await session.scalar(
        select(func.count()).select_from(Reminder).where(Reminder.user_id == user_id)
    )
    if (count or 0) >= MAX_REMINDERS:
        return "limit"
    stmt = (
        insert(Reminder)
        .values(user_id=user_id, remind_at=at)
        .on_conflict_do_nothing()
        .returning(Reminder.id)
    )
    result = await session.execute(stmt)
    return "ok" if result.first() is not None else "dup"


async def delete_one(session: AsyncSession, user_id: int, reminder_id: int) -> None:
    await session.execute(
        delete(Reminder).where(Reminder.id == reminder_id, Reminder.user_id == user_id)
    )


async def delete_all_for_user(session: AsyncSession, user_id: int) -> None:
    await session.execute(delete(Reminder).where(Reminder.user_id == user_id))


async def list_all_with_users(session: AsyncSession) -> list[tuple[Reminder, User]]:
    result = await session.execute(select(Reminder, User).join(User, User.id == Reminder.user_id))
    return [(reminder, user) for reminder, user in result.all()]
