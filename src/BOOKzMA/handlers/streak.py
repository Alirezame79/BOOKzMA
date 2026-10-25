from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from BOOKzMA import texts
from BOOKzMA.handlers.common import render_home
from BOOKzMA.repositories import readings, users
from BOOKzMA.repositories import streak_freezes
from BOOKzMA.services.comeback import ComebackState, apply_read
from BOOKzMA.services.streak import displayed_streak
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
    comeback_change = None
    if created:
        freeze_change = await apply_streak_freeze(session, user.id, today)
        new_state, comeback_change = apply_read(
            days=set(await readings.get_days(session, user.id)),
            frozen=set(await streak_freezes.used_days(session, user.id)),
            today=today,
            state=ComebackState(
                bonus_days=user.comeback_bonus_days,
                bonus_base_day=user.comeback_base_day,
                broken_streak_days=user.broken_streak_days,
            ),
        )
        user.broken_streak_days = new_state.broken_streak_days
        user.comeback_bonus_days = new_state.bonus_days
        user.comeback_base_day = new_state.bonus_base_day
    await session.commit()

    days = await readings.get_days(session, user.id)
    frozen_days = await streak_freezes.used_days(session, user.id)
    streak = displayed_streak(
        days, today, frozen_days, user.comeback_bonus_days, user.comeback_base_day
    )
    toast = texts.read_toast(
        streak,
        created,
        freeze_used=freeze_change is not None and freeze_change.used_day is not None,
        freeze_earned=freeze_change is not None and freeze_change.earned,
        freeze_balance=await streak_freezes.balance(session, user.id),
        comeback=texts.comeback_line(comeback_change, streak),
    )
    await callback.answer(toast)
    await render_home(callback, session, tg)
