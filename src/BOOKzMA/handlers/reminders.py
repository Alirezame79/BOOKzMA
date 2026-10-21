import re
from datetime import time

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.types import User as TgUser
from sqlalchemy.ext.asyncio import AsyncSession

from BOOKzMA import keyboards, texts
from BOOKzMA.constants import PRESET_TIMES, TZ_LABELS
from BOOKzMA.handlers.common import show
from BOOKzMA.repositories import reminders as reminders_repo
from BOOKzMA.repositories import users
from BOOKzMA.utils import parse_time

router = Router()


class AddTime(StatesGroup):
    waiting = State()


async def render_reminders(
    event: Message | CallbackQuery, session: AsyncSession, tg: TgUser
) -> None:
    user = await users.get_or_create(session, tg.id, tg.username)
    await session.commit()
    items = await reminders_repo.list_for_user(session, user.id)
    pairs = [(r.id, r.remind_at.strftime("%H:%M")) for r in items]
    label = TZ_LABELS.get(user.timezone, user.timezone)
    await show(
        event,
        texts.reminders([t for _, t in pairs], label),
        keyboards.reminders_kb(pairs),
    )


@router.message(Command("reminders"))
async def cmd_reminders(message: Message, session: AsyncSession, state: FSMContext) -> None:
    await state.clear()
    if message.from_user:
        await render_reminders(message, session, message.from_user)


@router.callback_query(F.data == "rem")
async def on_reminders(callback: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    await render_reminders(callback, session, callback.from_user)


@router.callback_query(F.data.startswith("rem_add:"))
async def on_preset(callback: CallbackQuery, session: AsyncSession) -> None:
    raw = (callback.data or "").split(":", 1)[1]
    if raw not in {t.replace(":", "") for t in PRESET_TIMES}:
        await callback.answer()
        return
    tg = callback.from_user
    user = await users.get_or_create(session, tg.id, tg.username)
    result = await reminders_repo.add(session, user.id, time(int(raw[:2]), int(raw[2:])))
    await session.commit()
    await callback.answer(texts.ADD_RESULT[result])
    await render_reminders(callback, session, tg)


@router.callback_query(F.data.startswith("rem_del:"))
async def on_delete(callback: CallbackQuery, session: AsyncSession) -> None:
    raw = (callback.data or "").split(":", 1)[1]
    if not re.fullmatch(r"\d+", raw):
        await callback.answer()
        return
    await reminders_repo.delete_one(session, callback.from_user.id, int(raw))
    await session.commit()
    await callback.answer(texts.REMINDER_DELETED)
    await render_reminders(callback, session, callback.from_user)


@router.callback_query(F.data == "rem_custom")
async def on_custom(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AddTime.waiting)
    await callback.answer()
    await show(callback, texts.custom_time(), keyboards.cancel_kb())


@router.message(AddTime.waiting, F.text)
async def on_custom_time(message: Message, session: AsyncSession, state: FSMContext) -> None:
    at = parse_time(message.text or "")
    if at is None:
        await message.answer(texts.BAD_TIME)
        return
    tg = message.from_user
    if tg is None:
        return
    user = await users.get_or_create(session, tg.id, tg.username)
    result = await reminders_repo.add(session, user.id, at)
    await session.commit()
    await state.clear()
    await message.answer(texts.ADD_RESULT[result])
    await render_reminders(message, session, tg)
