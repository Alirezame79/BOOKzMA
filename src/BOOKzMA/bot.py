import asyncio
import contextlib
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError
from aiogram.types import BotCommand

from BOOKzMA.config import Settings
from BOOKzMA.db.session import create_session_pool
from BOOKzMA.handlers import get_router
from BOOKzMA.middlewares.db import DbSessionMiddleware
from BOOKzMA.middlewares.membership import MembershipMiddleware
from BOOKzMA.services.scheduler import reminder_loop

log = logging.getLogger(__name__)

COMMANDS = [
    BotCommand(command="start", description="منوی اصلی و استریک"),
    BotCommand(command="reminders", description="یادآورهای مطالعه"),
    BotCommand(command="timezone", description="منطقه زمانی"),
]


async def main() -> None:
    settings = Settings()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    engine, session_pool = create_session_pool(settings.database_url)
    bot = Bot(
        token=settings.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()
    membership = MembershipMiddleware()
    dp.update.outer_middleware(DbSessionMiddleware(session_pool))
    dp.message.outer_middleware(membership)
    dp.callback_query.outer_middleware(membership)
    dp.include_router(get_router())

    reminders_task = asyncio.create_task(reminder_loop(bot, session_pool))
    try:
        try:
            await bot.set_my_commands(COMMANDS)
        except TelegramAPIError:
            log.warning("set_my_commands failed, continuing")
        await dp.start_polling(bot)
    finally:
        reminders_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await reminders_task
        await engine.dispose()
        await bot.session.close()
