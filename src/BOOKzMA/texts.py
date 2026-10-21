from BOOKzMA.constants import MAX_REMINDERS, MILESTONES
from BOOKzMA.utils import fa

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


def home(streak: int, best: int, strip: str, read_today: bool) -> str:
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
        "۷ روز اخیر (آخری = امروز):\n"
        f"{strip}\n\n"
        f"{status}"
    )


def read_toast(streak: int, created: bool) -> str:
    if not created:
        return ALREADY_READ
    if streak in MILESTONES:
        return f"🎉 {fa(streak)} روز پشت‌سرهم! عالیه 🔥"
    if streak == 1:
        return "شروع خوبیه! استریک ۱ روزه 🔥"
    return f"🔥 {fa(streak)} روز پشت‌سرهم، ادامه بده"


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


def reminder_push(streak: int) -> str:
    if streak:
        return (
            "⏰ <b>وقت مطالعه‌ست!</b>\n"
            f"🔥 استریک {fa(streak)} روزه‌ات منتظرته، امروز هم ادامه بده."
        )
    return "⏰ <b>وقت مطالعه‌ست!</b>\nامروز یه استریک جدید شروع کن 🔥"
