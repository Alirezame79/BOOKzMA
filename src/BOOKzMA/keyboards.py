from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from BOOKzMA.constants import MAX_REMINDERS, PRESET_TIMES, TIMEZONES


def _btn(text: str, data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=data)


def _chunk(items: list, size: int) -> list[list]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def join_kb(missing: list[str]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f"عضویت در {ch}", url=f"https://t.me/{ch.lstrip('@')}")]
        for ch in missing
    ]
    rows.append([_btn("✅ عضو شدم", "check_join")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def home_kb(read_today: bool) -> InlineKeyboardMarkup:
    read_text = "✅ امروز ثبت شد" if read_today else "📖 امروز خوندم"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [_btn(read_text, "read")],
            [_btn("📊 خلاصهٔ هفتگی", "weekly")],
            [_btn("⏰ یادآورها", "rem"), _btn("🌍 منطقه زمانی", "tz")],
        ]
    )


def reminders_kb(items: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    """items: لیست (id, "HH:MM")"""
    existing = {t for _, t in items}
    rows: list[list[InlineKeyboardButton]] = []
    if items:
        rows.extend(_chunk([_btn(f"🗑 {t}", f"rem_del:{rid}") for rid, t in items], 3))
    if len(items) < MAX_REMINDERS:
        presets = [
            _btn(f"➕ {t}", f"rem_add:{t.replace(':', '')}")
            for t in PRESET_TIMES
            if t not in existing
        ]
        rows.extend(_chunk(presets, 3))
        rows.append([_btn("✏️ ساعت دلخواه", "rem_custom")])
    rows.append([_btn("🔙 برگشت", "home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[_btn("🔙 انصراف", "rem")]])


def timezone_kb() -> InlineKeyboardMarkup:
    buttons = [_btn(label, f"tz_set:{i}") for i, (label, _) in enumerate(TIMEZONES)]
    rows = _chunk(buttons, 2)
    rows.append([_btn("🔙 برگشت", "home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def reminder_push_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[_btn("📖 امروز خوندم", "read"), _btn("🏠 منو", "home")]]
    )


def weekly_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[_btn("🔙 برگشت", "home")]])
