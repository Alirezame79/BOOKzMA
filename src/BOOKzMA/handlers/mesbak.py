import re
from datetime import date, time

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.types import User as TgUser
from sqlalchemy.ext.asyncio import AsyncSession

from BOOKzMA import keyboards, texts
from BOOKzMA.constants import MESBAK_PRESET_TIMES
from BOOKzMA.handlers.common import show
from BOOKzMA.repositories import mesbak as mesbak_repo
from BOOKzMA.repositories import users
from BOOKzMA.services.mesbak import (
    completed_days,
    current_streak,
    default_schedule,
    effective_goal,
    is_legacy_default_schedule,
    longest_streak,
)
from BOOKzMA.utils import fa, local_today, parse_time

router = Router()


class SetReminderTime(StatesGroup):
    waiting = State()


async def render_mesbak(
    event: Message | CallbackQuery,
    session: AsyncSession,
    tg: TgUser,
) -> None:
    user = await users.get_or_create(session, tg.id, tg.username, tg.full_name)
    if user.started_at is None:
        await users.mark_started(session, user.id)
    today = local_today(user.timezone)
    profile = await mesbak_repo.get_profile(session, user.id, today)
    if profile is None or not profile.enabled:
        await session.commit()
        await show(event, texts.mesbak_INTRO, keyboards.mesbak_intro_kb())
        return

    goal = effective_goal(
        profile.daily_goal, profile.next_daily_goal, profile.goal_effective_on, today
    )
    records = await mesbak_repo.daily_records(session, user.id)
    days = completed_days(records)
    slots = await mesbak_repo.entries_for_day(session, user.id, today)
    reminders = await mesbak_repo.list_reminders(session, user.id)
    badges = await mesbak_repo.list_badges(session, user.id)
    reminder_pairs = [
        (reminder.slot, reminder.remind_at.strftime("%H:%M"))
        for reminder in reminders
        if reminder.slot <= goal
    ]
    pending_date = (
        profile.goal_effective_on.isoformat()
        if profile.next_daily_goal is not None and profile.goal_effective_on is not None
        else None
    )
    message = texts.mesbak_screen(
        goal,
        len(slots),
        current_streak(days, today),
        longest_streak(days),
        [value for _, value in reminder_pairs],
        profile.next_daily_goal,
        pending_date,
        badges,
    )
    await session.commit()
    await show(
        event,
        message,
        keyboards.mesbak_screen_kb(
            goal,
            reminder_pairs,
            slots,
            today.strftime("%Y%m%d"),
            profile.enabled,
        ),
    )


async def _user_from_callback(
    callback: CallbackQuery, session: AsyncSession
) -> tuple[TgUser, date, int]:
    tg = callback.from_user
    user = await users.get_or_create(session, tg.id, tg.username, tg.full_name)
    return tg, local_today(user.timezone), user.id


@router.message(F.text == "🪥 مسباک")
@router.message(Command("mesbak"))
async def on_menu(message: Message, session: AsyncSession, state: FSMContext) -> None:
    await state.clear()
    if message.from_user:
        await render_mesbak(message, session, message.from_user)


@router.callback_query(F.data == "mesbak:open")
async def on_open(callback: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    await render_mesbak(callback, session, callback.from_user)


@router.callback_query(F.data == "mesbak:choose_goal")
async def on_choose_goal(callback: CallbackQuery, session: AsyncSession) -> None:
    profile = await mesbak_repo.get_profile(session, callback.from_user.id)
    if profile is None or not profile.enabled:
        await callback.answer("اول به بخش مسباک بپیوند.", show_alert=True)
        return
    await callback.answer()
    await show(callback, "هدف روزانه‌ات رو انتخاب کن:", keyboards.mesbak_goal_kb())


async def _configure_from_callback(
    callback: CallbackQuery,
    session: AsyncSession,
    goal: int,
    state: FSMContext | None = None,
) -> None:
    if not 1 <= goal <= 5:
        await callback.answer(texts.INVALID_ACTION, show_alert=True)
        return
    tg, today, user_id = await _user_from_callback(callback, session)
    existing = await mesbak_repo.list_reminders(session, user_id)
    selected = {reminder.slot: reminder.remind_at for reminder in existing}
    profile = await mesbak_repo.get_profile(session, user_id, today)
    if profile is not None:
        current_goal = effective_goal(
            profile.daily_goal,
            profile.next_daily_goal,
            profile.goal_effective_on,
            today,
        )
        current_schedule = [
            reminder.remind_at
            for reminder in existing
            if reminder.slot <= current_goal
        ]
        if is_legacy_default_schedule(current_goal, current_schedule):
            selected = {}
    defaults = default_schedule(goal)
    times = []
    used = set()
    for slot in range(1, goal + 1):
        candidate = selected.get(slot)
        if candidate is None or candidate in used:
            candidate = next(value for value in defaults if value not in used)
        times.append(candidate)
        used.add(candidate)
    await mesbak_repo.configure(session, user_id, goal, times, today)
    await session.commit()
    if state is not None:
        await state.clear()
    await callback.answer(texts.mesbak_JOINED)
    await render_mesbak(callback, session, tg)


@router.callback_query(F.data.startswith("mesbak:join:"))
async def on_join(callback: CallbackQuery, session: AsyncSession) -> None:
    match = re.fullmatch(r"mesbak:join:([1-5])", callback.data or "")
    if match is None:
        await callback.answer(texts.INVALID_ACTION, show_alert=True)
        return
    await _configure_from_callback(callback, session, int(match[1]))


@router.callback_query(F.data.startswith("mesbak:goal:"))
async def on_goal(callback: CallbackQuery, session: AsyncSession) -> None:
    match = re.fullmatch(r"mesbak:goal:([1-5])", callback.data or "")
    if match is None:
        await callback.answer(texts.INVALID_ACTION, show_alert=True)
        return
    profile = await mesbak_repo.get_profile(session, callback.from_user.id)
    if profile is None or not profile.enabled:
        await callback.answer("عضویتت در این بخش فعال نیست.", show_alert=True)
        return
    await _configure_from_callback(callback, session, int(match[1]))


@router.callback_query(F.data.startswith("mesbak:done:"))
async def on_record(callback: CallbackQuery, session: AsyncSession) -> None:
    match = re.fullmatch(r"mesbak:done:(\d{8}):([1-5])", callback.data or "")
    if match is None:
        await callback.answer(texts.INVALID_ACTION, show_alert=True)
        return
    tg, today, user_id = await _user_from_callback(callback, session)
    if match[1] != today.strftime("%Y%m%d"):
        await callback.answer(texts.mesbak_STALE_ACTION, show_alert=True)
        return
    result = await mesbak_repo.record_occurrence(session, user_id, today, int(match[2]))
    await session.commit()
    if result.status == "inactive":
        await callback.answer(texts.mesbak_INACTIVE, show_alert=True)
        return
    if result.status == "invalid_slot":
        await callback.answer(texts.INVALID_ACTION, show_alert=True)
        return
    if result.status == "duplicate":
        await callback.answer(texts.mesbak_DUPLICATE, show_alert=True)
        await render_mesbak(callback, session, tg)
        return
    days = await mesbak_repo.completed_day_set(session, user_id)
    streak = current_streak(days, today)
    badges = (
        await mesbak_repo.award_streak_badges(session, user_id, today, streak)
        if result.day_complete
        else []
    )
    if badges:
        await session.commit()
    response = texts.mesbak_recorded(
        result.completed_count, result.daily_goal, streak, badges
    )
    await callback.answer(response, show_alert=result.day_complete)
    await render_mesbak(callback, session, tg)


@router.callback_query(F.data.startswith("mesbak:time:"))
async def on_time_settings(callback: CallbackQuery, session: AsyncSession) -> None:
    match = re.fullmatch(r"mesbak:time:([1-5])", callback.data or "")
    if match is None:
        await callback.answer(texts.INVALID_ACTION, show_alert=True)
        return
    user = await users.get_or_create(
        session,
        callback.from_user.id,
        callback.from_user.username,
        callback.from_user.full_name,
    )
    today = local_today(user.timezone)
    profile = await mesbak_repo.get_profile(session, user.id, today)
    if profile is None or not profile.enabled:
        await callback.answer(texts.mesbak_INACTIVE, show_alert=True)
        return
    await session.commit()
    reminders = await mesbak_repo.list_reminders(session, callback.from_user.id)
    existing = {item.remind_at.strftime("%H:%M") for item in reminders}
    await callback.answer()
    await show(
        callback,
        f"ساعت نوبت {fa(int(match[1]))} رو انتخاب کن یا ساعت دلخواه بفرست:",
        keyboards.mesbak_time_kb(int(match[1]), existing),
    )


async def _save_time(
    callback: CallbackQuery, session: AsyncSession, slot: int, at: time
) -> None:
    tg, today, user_id = await _user_from_callback(callback, session)
    profile = await mesbak_repo.get_profile(session, user_id, today)
    if profile is None or not profile.enabled:
        await callback.answer(texts.mesbak_INACTIVE, show_alert=True)
        return
    goal = effective_goal(
        profile.daily_goal, profile.next_daily_goal, profile.goal_effective_on, today
    )
    if slot > goal:
        await callback.answer(texts.INVALID_ACTION, show_alert=True)
        return
    reminders = await mesbak_repo.list_reminders(session, user_id)
    if any(item.slot != slot and item.remind_at == at for item in reminders):
        await callback.answer("این ساعت برای نوبت دیگری انتخاب شده.", show_alert=True)
        return
    result = await mesbak_repo.set_reminder_time(session, user_id, slot, at)
    if result == "duplicate":
        await callback.answer("این ساعت برای نوبت دیگری انتخاب شده.", show_alert=True)
        return
    if result != "ok":
        await callback.answer(texts.mesbak_INACTIVE, show_alert=True)
        return
    await session.commit()
    await callback.answer("ساعت یادآوری تغییر کرد ✅")
    await render_mesbak(callback, session, tg)


@router.callback_query(F.data.startswith("mesbak:settime:"))
async def on_preset_time(callback: CallbackQuery, session: AsyncSession) -> None:
    match = re.fullmatch(r"mesbak:settime:([1-5]):(\d{4})", callback.data or "")
    presets = {value.replace(":", "") for value in MESBAK_PRESET_TIMES}
    if match is None or match[2] not in presets:
        await callback.answer(texts.INVALID_ACTION, show_alert=True)
        return
    await _save_time(callback, session, int(match[1]), time(int(match[2][:2]), int(match[2][2:])))


@router.callback_query(F.data.startswith("mesbak:customtime:"))
async def on_custom_time_start(
    callback: CallbackQuery, state: FSMContext
) -> None:
    match = re.fullmatch(r"mesbak:customtime:([1-5])", callback.data or "")
    if match is None:
        await callback.answer(texts.INVALID_ACTION, show_alert=True)
        return
    await state.set_state(SetReminderTime.waiting)
    await state.update_data(slot=int(match[1]))
    await callback.answer()
    await show(
        callback,
        "ساعت جدید رو بفرست؛ مثلاً <code>06:30</code>.",
        keyboards.mesbak_cancel_kb(),
    )


@router.message(SetReminderTime.waiting, F.text)
async def on_custom_time(message: Message, session: AsyncSession, state: FSMContext) -> None:
    at = parse_time(message.text or "")
    if at is None:
        await message.answer(texts.mesbak_BAD_TIME)
        return
    if message.from_user is None:
        return
    data = await state.get_data()
    user = await users.get_or_create(
        session, message.from_user.id, message.from_user.username, message.from_user.full_name
    )
    today = local_today(user.timezone)
    profile = await mesbak_repo.get_profile(session, user.id, today)
    slot = int(data.get("slot", 0))
    if profile is None or not profile.enabled:
        await state.clear()
        await message.answer(texts.mesbak_INACTIVE)
        return
    goal = effective_goal(
        profile.daily_goal, profile.next_daily_goal, profile.goal_effective_on, today
    )
    if not 1 <= slot <= goal:
        await state.clear()
        await message.answer(texts.INVALID_ACTION)
        return
    reminders = await mesbak_repo.list_reminders(session, user.id)
    if any(item.slot != slot and item.remind_at == at for item in reminders):
        await message.answer("این ساعت برای نوبت دیگری انتخاب شده؛ یک ساعت دیگر بفرست.")
        return
    result = await mesbak_repo.set_reminder_time(session, user.id, slot, at)
    if result == "duplicate":
        await message.answer("این ساعت برای نوبت دیگری انتخاب شده؛ یک ساعت دیگر بفرست.")
        return
    if result != "ok":
        await state.clear()
        await message.answer(texts.mesbak_INACTIVE)
        return
    await session.commit()
    await state.clear()
    await render_mesbak(message, session, message.from_user)


@router.callback_query(F.data == "mesbak:exit")
async def on_exit(callback: CallbackQuery, session: AsyncSession) -> None:
    await mesbak_repo.set_enabled(session, callback.from_user.id, False)
    await session.commit()
    await callback.answer(texts.mesbak_EXITED, show_alert=True)
    await render_mesbak(callback, session, callback.from_user)


@router.callback_query(F.data == "mesbak:weekly")
async def on_weekly(callback: CallbackQuery, session: AsyncSession) -> None:
    tg, today, user_id = await _user_from_callback(callback, session)
    profile = await mesbak_repo.get_profile(session, user_id, today)
    if profile is None or not profile.enabled:
        await callback.answer(texts.mesbak_INACTIVE, show_alert=True)
        return
    days = completed_days(await mesbak_repo.daily_records(session, user_id))
    week = [today - date.resolution * offset for offset in range(6, -1, -1)]
    count = sum(day in days for day in week)
    cells = [
        f"{fa(day.month):>2}/{fa(day.day):>2} {'✅' if day in days else '▫️'}"
        for day in week
    ]
    text = texts.mesbak_weekly(
        count, current_streak(days, today), longest_streak(days), cells
    )
    await session.commit()
    await callback.answer()
    await show(callback, text, keyboards.weekly_kb())


@router.callback_query(F.data == "mesbak:monthly")
async def on_monthly(callback: CallbackQuery, session: AsyncSession) -> None:
    tg, today, user_id = await _user_from_callback(callback, session)
    profile = await mesbak_repo.get_profile(session, user_id, today)
    if profile is None or not profile.enabled:
        await callback.answer(texts.mesbak_INACTIVE, show_alert=True)
        return
    days = completed_days(await mesbak_repo.daily_records(session, user_id))
    start = today - date.resolution * 29
    count = sum(start <= day <= today for day in days)
    text = texts.mesbak_monthly(count, current_streak(days, today), longest_streak(days))
    await session.commit()
    await callback.answer()
    await show(callback, text, keyboards.weekly_kb())