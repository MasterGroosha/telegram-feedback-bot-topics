from typing import Callable, Awaitable, Dict, Any

import structlog
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message

from bot.user_topic_context import UserTopicContext

logger: structlog.BoundLogger = structlog.get_logger()


class BansMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        await logger.adebug("Called BansMiddleware")
        # If someone accidentally tried to add this middleware
        # to anything but messages, just ignore it
        if not isinstance(event, Message):
            await logger.awarn("%s used not for Message, but for %s", self.__class__.__name__, type(event))
            return await handler(event, data)

        context: UserTopicContext = data["context"]

        # If message comes from forum, skip middleware
        if event.chat.id == data["forum_chat_id"]:
            # Just fetch possible ban entry and save it to context
            await context.get_ban_entry(context.topic_entry.user_id)
            return await handler(event, data)

        # If message comes from private chat with user:

        # Check if user is (shadow)banned
        ban_entry = await context.get_ban_entry(context.caller.id)

        # If user is not banned, skip this middleware
        if ban_entry is None:
            return await handler(event, data)

        # Is user is shadowbanned, drop the update
        if ban_entry.is_shadowbanned is True:
            return

        if ban_entry.is_banned is True:
            data.update(error="you-are-banned")
            return await handler(event, data)

        # If for some reason user is neither banned nor shadowbanned,
        # just log this issue
        await logger.awarn(
            event="User is marked as banned, but both is_banned and is_shadowbanned are False",
            user_id=event.from_user.id
        )


