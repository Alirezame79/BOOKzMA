import asyncio
import os
import random
from datetime import date

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from BOOKzMA.api import Identity, _create_access_token, create_app
from BOOKzMA.config import Settings
from BOOKzMA.db.models import DeletedAccount, ReadingLog, User
from BOOKzMA.repositories.readings import mark_read

BOT_TOKEN = "test-bot-token"
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


def test_delete_me_route_is_documented_in_schema():
    settings = Settings(bot_token=SecretStr(BOT_TOKEN))
    schema = create_app(settings, run_bot=False).openapi()

    assert "delete" in schema["paths"]["/api/v1/me"]


@pytest.mark.skipif(
    not TEST_DATABASE_URL, reason="TEST_DATABASE_URL must point to a disposable PostgreSQL database"
)
def test_delete_me_removes_account_and_blocks_existing_token():
    async def run_test() -> None:
        engine = create_async_engine(TEST_DATABASE_URL)
        session_pool = async_sessionmaker(engine, expire_on_commit=False)
        user_id = 5_000_000_000_000_000_000 + random.randrange(1_000_000_000)
        settings = Settings(bot_token=SecretStr(BOT_TOKEN), database_url=TEST_DATABASE_URL)
        headers = {
            "Authorization": "Bearer "
            + _create_access_token(Identity(id=user_id, username="reader"), BOT_TOKEN)
        }
        try:
            async with session_pool.begin() as session:
                session.add(User(id=user_id))
                await mark_read(session, user_id, date(2026, 10, 20))

            with TestClient(create_app(settings, run_bot=False, run_migrations=False)) as client:
                assert client.get("/api/v1/me", headers=headers).status_code == 200
                assert client.delete("/api/v1/me", headers=headers).status_code == 204
                # توکن هنوز از نظر امضا معتبر است، ولی حساب حذف شده
                assert client.get("/api/v1/me", headers=headers).status_code == 401

            async with session_pool() as session:
                assert (
                    await session.scalar(
                        select(func.count())
                        .select_from(ReadingLog)
                        .where(ReadingLog.user_id == user_id)
                    )
                    == 0
                )
                assert (
                    await session.scalar(
                        select(func.count()).select_from(User).where(User.id == user_id)
                    )
                    == 0
                )
                tombstone = await session.scalar(
                    select(DeletedAccount.reason).where(DeletedAccount.user_id == user_id)
                )
                assert tombstone is None  # حذف از API بدون دلیل ثبت می‌شود
        finally:
            async with session_pool() as session:
                await session.execute(delete(User).where(User.id == user_id))
                await session.execute(
                    delete(DeletedAccount).where(DeletedAccount.user_id == user_id)
                )
                await session.commit()
            await engine.dispose()

    asyncio.run(run_test())
