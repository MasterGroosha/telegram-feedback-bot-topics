from typing import Any, Awaitable, Callable, Dict, Optional

import structlog
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from motor.motor_asyncio import AsyncIOMotorDatabase

log: structlog.BoundLogger = structlog.get_logger()


class EditedMessagesMiddleware(BaseMiddleware):
    def __init__(self, mongo: AsyncIOMotorDatabase):
        self.mongo = mongo

    async def get_message_by_id(
            self,
            chat_id: int,
            message_id: int
    ) -> Optional[dict]:
        filters = {"from_chat_id": chat_id, "from_message_id": message_id}
        mongo_document = await self.mongo.messages.find_one(filters)
        return mongo_document

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
        saved_message = await self.get_message_by_id(
            chat_id=event.chat.id,
            message_id=event.message_id
        )
        data.update(
            edit_chat_id=saved_message["to_chat_id"],
            edit_message_id=saved_message["to_message_id"]
        )

        return await handler(event, data)
