from BOOKzMA.constants import MAX_REMINDERS, MILESTONES
from BOOKzMA.services.badges import badge_label
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

ONBOARDING_WELCOME = (
    "سلام! 👋 خوش اومدی\n\n"
    "اینجا جاییه که عادت کتاب‌خوندن رو باهم می‌سازیم: هر روز که بخونی ثبتش می‌کنیم، "
    "استریک‌ت بالا می‌ره و یادآور هم یادت نمی‌ذاره.\n\n"
    "برای شروع، اولین یادآور روزانه‌ات رو انتخاب کن:"
)
ONBOARDING_DONE = "یادآورت فعاله ⏰ حالا هر روز سر وقت بهت یادآوری می‌کنم."
ONBOARDING_SKIPPED = "باشه! هر وقت خواستی از منوی «⏰ یادآورها» بذار 🙂"
WELCOME_BACK = (
    "چه خوب که برگشتی! 👋\n"
    "هر چقدر هم غیبت شد، مهم نیست؛ از همین امروز دوباره شروع کنیم."
)
COMEBACK_BROKEN = (
    "😌 استریک {days} روزه‌ات تموم شد؛ اتفاق می‌افده. ولی از دست نرفته:\n"
    "۳ روز پشت‌سرهم بخون تا نصفش پس بگیری 💪"
)
COMEBACK_PROGRESS = "🔁 روز {done} از ۳ برای پس‌گرفتن استریک. ادامه بده!"
COMEBACK_RESTORED = (
    "🎉 آفرین! {added} روز به استریکت برگشت؛ الان {total} روزه‌ای."
)
RISK_ALERT = (
    "⚠️ <b>استریکت در خطره!</b>\n"
    "امروز هنوز نخوندی. همین یه مطالعهٔ کوچیک هم روزت رو نجات می‌ده."
)
BUDDY_INTRO = (
    "🤝 <b>رفیق مطالعه</b>\n\n"
    "می‌تونی دوست خودت رو دعوت کنی یا برای پیدا کردن رفیق ناشناس وارد صف بشی.\n"
    "با هم به همدیگه تلنگر ملایم می‌زنید که امروز بخونید.\n\n"
    "• فقط نام نمایشی‌ات برای رفیقت دیده می‌شه\n"
    "• هر وقت بخوای می‌تونی هم‌یاری رو تمام کنی\n"
    "• تلنگر حداکثر روزی یک‌باره\n\n"
    "آماده‌ای؟"
)
BUDDY_INVITE_READY = (
    "لینک یک‌بارمصرفت آماده است؛ تا ۷ روز اعتبار دارد:\n<code>{link}</code>\n\n"
    "فقط کسی که این لینک را برایش می‌فرستی می‌تواند رفیقت شود."
)
BUDDY_INVITE_ACCEPTED = "🤝 دعوت {name} رو پذیرفتی؛ از «رفیق مطالعه» می‌تونی وضعیتش رو ببینی."
BUDDY_INVITE_PEER_ACCEPTED = "🤝 {name} دعوتت رو پذیرفت و رفیق مطالعه‌ات شد."
BUDDY_INVITE_ALREADY_FRIENDS = "شما از قبل رفیق مطالعهٔ هم هستین 🤝"
BUDDY_INVITE_BUSY = (
    "برای پذیرفتن دعوت، هیچ‌کدام نباید توی صف ناشناس باشین. "
    "لینک هنوز مصرف نشده و بعداً می‌تونی دوباره امتحان کنی."
)
BUDDY_INVITE_UNAVAILABLE = "این لینک معتبر نیست، منقضی شده یا قبلاً استفاده شده."
BUDDY_ALREADY_QUEUED = "اول از صف ناشناس خارج شو، بعد می‌تونی لینک دعوت بسازی."
BUDDY_WAITING = (
    "دنبال رفیق می‌گردیم... 🔍\n"
    "به‌محض پیدا شدن، خبرت می‌کنم. این صفحه رو می‌تونی هر وقت ببینی."
)
BUDDY_LEFT_QUEUE = "انتظار لغو شد."
BUDDY_MATCHED_SELF = "🤝 رفیقت پیدا شد: <b>{name}</b>! از «🤝 رفیق مطالعه» وضعیتش رو دنبال کن."
BUDDY_MATCHED_PEER = "🤝 رفیق جدید پیدا شد: <b>{name}</b>! از «🤝 رفیق مطالعه» شروع کن."
NUDGE_PUSH = "🔔 <b>{name}</b> بهت تلنگر زد: یه گوشه بشین و یه کم بخون!"
BUDDY_NUDGE_SENT = "تلنگر رفت 🔔"
BUDDY_NUDGE_LIMIT = "امروز یه تلنگر زدی؛ فردا دوباره 🙂"
BUDDY_ALREADY_READ = "رفیقت امروز مطالعه‌ش رو ثبت کرده؛ تلنگر براش نفرستادم ✅"
BUDDY_NUDGE_PROMPT = "امروز خوندی 👏 دوست داری به رفیق‌هایی که هنوز نخوندن تلنگر بزنی؟"
BUDDY_ENDED = (
    "هم‌یاری تمام شد. بدون دلخوری؛ هر وقت خواستی دوباره می‌تونی رفیق پیدا کنی 👋"
)


def buddy_screen(name: str, streak: int, read_today: bool) -> str:
    if read_today:
        status = "✅ امروزش رو ثبت کرده"
    else:
        status = "⏳ هنوز امروز نخونده"
    return (
        f"🤝 <b>رفیقت: {name}</b>\n\n"
        f"🔥 استریک: {fa(streak)} روز\n"
        f"{status}\n\n"
        "اگه دیر کرد، یه تلنگر دوستانه بزن."
    )


def buddy_overview(names: list[str], queued: bool) -> str:
    if names:
        friends = "\n".join(
            f"{fa(index)}. <b>{buddy_name(name)}</b>" for index, name in enumerate(names, 1)
        )
        text = f"🤝 <b>رفیق‌های مطالعه‌ات</b>\n\n{friends}"
    else:
        text = "🤝 هنوز رفیق مطالعه‌ای نداری."
    if queued:
        text += "\n\n🔍 توی صف پیدا کردن رفیق ناشناس هستی."
    return text


def buddy_name(display_name: str | None) -> str:
    from html import escape

    return escape((display_name or "کتاب‌خوان").replace("\n", " ").strip() or "کتاب‌خوان")


def buddy_button_name(display_name: str | None) -> str:
    name = (display_name or "کتاب‌خوان").replace("\n", " ").strip() or "کتاب‌خوان"
    return name[:40]


def buddy_nudge_summary(sent: int, already_read: int, already_nudged: int, failed: int) -> str:
    if not sent and not already_read and not already_nudged and not failed:
        return "امروز موردی برای تلنگر نبود."
    parts = []
    if sent:
        parts.append(f"به {fa(sent)} نفر تلنگر رفت")
    if already_read:
        parts.append(f"{fa(already_read)} نفر امروز خوانده بودند")
    if already_nudged:
        parts.append(f"به {fa(already_nudged)} نفر امروز قبلاً تلنگر زده بودی")
    if failed:
        parts.append(f"ارسال به {fa(failed)} نفر انجام نشد")
    return "؛ ".join(parts) + "."


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


def comeback_line(change, total_streak: int) -> str | None:
    if change is None:
        return None
    if change.bonus_added:
        return COMEBACK_RESTORED.format(added=fa(change.bonus_added), total=fa(total_streak))
    if change.broken_days:
        return COMEBACK_BROKEN.format(days=fa(change.broken_days))
    if change.progress_done:
        return COMEBACK_PROGRESS.format(done=fa(change.progress_done))
    return None


def badge_toast(codes: list[str]) -> str | None:
    if not codes:
        return None
    labels = " · ".join(badge_label(code) for code in codes)
    return f"🏅 نشان جدید گرفتی: {labels}"


def read_toast(
    streak: int,
    created: bool,
    freeze_used: bool = False,
    freeze_earned: bool = False,
    freeze_balance: int = 0,
    comeback: str | None = None,
    badges: list[str] | None = None,
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
    if comeback:
        message += f"\n{comeback}"
    badge_line = badge_toast(badges or [])
    if badge_line:
        message += f"\n{badge_line}"
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


def profile(streak: int, best: int, freeze_balance: int, opted_out: bool, badges: list[str]) -> str:
    participation = "خاموش" if opted_out else "روشن"
    if badges:
        badges_line = " · ".join(badge_label(code) for code in badges)
    else:
        badges_line = "هنوز نشانی نداری؛ اولین مطالعه اولین نشانته ⭐"
    return (
        "👤 <b>پروفایل من</b>\n\n"
        f"🔥 استریک فعلی: {fa(streak)} روز\n"
        f"🏆 بهترین استریک: {fa(best)} روز\n"
        f"🛡️ فریزهای موجود: {fa(freeze_balance)}/{fa(MAX_STREAK_FREEZES)}\n"
        f"🏅 حضور در لیدربورد: {participation}\n\n"
        f"🎖 نشان‌ها: {badges_line}"
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
        f"🎓 آنبردینگ کامل‌شده: {fa(stats['onboarded'])}\n"
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
        f"⚠️ هشدار «استریک در خطر» در ۷ روز: {fa(stats['streak_alerts_7d'])}\n"
        f"🔁 کاربران با پاداش comeback: {fa(stats['comeback_users'])}\n"
        f"🎖 نشان‌ها: {fa(stats['badges_total'])} اهدا به {fa(stats['badge_holders'])} نفر\n"
        f"🤝 جفت‌های رفیق مطالعه: {fa(stats['buddy_pairs_active'])} فعال · "
        f"{fa(stats['buddy_pairs_total'])} کل\n"
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
