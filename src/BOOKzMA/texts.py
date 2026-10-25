from BOOKzMA.constants import MAX_REMINDERS, MILESTONES
from BOOKzMA.services.backup import BackupInfo
from BOOKzMA.utils import fa

MAX_STREAK_FREEZES = 2
JOIN_GATE = "برای استفاده از ربات باید عضو کانال‌های زیر باشی. عضو که شدی دکمه «عضو شدم» رو بزن:"
JOIN_FIRST = "اول باید عضو کانال‌ها بشی 🙂"
NOT_JOINED = "هنوز عضو همه کانال‌ها نیستی 🙂"
JOINED = "عضویتت تایید شد ✅"

ADD_RESULT = {
    "ok": "یادآور اضافه شد ✅",
    "dup": "این ساعت رو قبلاً گذاشتی 🙂",
    "limit": "به سقف تعداد یادآورها رسیدی، اول یکی رو حذف کن.",
}
REMINDER_DELETED = "حذف شد 🗑"
BAD_TIME = "فرمت ساعت درست نیست 🤔 مثلاً <code>21:30</code> بفرست."
ALREADY_READ = "امروز رو قبلاً ثبت کردی ✅"

ACCOUNT_DELETE_WARN = (
    "🗑 <b>حذف حساب</b>\n\n"
    "با حذف حساب، همه‌چیز برای همیشه پاک می‌شه:\n"
    "• استریک و رکوردت\n"
    "• فریزها و روزهای مطالعه\n"
    "• یادآورها و حضورت در لیدربورد\n\n"
    "این کار برگشت‌پذیر نیست. فقط این نکته رو بدون که اطلاعات ممکنه تا وقتی بکاپ‌های قدیمی "
    "پاک بشن، توی همون بکاپ‌ها بمونن.\n\n"
    "مطمئنی ادامه بدی؟"
)
ACCOUNT_DELETE_WHY = "قبل از حذف، بگو چرا می‌خوای بری؟ راستش برای بهتر شدن ربات بهش نیاز داریم 🌱"
ACCOUNT_DELETE_TYPE = (
    "قراره همه‌چیز پاک بشه. اگه هنوز مطمئنی، برای تأیید کلمهٔ <code>حذف</code> رو بنویس و بفرست."
)
ACCOUNT_DELETE_BAD_WORD = (
    "کلمهٔ تأیید درست نیست. فقط کافیه <code>حذف</code> رو بنویسی، یا با دکمهٔ پایین منصرف شو."
)
ACCOUNT_DELETE_FINAL = (
    "آخرین قدم! با زدن دکمهٔ زیر، حسابت و تمام داده‌هات بدون راه برگشت پاک می‌شه."
)
ACCOUNT_DELETED_DONE = (
    "حسابت همراه با همهٔ داده‌هاش پاک شد. 🌙\n"
    "امیدواریم دوباره ببینیمت؛ هر وقت خواستی برگرد."
)
ACCOUNT_DELETE_CANCELLED = "باشه، حذف لغو شد. خوشحالیم که هنوز اینجایی 🙂"
# پیام خنثی برای کاربر سنگ‌قبری؛ نباید به وجود حساب قبلی اشاره کند
ACCOUNT_DELETED_NOTICE = "برای شروع، دکمهٔ زیر رو بزن 👋"
ACCOUNT_RESTORED = "شروع شد! 📚"
INVALID_ACTION = "این دکمه دیگه معتبر نیست. دوباره امتحان کن 🙏"
RATE_LIMITED = "آروم‌تر 🙂 چند لحظه صبر کن و بعد دوباره امتحان کن."

BACKUP_NONE = "هنوز هیچ بکاپی ثبت نشده. با دکمهٔ «بکاپ جدید» یکی بگیر."
BACKUP_MENU_TITLE = "💾 <b>بکاپ دیتابیس</b>\n"
RESTORE_WORD = "بازیابی"


def _fa_size(size_bytes: int) -> str:
    if size_bytes >= 1024 * 1024:
        return f"{fa(round(size_bytes / 1024 / 1024))} مگابایت"
    return f"{fa(max(1, round(size_bytes / 1024)))} کیلوبایت"


def backup_status(backups: list[BackupInfo]) -> str:
    if not backups:
        return BACKUP_MENU_TITLE + "\n" + BACKUP_NONE
    newest = backups[0]
    lines = [
        BACKUP_MENU_TITLE,
        f"آخرین بکاپ: <code>{newest.name}</code>",
        f"حجم: {_fa_size(newest.size_bytes)}",
        f"تعداد بکاپ‌های محلی: {fa(len(backups))}",
    ]
    return "\n".join(lines)


def backup_list(backups: list[BackupInfo]) -> str:
    lines = [BACKUP_MENU_TITLE, "بکاپ‌های موجود:", ""]
    for info in backups:
        lines.append(f"• <code>{info.name}</code> ({_fa_size(info.size_bytes)})")
    lines.append("")
    lines.append("برای بازگردانی، یکی رو انتخاب کن.")
    return "\n".join(lines)


def restore_warn(name: str) -> str:
    return (
        f"♻️ <b>بازگردانی از بکاپ</b>\n\n"
        f"فایل: <code>{name}</code>\n\n"
        "⚠️ با این کار <b>همهٔ داده‌های فعلی</b> (استریک‌ها، مطالعه‌ها، یادآورها و حساب‌های جدید) "
        "با محتوای همین بکاپ جایگزین می‌شن و برنمی‌گردن.\n\n"
        "اگه مطمئنی، اول با «بکاپ جدید» از وضعیت الان نسخه بگیر، بعد ادامه بده."
    )


RESTORE_CONFIRM = (
    "برای تأیید بازگردانی، کلمهٔ <code>بازیابی</code> رو بنویس و بفرست.\n"
    "با دکمهٔ پایین می‌تونی منصرف شی."
)
RESTORE_BAD_WORD = (
    "کلمهٔ تأیید درست نبود. فقط کافیه <code>بازیابی</code> رو بنویسی، یا منصرف شی."
)
RESTORE_RUNNING = "⏳ در حال بازگردانی… ممکنه چند ثانیه طول بکشه."
RESTORE_DONE = (
    "✅ بازگردانی انجام شد.\n\n"
    "برای اعمال کامل، روی سرور <code>docker compose restart bot</code> رو اجرا کن."
)
BACKUP_RUNNING = "⏳ در حال گرفتن بکاپ…"
BACKUP_FAILED = "❌ گرفتن بکاپ ناموفق بود. جزئیات در لاگ سرور."
RESTORE_FAILED = "❌ بازگردانی ناموفق بود. جزئیات در لاگ سرور."


def backup_done(name: str, size_bytes: int) -> str:
    return f"✅ بکاپ گرفته شد: <code>{name}</code>\nحجم: {_fa_size(size_bytes)}"


def admin_backup_hint() -> str:
    return "بکاپ روزانهٔ خودکار ساعت ۳:۳۰ با cron سرور انجام می‌شه؛ این بخش برای کار دستیه."


def home(streak: int, best: int, strip: str, read_today: bool, freeze_balance: int) -> str:
    if streak:
        streak_line = f"🔥 <b>{fa(streak)}</b> روز پشت‌سرهم"
    else:
        streak_line = "🔥 هنوز استریکی نداری"

    if read_today:
        status = "✅ مطالعه‌ی امروزت ثبت شده، آفرین!"
    elif streak:
        status = f"⏳ برای اینکه استریک {fa(streak)} روزه‌ات نسوزه، امروز هم بخون."
    else:
        status = "⏳ امروز هنوز نخوندی. همین الان یه استریک جدید شروع کن!"

    return (
        "📚 <b>کتابخونه مرجع</b>\n\n"
        f"{streak_line}\n"
        f"🏆 رکورد: {fa(best)} روز\n\n"
        f"🛡️ فریز استریک: {fa(freeze_balance)} از {fa(MAX_STREAK_FREEZES)}\n\n"
        "۷ روز اخیر (آخری = امروز):\n"
        f"{strip}\n\n"
        f"{status}"
    )


def read_toast(
    streak: int,
    created: bool,
    freeze_used: bool = False,
    freeze_earned: bool = False,
    freeze_balance: int = 0,
) -> str:
    if not created:
        return ALREADY_READ
    if streak in MILESTONES:
        message = f"🎉 {fa(streak)} روز پشت‌سرهم! عالیه 🔥"
    elif streak == 1:
        message = "شروع خوبیه! استریک ۱ روزه 🔥"
    else:
        message = f"🔥 {fa(streak)} روز پشت‌سرهم، ادامه بده"
    if freeze_used:
        message += "\n🛡️ فریزت دیروز رو پوشش داد و استریکت حفظ شد."
    if freeze_earned:
        message += (
            f"\n🎁 یک فریز جایزه گرفتی؛ موجودی: "
            f"{fa(freeze_balance)}/{fa(MAX_STREAK_FREEZES)}"
        )
    return message


def reminders(times: list[str], tz_label: str) -> str:
    listing = "\n".join(f"• {t}" for t in times) if times else "هنوز یادآوری نداری."
    return (
        "⏰ <b>یادآورها</b>\n\n"
        f"هر روز سر این ساعت‌ها بهت پیام می‌دم (به وقت {tz_label}):\n\n"
        f"{listing}\n\n"
        f"حداکثر {fa(MAX_REMINDERS)} تا یادآور می‌تونی داشته باشی."
    )


def custom_time() -> str:
    return (
        "ساعت دلخواهت رو بفرست، مثلاً <code>21:30</code> یا <code>۷:۴۵</code>.\n"
        "(ساعت ۲۴ ساعته و به وقت منطقه زمانی خودت)"
    )


def timezone(tz_label: str) -> str:
    return (
        "🌍 <b>منطقه زمانی</b>\n\n"
        f"الان: {tz_label}\n"
        "یادآورها و «امروز» بر اساس همین حساب می‌شن."
    )


def weekly_summary(days_read: int, streak: int, best: int, freeze_balance: int) -> str:
    return (
        "📊 <b>خلاصهٔ ۷ روز اخیر</b>\n\n"
        f"📚 روزهای مطالعه: {fa(days_read)} از ۷\n"
        f"🔥 استریک فعلی: {fa(streak)} روز\n"
        f"🏆 بهترین استریک: {fa(best)} روز\n"
        f"🛡️ فریزهای موجود: {fa(freeze_balance)}/{fa(MAX_STREAK_FREEZES)}"
    )


def profile(streak: int, best: int, freeze_balance: int, opted_out: bool) -> str:
    participation = "خاموش" if opted_out else "روشن"
    return (
        "👤 <b>پروفایل من</b>\n\n"
        f"🔥 استریک فعلی: {fa(streak)} روز\n"
        f"🏆 بهترین استریک: {fa(best)} روز\n"
        f"🛡️ فریزهای موجود: {fa(freeze_balance)}/{fa(MAX_STREAK_FREEZES)}\n"
        f"🏅 حضور در لیدربورد: {participation}"
    )


def support() -> str:
    return (
        "💚 <b>حمایت از پروژه</b>\n\n"
        "با ستاره‌دادن به پروژه در گیت‌هاب یا پیام خصوصی برای دریافت راهنمای حمایت مالی با Gram، "
        "به ادامهٔ توسعه کمک کن."
    )


def admin_dashboard(stats: dict[str, int], series: list[tuple[object, int]]) -> str:
    maximum = max((count for _, count in series), default=0)
    chart = []
    for day, count in series:
        width = round(count / maximum * 10) if maximum else 0
        chart.append(f"{day:%m/%d} {'█' * width or '·'} {fa(count)}")
    return (
        "📊 <b>گزارش بات (UTC)</b>\n\n"
        f"👤 کاربران ثبت‌شده: {fa(stats['users'])}\n"
        f"🚀 شروع‌کننده‌ها: {fa(stats['starters'])}\n"
        f"🆕 شروع در ۷/۳۰ روز: {fa(stats['starts_7d'])} / {fa(stats['starts_30d'])}\n"
        f"🟢 فعال روزانه/هفتگی/ماهانه: "
        f"{fa(stats['dau'])} / {fa(stats['wau'])} / {fa(stats['mau'])}\n"
        f"⚪ شروع‌کنندهٔ غیرفعال در ۳۰ روز: {fa(stats['inactive_30d'])}\n"
        f"📚 مطالعه‌کننده در ۷/۳۰ روز: "
        f"{fa(stats['readers_7d'])} / {fa(stats['readers_30d'])}\n"
        f"📖 روزهای ثبت مطالعه در ۷/۳۰ روز: "
        f"{fa(stats['reading_days_7d'])} / {fa(stats['reading_days_30d'])}\n"
        f"🔁 بازگشت D1/D7/D30: {fa(stats['retention_d1'])}% / "
        f"{fa(stats['retention_d7'])}% / {fa(stats['retention_d30'])}%\n"
        f"🔥 دارای استریک: {fa(stats['users_with_streak'])} · "
        f"بیشترین جاری/رکورد: {fa(stats['max_current_streak'])} / "
        f"{fa(stats['max_record_streak'])} روز\n"
        f"⏰ یادآورها: {fa(stats['reminders'])}\n"
        f"🛡️ فریزهای مصرف‌شده: {fa(stats['freezes_used'])}\n"
        f"🗑 حساب حذف‌شده: {fa(stats['accounts_deleted'])} · ۷ روز اخیر: "
        f"{fa(stats['deletions_7d'])}\n\n"
        "<b>فعالیت ۷ روز اخیر</b>\n" + "\n".join(chart)
    )


def reminder_push(streak: int) -> str:
    if streak:
        return (
            "⏰ <b>وقت مطالعه‌ست!</b>\n"
            f"🔥 استریک {fa(streak)} روزه‌ات منتظرته، امروز هم ادامه بده."
        )
    return "⏰ <b>وقت مطالعه‌ست!</b>\nامروز یه استریک جدید شروع کن 🔥"
