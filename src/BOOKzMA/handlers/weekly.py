from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from BOOKzMA import keyboards, texts
from BOOKzMA.handlers.common import show
from BOOKzMA.repositories import readings, users
from BOOKzMA.services.streak import compute_streak, longest_streak, weekly_summary
from BOOKzMA.utils import local_today

router = Router()


@router.callback_query(F.data == "weekly")
async def on_weekly_summary(callback: CallbackQuery, session: AsyncSession) -> None:
    tg = callback.from_user
    user = await users.get_or_create(session, tg.id, tg.username)
    await session.commit()
    today = local_today(user.timezone)
    days = await readings.get_days(session, user.id)
    summary = weekly_summary(days, today)
    await callback.answer()
    await show(
        callback,
        texts.weekly_summary(
            summary["days_read"], compute_streak(days, today), longest_streak(days)
        ),
        keyboards.weekly_kb(),
    )