"""رفیق مطالعه (C-06): opt-in، صف خودکار FIFO، تلنگر روزانه و پایان بدون سرزنش."""

import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.types import User as TgUser
from sqlalchemy.ext.asyncio import AsyncSession

from BOOKzMA import keyboards, texts
from BOOKzMA.db.models import User
from BOOKzMA.handlers.common import show
from BOOKzMA.repositories import buddy as buddy_repo
from BOOKzMA.repositories import readings, users
from BOOKzMA.repositories import streak_freezes
from BOOKzMA.services.streak import displayed_streak
from BOOKzMA.utils import local_today

router = Router()
log = logging.getLogger(__name__)


async def render_buddy(event: Message | CallbackQuery, session: AsyncSession, tg: TgUser) -> None:
    user = await users.get_or_create(session, tg.id, tg.username, tg.full_name)
    await session.commit()
    found = await buddy_repo.active_pair(session, user.id)
    if found:
        _pair, buddy_id = found
        buddy = await session.get(User, buddy_id)
        if buddy is not None:
            today = local_today(buddy.timezone)
            buddy_read_today = await readings.has_read(session, buddy.id, today)
            buddy_days = await readings.get_days(session, buddy.id)
            buddy_frozen = await streak_freezes.used_days(session, buddy.id)
            streak = displayed_streak(
                buddy_days,
                today,
                buddy_frozen,
                buddy.comeback_bonus_days,
                buddy.comeback_base_day,
            )
            await show(
                event,
                texts.buddy_screen(texts.buddy_name(buddy.display_name), streak, buddy_read_today),
                keyboards.buddy_pair_kb(),
            )
            return
    if await buddy_repo.is_queued(session, user.id):
        await show(event, texts.BUDDY_WAITING, keyboards.buddy_waiting_kb())
        return
    await show(event, texts.BUDDY_INTRO, keyboards.buddy_intro_kb())


async def _safe_send(bot: Bot, user_id: int, text: str) -> None:
    try:
        await bot.send_message(user_id, text)
    except TelegramAPIError:
        log.info("buddy notification to %s failed", user_id)


@router.message(F.text == "🤝 رفیق مطالعه")
async def on_menu_buddy(message: Message, session: AsyncSession) -> None:
    if message.from_user:
        await render_buddy(message, session, message.from_user)


@router.callback_query(F.data == "buddy:join")
async def on_join(
    callback: CallbackQuery, session: AsyncSession, bot: Bot, state: FSMContext
) -> None:
    await state.clear()
    tg = callback.from_user
    user = await users.get_or_create(session, tg.id, tg.username, tg.full_name)
    await buddy_repo.join_queue(session, user.id)
    partner_id = await buddy_repo.try_match(session, user.id)
    await session.commit()
    my_name = texts.buddy_name(user.display_name)
    if partner_id is None:
        await callback.answer()
        await show(callback, texts.BUDDY_WAITING, keyboards.buddy_waiting_kb())
        return
    partner = await session.get(User, partner_id)
    partner_name = texts.buddy_name(partner.display_name if partner else None)
    if partner is not None:
        await _safe_send(bot, partner.id, texts.BUDDY_MATCHED_PEER.format(name=my_name))
    await callback.answer()
    if isinstance(callback.message, Message):
        await callback.message.answer(texts.BUDDY_MATCHED_SELF.format(name=partner_name))
        await render_buddy(callback.message, session, tg)


@router.callback_query(F.data == "buddy:leave")
async def on_leave(callback: CallbackQuery, session: AsyncSession) -> None:
    await buddy_repo.leave_queue(session, callback.from_user.id)
    await session.commit()
    await callback.answer(texts.BUDDY_LEFT_QUEUE)
    await show(callback, texts.BUDDY_INTRO, keyboards.buddy_intro_kb())


@router.callback_query(F.data == "buddy:nudge")
async def on_nudge(
    callback: CallbackQuery, session: AsyncSession, bot: Bot
) -> None:
    tg = callback.from_user
    user = await users.get_or_create(session, tg.id, tg.username)
    found = await buddy_repo.active_pair(session, user.id)
    if found is None:
        await callback.answer(texts.INVALID_ACTION, show_alert=True)
        return
    pair, buddy_id = found
    today = local_today(user.timezone)
    allowed = await buddy_repo.register_nudge(session, pair, today)
    await session.commit()
    if not allowed:
        await callback.answer(texts.BUDDY_NUDGE_LIMIT)
        return
    await _safe_send(
        bot, buddy_id, texts.NUDGE_PUSH.format(name=texts.buddy_name(user.display_name))
    )
    await callback.answer(texts.BUDDY_NUDGE_SENT)


@router.callback_query(F.data == "buddy:end")
async def on_end(
    callback: CallbackQuery, session: AsyncSession, bot: Bot
) -> None:
    tg = callback.from_user
    user = await users.get_or_create(session, tg.id, tg.username, tg.full_name)
    found = await buddy_repo.active_pair(session, user.id)
    if found is None:
        await callback.answer(texts.INVALID_ACTION, show_alert=True)
        return
    pair, buddy_id = found
    await buddy_repo.end_pair(session, pair, user.id)
    await session.commit()
    await _safe_send(bot, buddy_id, texts.BUDDY_ENDED)
    await callback.answer(texts.BUDDY_ENDED)
    await show(callback, texts.BUDDY_INTRO, keyboards.buddy_intro_kb())
