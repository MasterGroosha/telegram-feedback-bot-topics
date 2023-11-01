from typing import Any, Awaitable, Callable, Dict

import structlog
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message

from bot.user_topic_context import UserTopicContext

logger: structlog.BoundLogger = structlog.get_logger()


class EditedMessagesMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        await logger.adebug("Called EditedMessagesMiddleware")
        # If someone accidentally tried to add this middleware
        # to anything but messages, just ignore it
        if not isinstance(event, Message):
            await logger.awarn("%s used not for Message, but for %s", self.__class__.__name__, type(event))
            return await handler(event, data)

        event: Message
        context: UserTopicContext = data["context"]

        saved_message = await context.get_message_pair(
            is_from_bot=False,
            chat_id=event.chat.id,
            message_id=event.message_id
        )
        await logger.adebug(
            event="Attempted to get message pair for edited message",
            result=bool(saved_message)
        )
        if saved_message is not None:
            context.edit_chat_id = saved_message.to_chat_id
            context.edit_message_id = saved_message.to_message_id
        return await handler(event, data)
