import logging
import re

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from BOOKzMA import keyboards, texts
from BOOKzMA.config import Settings
from BOOKzMA.handlers.common import show
from BOOKzMA.repositories import analytics, broadcasts
from BOOKzMA.utils import local_today

router = Router()
log = logging.getLogger(__name__)
MAX_BROADCAST_LENGTH = 3500


class NewBroadcast(StatesGroup):
    waiting_for_text = State()


def is_admin(user_id: int, settings: Settings) -> bool:
    return user_id in settings.admin_ids


def _authorize(user_id: int, settings: Settings, action: str) -> bool:
    allowed = is_admin(user_id, settings)
    log.info("admin authorization action=%s actor=%s allowed=%s", action, user_id, allowed)
    return allowed


async def show_admin(event: Message | CallbackQuery, session: AsyncSession) -> None:
    today = local_today("UTC")
    stats = await analytics.dashboard(session, today)
    series = await analytics.activity_series(session, today)
    text = texts.admin_dashboard(stats, series)
    await show(event, text, keyboards.admin_kb())


@router.message(Command("admin"))
@router.message(F.text == "⚙️ مدیریت ربات")
async def on_admin(message: Message, session: AsyncSession, settings: Settings) -> None:
    if not message.from_user or not _authorize(message.from_user.id, settings, "open_panel"):
        await message.answer("این بخش فقط برای مدیر رباته.")
        return
    await show_admin(message, session)


@router.callback_query(F.data == "admin:stats")
async def on_admin_stats(
    callback: CallbackQuery, session: AsyncSession, settings: Settings
) -> None:
    if not _authorize(callback.from_user.id, settings, "view_stats"):
        await callback.answer("دسترسی نداری.", show_alert=True)
        return
    await callback.answer()
    await show_admin(callback, session)


@router.callback_query(F.data == "admin:broadcast")
async def on_broadcast_start(
    callback: CallbackQuery, state: FSMContext, settings: Settings
) -> None:
    if not _authorize(callback.from_user.id, settings, "create_broadcast"):
        await callback.answer("دسترسی نداری.", show_alert=True)
        return
    await state.set_state(NewBroadcast.waiting_for_text)
    await callback.answer()
    if isinstance(callback.message, Message):
        await callback.message.answer(
            "متن پیام همگانی رو بفرست.\n"
            f"حداکثر {MAX_BROADCAST_LENGTH} نویسه؛ قبل از ارسال، پیش‌نمایش و تأیید می‌گیری."
        )


@router.message(NewBroadcast.waiting_for_text, F.text)
async def on_broadcast_text(
    message: Message, session: AsyncSession, state: FSMContext, settings: Settings
) -> None:
    if not message.from_user or not _authorize(message.from_user.id, settings, "draft_broadcast"):
        await state.clear()
        return
    text = message.text or ""
    if not text.strip() or len(text) > MAX_BROADCAST_LENGTH:
        await message.answer("متن خالیه یا از سقف مجاز طولانی‌تره؛ دوباره بفرست.")
        return
    campaign_id, recipient_count = await broadcasts.create(
        session, message.from_user.id, text
    )
    await session.commit()
    await state.clear()
    await message.answer(
        f"پیش‌نمایش پیام همگانی\n\n{text}\n\n"
        f"مخاطب‌ها: {recipient_count}\n"
        "برای شروع ارسال، تأیید کن.",
        reply_markup=keyboards.broadcast_confirm_kb(campaign_id),
        parse_mode=None,
    )


def _campaign_id(callback_data: str, action: str) -> int | None:
    match = re.fullmatch(rf"broadcast:{action}:(\d{{1,10}})", callback_data)
    if match is None:
        return None
    campaign_id = int(match[1])
    return campaign_id if campaign_id <= 2_147_483_647 else None


@router.callback_query(F.data.startswith("broadcast:status:"))
async def on_broadcast_status(
    callback: CallbackQuery, session: AsyncSession, settings: Settings
) -> None:
    if not _authorize(callback.from_user.id, settings, "broadcast_status"):
        await callback.answer("دسترسی نداری.", show_alert=True)
        return
    campaign_id = _campaign_id(callback.data or "", "status")
    campaign = (
        await broadcasts.owned_campaign(session, campaign_id, callback.from_user.id)
        if campaign_id is not None
        else None
    )
    if campaign is None:
        await callback.answer("کمپین پیدا نشد.", show_alert=True)
        return
    counts = await broadcasts.campaign_counts(session, campaign.id)
    total = sum(counts.values())
    summary = (
        f"وضعیت: {campaign.status}\n"
        f"کل: {total} · ارسال‌شده: {counts.get('sent', 0)} · "
        f"در صف: {counts.get('pending', 0) + counts.get('sending', 0)} · "
        f"ناموفق: {counts.get('failed', 0)} · لغوشده: {counts.get('cancelled', 0)}"
    )
    await callback.answer(summary, show_alert=True)


@router.callback_query(F.data.startswith("broadcast:start:"))
async def on_broadcast_confirm(
    callback: CallbackQuery,
    session: AsyncSession,
    settings: Settings,
) -> None:
    if not _authorize(callback.from_user.id, settings, "confirm_broadcast"):
        await callback.answer("دسترسی نداری.", show_alert=True)
        return
    campaign_id = _campaign_id(callback.data or "", "start")
    if campaign_id is None or not await broadcasts.start(
        session, campaign_id, callback.from_user.id
    ):
        await callback.answer(
            "کمپین پیدا نشد، قبلاً تأیید شده یا یک ارسال دیگر در جریانه.",
            show_alert=True,
        )
        return
    await session.commit()
    await callback.answer("ارسال در صف قرار گرفت.")
    if isinstance(callback.message, Message):
        await callback.message.edit_reply_markup(
            reply_markup=keyboards.broadcast_cancel_kb(campaign_id)
        )


@router.callback_query(F.data.startswith("broadcast:cancel:"))
async def on_broadcast_cancel(
    callback: CallbackQuery, session: AsyncSession, settings: Settings
) -> None:
    if not _authorize(callback.from_user.id, settings, "cancel_broadcast"):
        await callback.answer("دسترسی نداری.", show_alert=True)
        return
    campaign_id = _campaign_id(callback.data or "", "cancel")
    if campaign_id is None or not await broadcasts.cancel(
        session, campaign_id, callback.from_user.id
    ):
        await callback.answer("این کمپین پیدا نشد یا تمام شده.", show_alert=True)
        return
    await session.commit()
    await callback.answer("ارسال لغو شد.")
