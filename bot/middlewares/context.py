from typing import Any, Awaitable, Callable, Dict

import structlog
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from aiogram.enums.chat_type import ChatType

from bot.user_topic_context import UserTopicContext, MessageDirection

logger: structlog.BoundLogger = structlog.get_logger()


class UserTopicContextMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:

        if isinstance(event.event, Message):
            # Ignore "service messages" and other irrelevant content types
            if UserTopicContext.is_service_message(event.event):
                return

            context = UserTopicContext(data.get("event_from_user"))

            if event.event.chat.id == data["forum_chat_id"]:
                context.message_direction = MessageDirection.FORUM_TO_USER
            elif event.event.chat.type == ChatType.PRIVATE:
                context.message_direction = MessageDirection.USER_TO_FORUM
            else:
                await logger.adebug(
                    event="Unknown message direction",
                    update=event
                )
                context.message_direction = MessageDirection.UNKNOWN

            await logger.adebug(
                event="User Topic Context created!"
            )
            data.update(context=context)

        return await handler(event, data)
