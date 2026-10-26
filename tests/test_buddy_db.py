import asyncio
import os
import random
from datetime import date, timedelta

import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from BOOKzMA.db.models import BuddyPair, BuddyQueue, User
from BOOKzMA.repositories import analytics
from BOOKzMA.repositories import buddy as buddy_repo
from BOOKzMA.repositories import users as users_repo

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL, reason="TEST_DATABASE_URL must point to a disposable PostgreSQL database"
)


def _uid() -> int:
    return 4_000_000_000_000_000_000 + random.randrange(1_000_000_000)


def test_pairing_queue_end_and_rematch():
    async def run_test() -> None:
        engine = create_async_engine(TEST_DATABASE_URL)
        session_pool = async_sessionmaker(engine, expire_on_commit=False)
        uid_a, uid_b, uid_c = _uid(), _uid(), _uid()
        try:
            async with session_pool.begin() as session:
                session.add_all(User(id=uid) for uid in (uid_a, uid_b, uid_c))

            async with session_pool.begin() as session:
                await buddy_repo.join_queue(session, uid_a)
                assert await buddy_repo.try_match(session, uid_a) is None

            async with session_pool.begin() as session:
                await buddy_repo.join_queue(session, uid_b)
                assert await buddy_repo.try_match(session, uid_b) == uid_a

            async with session_pool() as session:
                found = await buddy_repo.active_pair(session, uid_a)
                assert found is not None
                pair, buddy_id = found
                assert buddy_id == uid_b
                assert await buddy_repo.is_queued(session, uid_a) is False

            async with session_pool.begin() as session:
                await buddy_repo.end_pair(session, pair, uid_a)

            async with session_pool() as session:
                assert await buddy_repo.active_pair(session, uid_a) is None

            # نفر سوم و کاربر آزادشده دوباره جفت می‌شوند
            async with session_pool.begin() as session:
                await buddy_repo.join_queue(session, uid_c)
                assert await buddy_repo.try_match(session, uid_c) in (uid_a, uid_b)

            async with session_pool() as session:
                stats = await analytics.dashboard(session, date(2026, 10, 25))
                assert stats["buddy_pairs_total"] >= 2
        finally:
            async with session_pool() as session:
                await session.execute(delete(User).where(User.id.in_([uid_a, uid_b, uid_c])))
                await session.commit()
            await engine.dispose()

    asyncio.run(run_test())


def test_nudge_cap_is_once_per_day_and_per_pair():
    async def run_test() -> None:
        engine = create_async_engine(TEST_DATABASE_URL)
        session_pool = async_sessionmaker(engine, expire_on_commit=False)
        uid_a, uid_b = _uid(), _uid()
        try:
            async with session_pool.begin() as session:
                session.add_all(User(id=uid) for uid in (uid_a, uid_b))
                session.add(BuddyPair(user_a=min(uid_a, uid_b), user_b=max(uid_a, uid_b)))

            async with session_pool.begin() as session:
                found = await buddy_repo.active_pair(session, uid_a)
                assert found is not None
                pair, _buddy_id = found
                first_day = date(2026, 10, 25)
                assert await buddy_repo.register_nudge(session, pair, first_day) is True
                assert await buddy_repo.register_nudge(session, pair, first_day) is False
                next_day = first_day + timedelta(days=1)
                assert await buddy_repo.register_nudge(session, pair, next_day) is True
        finally:
            async with session_pool() as session:
                await session.execute(delete(User).where(User.id.in_([uid_a, uid_b])))
                await session.commit()
            await engine.dispose()

    asyncio.run(run_test())


def test_account_deletion_cascades_pair_and_queue():
    async def run_test() -> None:
        engine = create_async_engine(TEST_DATABASE_URL)
        session_pool = async_sessionmaker(engine, expire_on_commit=False)
        uid_a, uid_b = _uid(), _uid()
        try:
            async with session_pool.begin() as session:
                session.add_all(User(id=uid) for uid in (uid_a, uid_b))
                session.add(BuddyQueue(user_id=uid_a))
                session.add(BuddyPair(user_a=min(uid_a, uid_b), user_b=max(uid_a, uid_b)))

            async with session_pool.begin() as session:
                await users_repo.delete_account(session, uid_a, "privacy")

            async with session_pool() as session:
                assert await buddy_repo.active_pair(session, uid_b) is None
                assert await buddy_repo.is_queued(session, uid_a) is False

            async with session_pool() as session:
                await session.execute(delete(User).where(User.id == uid_b))
                await session.commit()
        finally:
            await engine.dispose()

    asyncio.run(run_test())
