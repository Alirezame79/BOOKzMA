from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from BOOKzMA.db.models import User


async def get_or_create(session: AsyncSession, user_id: int, username: str | None) -> User:
    stmt = (
        insert(User)
        .values(id=user_id, username=username)
        .on_conflict_do_update(index_elements=["id"], set_={"username": username})
    )
    await session.execute(stmt)
    user = await session.get(User, user_id, populate_existing=True)
    if user is None:
        raise RuntimeError(f"user {user_id} not found after upsert")
    return user


async def set_timezone(session: AsyncSession, user_id: int, tz_name: str) -> None:
    await session.execute(update(User).where(User.id == user_id).values(timezone=tz_name))
