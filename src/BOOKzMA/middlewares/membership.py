import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware, Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, Message, TelegramObject

from BOOKzMA import keyboards, texts
from BOOKzMA.constants import REQUIRED_CHANNELS

log = logging.getLogger(__name__)

MEMBER_STATUSES = {
    ChatMemberStatus.CREATOR,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.MEMBER,
}
CACHE_SECONDS = 300


async def missing_channels(bot: Bot, user_id: int) -> list[str]:
    """کانال‌هایی که کاربر عضوشون نیست. اگه چک خطا بده عضو حساب نمی‌شه."""
    missing = []
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in MEMBER_STATUSES:
                missing.append(channel)
        except TelegramAPIError:
            log.exception("membership check failed for %s (is the bot an admin there?)", channel)
            missing.append(channel)
    return missing


class MembershipMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self._ok_until: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)
        if isinstance(event, CallbackQuery) and event.data == "check_join":
            return await handler(event, data)
        if self._ok_until.get(user.id, 0) > time.monotonic():
            return await handler(event, data)

        bot: Bot = data["bot"]
        missing = await missing_channels(bot, user.id)
        if not missing:
            self._ok_until[user.id] = time.monotonic() + CACHE_SECONDS
            return await handler(event, data)

        if isinstance(event, CallbackQuery):
            await event.answer(texts.JOIN_FIRST, show_alert=True)
            if isinstance(event.message, Message):
                await event.message.answer(texts.JOIN_GATE, reply_markup=keyboards.join_kb(missing))
        elif isinstance(event, Message):
            await event.answer(texts.JOIN_GATE, reply_markup=keyboards.join_kb(missing))
        return None
