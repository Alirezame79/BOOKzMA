from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from BOOKzMA import texts
from BOOKzMA.handlers.common import render_home
from BOOKzMA.repositories import readings, users
from BOOKzMA.services.streak import compute_streak
from BOOKzMA.utils import local_today

router = Router()


@router.callback_query(F.data == "read")
async def on_read(callback: CallbackQuery, session: AsyncSession) -> None:
    tg = callback.from_user
    user = await users.get_or_create(session, tg.id, tg.username)
    today = local_today(user.timezone)
    created = await readings.mark_read(session, user.id, today)
    await session.commit()

    days = await readings.get_days(session, user.id)
    await callback.answer(texts.read_toast(compute_streak(days, today), created))
    await render_home(callback, session, tg)
