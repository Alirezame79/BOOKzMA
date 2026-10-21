from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.types import User as TgUser
from sqlalchemy.ext.asyncio import AsyncSession

from BOOKzMA import keyboards, texts
from BOOKzMA.repositories import readings, users
from BOOKzMA.services.streak import compute_streak, longest_streak, week_strip
from BOOKzMA.utils import local_today


async def show(event: Message | CallbackQuery, text: str, kb: InlineKeyboardMarkup) -> None:
    """دکمه‌ها پیام قبلی رو ویرایش می‌کنن، پیام جدید رو می‌فرستیم"""
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
        return
    if isinstance(event.message, Message):
        try:
            await event.message.edit_text(text, reply_markup=kb)
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise


async def render_home(event: Message | CallbackQuery, session: AsyncSession, tg: TgUser) -> None:
    user = await users.get_or_create(session, tg.id, tg.username)
    await session.commit()
    today = local_today(user.timezone)
    days = set(await readings.get_days(session, user.id))
    read_today = today in days
    text = texts.home(
        compute_streak(days, today), longest_streak(days), week_strip(days, today), read_today
    )
    await show(event, text, keyboards.home_kb(read_today))
