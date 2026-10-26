import asyncio
import os
import random
from datetime import date, datetime, time, timedelta, timezone

import pytest
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from BOOKzMA.db.models import BroadcastCampaign, MesbakEntry, MesbakProfile, User
from BOOKzMA.repositories import analytics, broadcasts, mesbak
from BOOKzMA.services.mesbak import completed_days, current_streak, longest_streak
from BOOKzMA.services.mesbak_social import invite_token_hash, new_invite_token

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="TEST_DATABASE_URL must point to a disposable PostgreSQL database",
)


def test_mesbak_goal_change_idempotency_cohort_and_account_cascade():
    async def run_test() -> None:
        engine = create_async_engine(TEST_DATABASE_URL)
        session_pool = async_sessionmaker(engine, expire_on_commit=False)
        user_id = 4_200_000_000_000_000_000 + random.randrange(500_000_000_000_000_000)
        today = date(2026, 10, 26)
        try:
            async with session_pool() as session:
                session.add(User(id=user_id))
                await session.commit()

                await mesbak.configure(
                    session,
                    user_id,
                    3,
                    [time(6, 30), time(13), time(16)],
                    today,
                )
                await session.commit()
                assert await mesbak.set_reminder_time(
                    session, user_id, 1, time(13)
                ) == "duplicate"
                assert await mesbak.set_reminder_time(
                    session, user_id, 1, time(7)
                ) == "ok"
                await session.commit()
                first = await mesbak.record_occurrence(session, user_id, today, 1)
                duplicate = await mesbak.record_occurrence(session, user_id, today, 1)
                second = await mesbak.record_occurrence(session, user_id, today, 2)
                third = await mesbak.record_occurrence(session, user_id, today, 3)
                await session.commit()
                assert (first.status, first.completed_count, first.day_complete) == (
                    "ok",
                    1,
                    False,
                )
                assert (duplicate.status, duplicate.completed_count) == ("duplicate", 1)
                assert (second.completed_count, second.day_complete) == (2, False)
                assert (third.completed_count, third.day_complete) == (3, True)

                await mesbak.configure(
                    session,
                    user_id,
                    2,
                    [time(7), time(14)],
                    today,
                )
                await session.commit()
                profile = await mesbak.get_profile(session, user_id, today)
                assert profile is not None
                assert (profile.daily_goal, profile.next_daily_goal) == (3, 2)

                tomorrow = today + timedelta(days=1)
                profile = await mesbak.get_profile(session, user_id, tomorrow)
                assert profile is not None
                assert (profile.daily_goal, profile.next_daily_goal) == (2, None)
                await session.commit()
                assert (
                    await mesbak.record_occurrence(session, user_id, tomorrow, 3)
                ).status == "invalid_slot"
                await mesbak.record_occurrence(session, user_id, tomorrow, 1)
                await mesbak.record_occurrence(session, user_id, tomorrow, 2)
                await session.commit()

                records = await mesbak.daily_records(session, user_id)
                days = completed_days(records)
                assert current_streak(days, tomorrow) == 2
                assert longest_streak(days) == 2

                campaign_id, recipient_count = await broadcasts.create(
                    session, user_id, "Lesson", audience="mesbak"
                )
                await session.commit()
                assert recipient_count >= 1
                campaign = await session.get(BroadcastCampaign, campaign_id)
                assert campaign is not None
                assert await broadcasts.eligible_recipient(session, campaign, user_id)

                profile = await session.get(MesbakProfile, user_id)
                assert profile is not None
                profile.enabled = False
                await session.commit()
                assert not await broadcasts.eligible_recipient(session, campaign, user_id)

                entry = await session.scalar(
                    select(MesbakEntry).where(MesbakEntry.user_id == user_id)
                )
                assert entry is not None
                await session.execute(
                    delete(BroadcastCampaign).where(BroadcastCampaign.admin_id == user_id)
                )
                await session.execute(delete(User).where(User.id == user_id))
                await session.commit()
                session.expire_all()
                assert await session.get(MesbakProfile, user_id) is None
                assert await session.scalar(
                    select(MesbakEntry.user_id).where(MesbakEntry.user_id == user_id)
                ) is None
        finally:
            async with session_pool() as session:
                await session.execute(
                    delete(BroadcastCampaign).where(BroadcastCampaign.admin_id == user_id)
                )
                await session.execute(delete(User).where(User.id == user_id))
                await session.commit()
            await engine.dispose()

    asyncio.run(run_test())


def test_concurrent_same_slot_record_is_idempotent():
    async def run_test() -> None:
        engine = create_async_engine(TEST_DATABASE_URL)
        session_pool = async_sessionmaker(engine, expire_on_commit=False)
        user_id = 4_300_000_000_000_000_000 + random.randrange(400_000_000_000_000_000)
        today = date(2026, 10, 27)
        try:
            async with session_pool() as session:
                session.add(User(id=user_id))
                await session.commit()
                await mesbak.configure(
                    session, user_id, 1, [time(6, 30)], today - timedelta(days=1)
                )
                await session.commit()

            async def record_once():
                async with session_pool() as session:
                    result = await mesbak.record_occurrence(session, user_id, today, 1)
                    await session.commit()
                    return result

            results = await asyncio.gather(record_once(), record_once())
            assert sorted(result.status for result in results) == ["duplicate", "ok"]
            async with session_pool() as session:
                assert len(await mesbak.entries_for_day(session, user_id, today)) == 1
        finally:
            async with session_pool() as session:
                await session.execute(delete(User).where(User.id == user_id))
                await session.commit()
            await engine.dispose()

    asyncio.run(run_test())


def test_social_opt_in_challenge_league_and_buddy_limits():
    async def run_test() -> None:
        engine = create_async_engine(TEST_DATABASE_URL)
        session_pool = async_sessionmaker(engine, expire_on_commit=False)
        user_ids = [
            4_400_000_000_000_000_000 + random.randrange(100_000_000_000_000_000),
            4_600_000_000_000_000_000 + random.randrange(100_000_000_000_000_000),
        ]
        today = date.today()
        try:
            async with session_pool() as session:
                session.add_all(
                    [
                        User(id=user_ids[0], display_name="Member A"),
                        User(id=user_ids[1], display_name="Member B"),
                    ]
                )
                await session.commit()
                for user_id in user_ids:
                    await mesbak.configure(
                        session, user_id, 1, [time(6, 30)], today
                    )
                await session.commit()

                assert await mesbak.toggle_league(session, user_ids[0], True)
                league = await mesbak.league_rows(session, today)
                assert [row[0] for row in league] == [user_ids[0]]

                challenge, status = await mesbak.start_challenge(
                    session, user_ids[0], 7, today
                )
                assert challenge is not None and status == "started"
                for offset in range(7):
                    await mesbak.record_occurrence(
                        session, user_ids[0], today + timedelta(days=offset), 1
                    )
                await session.commit()
                challenge, progress = await mesbak.challenge_state(
                    session, user_ids[0], today + timedelta(days=6)
                )
                assert challenge is not None
                assert (progress, challenge.status) == (7, "completed")

                token_hash = invite_token_hash(new_invite_token())
                assert token_hash is not None
                now = datetime.now(timezone.utc)
                assert await mesbak.create_buddy_invite(
                    session, user_ids[0], token_hash, now + timedelta(days=7)
                )
                status, inviter_id = await mesbak.redeem_buddy_invite(
                    session, token_hash, user_ids[1], now
                )
                await session.commit()
                assert (status, inviter_id) == ("accepted", user_ids[0])
                buddy_rows = await mesbak.buddy_rows(session, user_ids[0])
                assert len(buddy_rows) == 1
                pair_id = buddy_rows[0][0]
                assert await mesbak.claim_buddy_nudge(
                    session, user_ids[0], pair_id, today
                ) == ("ok", user_ids[1], "invite")
                await session.commit()
                assert await mesbak.claim_buddy_nudge(
                    session, user_ids[0], pair_id, today
                ) == ("limit", user_ids[1], "invite")
                followup_challenge, challenge_status = await mesbak.start_challenge(
                    session, user_ids[0], 30, today + timedelta(days=7)
                )
                assert followup_challenge is not None and challenge_status == "started"
                followup_hash = invite_token_hash(new_invite_token())
                assert followup_hash is not None
                assert await mesbak.create_buddy_invite(
                    session, user_ids[0], followup_hash, now + timedelta(days=7)
                )
                before_exit = await analytics.mesbak_stats(
                    session, today + timedelta(days=6)
                )
                assert await mesbak.set_enabled(session, user_ids[0], False)
                after_exit = await analytics.mesbak_stats(
                    session, today + timedelta(days=6)
                )
                assert after_exit["mesbak_members"] == before_exit["mesbak_members"] - 1
                assert after_exit["mesbak_active_7d"] == before_exit["mesbak_active_7d"] - 1
                await session.commit()
                assert await mesbak.buddy_rows(session, user_ids[0]) == []
                profile = await mesbak.get_profile(session, user_ids[0])
                assert profile is not None
                assert not profile.league_opt_in
                assert await mesbak.challenge_state(session, user_ids[0], today) == (None, 0)
                assert await mesbak.redeem_buddy_invite(
                    session, followup_hash, user_ids[1], now
                ) == ("unavailable", None)
                await mesbak.configure(
                    session,
                    user_ids[0],
                    1,
                    [time(6, 30)],
                    today + timedelta(days=1),
                )
                await session.commit()
                profile = await mesbak.get_profile(session, user_ids[0])
                assert profile is not None and profile.enabled
                assert not profile.league_opt_in
        finally:
            async with session_pool() as session:
                await session.execute(delete(User).where(User.id.in_(user_ids)))
                await session.commit()
            await engine.dispose()

    asyncio.run(run_test())


def test_mesbak_random_buddy_queue_is_fifo_and_anonymous():
    async def run_test() -> None:
        engine = create_async_engine(TEST_DATABASE_URL)
        session_pool = async_sessionmaker(engine, expire_on_commit=False)
        user_ids = [
            4_300_000_000_000_000_000 + random.randrange(100_000_000_000_000_000)
            for _ in range(3)
        ]
        today = date(2026, 10, 26)
        try:
            async with session_pool() as session:
                session.add_all(
                    [User(id=user_ids[0], display_name="First User"),
                     User(id=user_ids[1], display_name="Second User"),
                     User(id=user_ids[2], display_name="Waiting User")]
                )
                await session.commit()
                for user_id in user_ids:
                    await mesbak.configure(session, user_id, 1, [time(6, 30)], today)
                await session.commit()
                stats_before = await analytics.mesbak_stats(session, today)

                assert await mesbak.join_random_buddy_queue(session, user_ids[0]) == (
                    "waiting",
                    None,
                )
                await session.commit()
                assert await mesbak.join_random_buddy_queue(session, user_ids[1]) == (
                    "matched",
                    user_ids[0],
                )
                await session.commit()
                assert not await mesbak.is_random_buddy_queued(session, user_ids[0])
                assert not await mesbak.is_random_buddy_queued(session, user_ids[1])

                rows = await mesbak.buddy_rows(session, user_ids[0])
                assert len(rows) == 1
                assert rows[0][1:] == (user_ids[1], "Second User", "random")
                pair_id = rows[0][0]
                assert await mesbak.join_random_buddy_queue(session, user_ids[0]) == (
                    "already",
                    None,
                )
                assert await mesbak.claim_buddy_nudge(
                    session, user_ids[0], pair_id, today
                ) == ("ok", user_ids[1], "random")
                await session.commit()

                assert await mesbak.join_random_buddy_queue(session, user_ids[2]) == (
                    "waiting",
                    None,
                )
                assert await mesbak.is_random_buddy_queued(session, user_ids[2])
                assert await mesbak.set_enabled(session, user_ids[2], False)
                await session.commit()
                assert not await mesbak.is_random_buddy_queued(session, user_ids[2])

                stats = await analytics.mesbak_stats(session, today)
                assert stats["mesbak_random_pairs"] == stats_before["mesbak_random_pairs"] + 1
                assert stats["mesbak_random_waiting"] == stats_before["mesbak_random_waiting"]
        finally:
            async with session_pool() as session:
                await session.execute(delete(User).where(User.id.in_(user_ids)))
                await session.commit()
            await engine.dispose()

    asyncio.run(run_test())