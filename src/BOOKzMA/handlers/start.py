from datetime import date, datetime, timezone

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from BOOKzMA import keyboards, texts
from BOOKzMA.config import Settings
from BOOKzMA.handlers.common import render_home
from BOOKzMA.handlers.onboarding import start_onboarding
from BOOKzMA.middlewares.membership import missing_channels
from BOOKzMA.repositories import activity, readings, users
from BOOKzMA.utils import local_today

router = Router()

WELCOME_BACK_AFTER_DAYS = 7


def is_returning_reader(last_read: date | None, today: date) -> bool:
    """کاربر قبلاً مطالعه داشته ولی بیش از یک هفته غیبت کرده."""
    return last_read is not None and (today - last_read).days > WELCOME_BACK_AFTER_DAYS


@router.message(CommandStart())
async def cmd_start(
    message: Message, session: AsyncSession, state: FSMContext, settings: Settings
) -> None:
    await state.clear()
    if message.from_user:
        tg = message.from_user
        user = await users.get_or_create(session, tg.id, tg.username, tg.full_name)
        await session.commit()
        if user.onboarded_at is None:
            await start_onboarding(message, session, state)
            return
        today = local_today(user.timezone)
        if is_returning_reader(await readings.last_read_day(session, user.id), today):
            await message.answer(texts.WELCOME_BACK)
        await render_home(message, session, tg)
        await message.answer(
            "از منوی پایین استفاده کن.",
            reply_markup=keyboards.menu_kb(tg.id in settings.admin_ids),
        )


@router.callback_query(F.data == "home")
async def on_home(callback: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    await render_home(callback, session, callback.from_user)


@router.message(F.text == "🏠 خانه")
async def on_menu_home(message: Message, session: AsyncSession) -> None:
    if message.from_user:
        await render_home(message, session, message.from_user)


@router.callback_query(F.data == "check_join")
async def on_check_join(
    callback: CallbackQuery, bot: Bot, session: AsyncSession, state: FSMContext
) -> None:
    missing = await missing_channels(bot, callback.from_user.id)
    if missing:
        await callback.answer(texts.NOT_JOINED, show_alert=True)
        if isinstance(callback.message, Message):
            try:
                await callback.message.edit_text(
                    texts.JOIN_GATE, reply_markup=keyboards.join_kb(missing)
                )
            except TelegramBadRequest:
                pass
        return
    user = await users.get_or_create(
        session,
        callback.from_user.id,
        callback.from_user.username,
        callback.from_user.full_name,
    )
    await activity.record_interaction(session, user.id, datetime.now(timezone.utc).date())
    if user.onboarded_at is None:
        await callback.answer(texts.JOINED)
        if isinstance(callback.message, Message):
            await start_onboarding(callback.message, session, state)
            return
        await render_home(callback, session, callback.from_user)
        return
    await callback.answer(texts.JOINED)
    await render_home(callback, session, callback.from_user)
