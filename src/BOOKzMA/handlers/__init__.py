from aiogram import Router

from BOOKzMA.handlers import (
    account,
    admin,
    buddy,
    onboarding,
    profile,
    reminders,
    start,
    streak,
    timezone,
    weekly,
)


def get_router() -> Router:
    # فیچر جدید = یه فایل تو همین پوشه + یه خط اینجا
    router = Router()
    router.include_routers(
        start.router,
        onboarding.router,
        admin.router,
        account.router,
        buddy.router,
        profile.router,
        streak.router,
        reminders.router,
        timezone.router,
        weekly.router,
    )
    return router
