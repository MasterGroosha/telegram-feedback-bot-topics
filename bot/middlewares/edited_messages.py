from typing import Any, Awaitable, Callable, Dict, Optional

import structlog
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from bot.db.requests import get_message_pair

log: structlog.BoundLogger = structlog.get_logger()


class EditedMessagesMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        # If someone accidentally tried to add this middleware
        # to anything but messages, just ignore it
        if not isinstance(event, Message):
            log.warn("%s used not for Message, but for %s", self.__class__.__name__, type(event))
            return await handler(event, data)

        event: Message
        session = data["session"]

        saved_message = await get_message_pair(
            session=session,
            is_from_bot=False,
            chat_id=event.chat.id,
            message_id=event.message_id
        )
        data.update(
            edit_chat_id=saved_message.to_chat_id,
            edit_message_id=saved_message.to_message_id
        )

        return await handler(event, data)
