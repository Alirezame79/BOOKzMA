from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from BOOKzMA.constants import DELETE_REASONS, MAX_REMINDERS, PRESET_TIMES, TIMEZONES


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


def menu_kb(is_admin: bool = False) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="🏠 خانه"), KeyboardButton(text="👤 پروفایل")],
        [KeyboardButton(text="⏰ یادآورها"), KeyboardButton(text="🌍 منطقه زمانی")],
        [KeyboardButton(text="💚 حمایت از پروژه")],
    ]
    if is_admin:
        rows.append([KeyboardButton(text="⚙️ مدیریت ربات")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def profile_kb(opt_out: bool) -> InlineKeyboardMarkup:
    toggle_text = "➖ خروج از لیدربورد" if not opt_out else "➕ حضور در لیدربورد"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [_btn(toggle_text, "leaderboard:toggle")],
            [_btn("🏅 لیدربورد استریک", "leaderboard")],
            [_btn("🗑 حذف حساب", "account_del:start")],
            [_btn("🏠 منوی اصلی", "home")],
        ]
    )


def account_delete_warn_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [_btn("ادامه می‌دم", "account_del:why")],
            [_btn("🔙 انصراف", "account_del:cancel")],
        ]
    )


def account_delete_reasons_kb() -> InlineKeyboardMarkup:
    buttons = [
        _btn(label, f"account_del:reason:{i}") for i, (_code, label) in enumerate(DELETE_REASONS)
    ]
    rows = _chunk(buttons, 2)
    rows.append([_btn("🔙 انصراف", "account_del:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def account_delete_type_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[_btn("🔙 انصراف", "account_del:cancel")]])


def account_delete_final_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [_btn("بله، همه‌چیز پاک شود", "account_del:go")],
            [_btn("🔙 انصراف", "account_del:cancel")],
        ]
    )


def restore_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[_btn("شروع", "account_restore")]])


def support_kb(github_url: str, support_url: str) -> InlineKeyboardMarkup:
    rows = []
    if github_url:
        rows.append([InlineKeyboardButton(text="⭐ گیت‌هاب پروژه", url=github_url)])
    if support_url:
        rows.append([InlineKeyboardButton(text="💌 حمایت مالی", url=support_url)])
    rows.append([_btn("🏠 منوی اصلی", "home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def admin_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [_btn("📊 آمار بات", "admin:stats")],
            [_btn("📣 پیام همگانی", "admin:broadcast")],
        ]
    )


def broadcast_confirm_kb(campaign_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [_btn("✅ تأیید و شروع", f"broadcast:start:{campaign_id}")],
            [_btn("لغو", f"broadcast:cancel:{campaign_id}")],
        ]
    )


def broadcast_cancel_kb(campaign_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [_btn("📊 وضعیت ارسال", f"broadcast:status:{campaign_id}")],
            [_btn("⏹ لغو ارسال", f"broadcast:cancel:{campaign_id}")],
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


def onboarding_time_kb() -> InlineKeyboardMarkup:
    presets = [_btn(f"⏰ {t}", f"onb:{t.replace(':', '')}") for t in PRESET_TIMES]
    rows = _chunk(presets, 2)
    rows.append([_btn("فعلاً نه", "onb:skip")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
