import asyncio
import os
import random
from datetime import date, timedelta

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from BOOKzMA.db.models import ActivityDay, User
from BOOKzMA.repositories import activity, readings, streak_freezes
from BOOKzMA.services.streak_freezes import on_read

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="TEST_DATABASE_URL must point to a disposable PostgreSQL database",
)


def test_freeze_reward_and_use_are_persisted_and_idempotent():
    async def run_test() -> None:
        engine = create_async_engine(TEST_DATABASE_URL)
        session_pool = async_sessionmaker(engine, expire_on_commit=False)
        user_id = 3_000_000_000_000_000_000 + random.randrange(1_000_000_000)
        today = date(2026, 10, 21)
        try:
            async with session_pool.begin() as session:
                session.add(User(id=user_id))
                await activity.record_interaction(session, user_id, today)
                await activity.record_interaction(session, user_id, today)
                activity_rows = await session.scalar(
                    select(func.count()).select_from(ActivityDay).where(
                        ActivityDay.user_id == user_id, ActivityDay.day == today
                    )
                )
                assert activity_rows == 1
                for offset in range(6, -1, -1):
                    await readings.mark_read(session, user_id, today - timedelta(days=offset))
                reward = await on_read(session, user_id, today)
                assert reward.earned
                assert await streak_freezes.balance(session, user_id) == 1

                assert await readings.mark_read(session, user_id, today + timedelta(days=2))
                protection = await on_read(session, user_id, today + timedelta(days=2))
                assert protection.used_day == today + timedelta(days=1)
                assert await streak_freezes.balance(session, user_id) == 0
                assert not await streak_freezes.add_event(
                    session, user_id, "used", today + timedelta(days=1)
                )
        finally:
            async with session_pool() as session:
                await session.execute(delete(User).where(User.id == user_id))
                await session.commit()
            await engine.dispose()

    asyncio.run(run_test())