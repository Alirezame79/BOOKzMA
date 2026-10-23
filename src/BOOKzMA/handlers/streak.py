from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from BOOKzMA import texts
from BOOKzMA.handlers.common import render_home
from BOOKzMA.repositories import readings, users
from BOOKzMA.repositories import streak_freezes
from BOOKzMA.services.streak import compute_streak
from BOOKzMA.services.streak_freezes import on_read as apply_streak_freeze
from BOOKzMA.utils import local_today

router = Router()


@router.callback_query(F.data == "read")
async def on_read(callback: CallbackQuery, session: AsyncSession) -> None:
    tg = callback.from_user
    user = await users.get_or_create(session, tg.id, tg.username)
    today = local_today(user.timezone)
    created = await readings.mark_read(session, user.id, today)
    freeze_change = None
    if created:
        freeze_change = await apply_streak_freeze(session, user.id, today)
    await session.commit()

    days = await readings.get_days(session, user.id)
    frozen_days = await streak_freezes.used_days(session, user.id)
    toast = texts.read_toast(
        compute_streak(days, today, frozen_days),
        created,
        freeze_used=freeze_change is not None and freeze_change.used_day is not None,
        freeze_earned=freeze_change is not None and freeze_change.earned,
        freeze_balance=await streak_freezes.balance(session, user.id),
    )
    await callback.answer(toast)
    await render_home(callback, session, tg)
