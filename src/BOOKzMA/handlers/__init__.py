from aiogram import Router

from BOOKzMA.handlers import reminders, start, streak, timezone


def get_router() -> Router:
    # فیچر جدید = یه فایل تو همین پوشه + یه خط اینجا
    router = Router()
    router.include_routers(
        start.router,
        streak.router,
        reminders.router,
        timezone.router,
    )
    return router
