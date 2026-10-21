from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from BOOKzMA import keyboards, texts
from BOOKzMA.handlers.common import render_home
from BOOKzMA.middlewares.membership import missing_channels

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, state: FSMContext) -> None:
    await state.clear()
    if message.from_user:
        await render_home(message, session, message.from_user)


@router.callback_query(F.data == "home")
async def on_home(callback: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    await render_home(callback, session, callback.from_user)


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
    await callback.answer(texts.JOINED)
    await render_home(callback, session, callback.from_user)
