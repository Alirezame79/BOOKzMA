from datetime import datetime, timezone

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from BOOKzMA import keyboards, texts
from BOOKzMA.config import Settings
from BOOKzMA.handlers.common import render_home
from BOOKzMA.middlewares.membership import missing_channels
from BOOKzMA.repositories import activity, users

router = Router()


@router.message(CommandStart())
async def cmd_start(
    message: Message, session: AsyncSession, state: FSMContext, settings: Settings
) -> None:
    await state.clear()
    if message.from_user:
        await render_home(message, session, message.from_user)
        await message.answer(
            "از منوی پایین استفاده کن.",
            reply_markup=keyboards.menu_kb(message.from_user.id in settings.admin_ids),
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
async def on_check_join(callback: CallbackQuery, bot: Bot, session: AsyncSession) -> None:
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
    await callback.answer(texts.JOINED)
    await render_home(callback, session, callback.from_user)
