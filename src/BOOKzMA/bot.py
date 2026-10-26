import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.base import BaseSession
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError
from aiogram.types import BotCommand, BotCommandScopeChat

from BOOKzMA.config import Settings
from BOOKzMA.handlers import get_router
from BOOKzMA.middlewares.db import DbSessionMiddleware
from BOOKzMA.middlewares.membership import MembershipMiddleware
from BOOKzMA.services.scheduler import reminder_loop
from BOOKzMA.services.broadcast import broadcast_loop
from BOOKzMA.services.risk_alert import risk_alert_loop

log = logging.getLogger(__name__)

COMMANDS = [
    BotCommand(command="start", description="منوی اصلی و استریک"),
    BotCommand(command="reminders", description="یادآورهای مطالعه"),
    BotCommand(command="timezone", description="منطقه زمانی"),
    BotCommand(command="profile", description="پروفایل و استریک من"),
    BotCommand(command="support", description="حمایت از پروژه"),
]
ADMIN_COMMANDS = [*COMMANDS, BotCommand(command="admin", description="مدیریت ربات")]


async def start_bot(
    settings: Settings,
    session_pool,
    bot_session: BaseSession | None = None,
) -> tuple[Bot, list[asyncio.Task]]:
    bot = Bot(
        token=settings.bot_token.get_secret_value(),
        session=bot_session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()
    membership = MembershipMiddleware(settings.admin_ids)
    dp.update.outer_middleware(DbSessionMiddleware(session_pool))
    dp.message.outer_middleware(membership)
    dp.callback_query.outer_middleware(membership)
    dp.workflow_data["settings"] = settings
    dp.include_router(get_router())

    reminders_task = asyncio.create_task(reminder_loop(bot, session_pool))
    broadcast_task = asyncio.create_task(broadcast_loop(bot, session_pool))
    risk_alert_task = asyncio.create_task(risk_alert_loop(bot, session_pool))
    try:
        await bot.set_my_commands(COMMANDS)
        for admin_id in settings.admin_ids:
            await bot.set_my_commands(
                ADMIN_COMMANDS, scope=BotCommandScopeChat(chat_id=admin_id)
            )
    except TelegramAPIError as exc:
        log.warning("set_my_commands failed (%s), continuing", type(exc).__name__)
    polling_task = asyncio.create_task(dp.start_polling(bot, handle_signals=False))
    log.info("Telegram polling task started")
    return bot, [reminders_task, broadcast_task, risk_alert_task, polling_task]
