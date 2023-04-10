from typing import Any, Awaitable, Callable, Dict, Optional

import structlog
from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Message
from motor.motor_asyncio import AsyncIOMotorDatabase

log: structlog.BoundLogger = structlog.get_logger()


class MessagesConnectorMiddleware(BaseMiddleware):
    def __init__(self, mongo: AsyncIOMotorDatabase):
        self.mongo = mongo

    async def get_message_by_id(
            self,
            is_from_bot: bool,
            chat_id: int,
            message_id: int
    ) -> Optional[dict]:
        if is_from_bot:
            filters = {"to_chat_id": chat_id, "to_message_id": message_id}
        else:
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
        is_incoming_message: bool = (event.chat.id != data["forum_chat_id"])

        message_data = {
            "incoming": is_incoming_message,
            "from_chat_id": event.chat.id,
            "from_message_id": event.message_id,
        }

        if event.reply_to_message:
            bot: Bot = data["bot"]
            is_from_bot: bool = event.reply_to_message.from_user.id == bot.id
            replied_message = await self.get_message_by_id(
                is_from_bot=is_from_bot,
                chat_id=event.reply_to_message.chat.id,
                message_id=event.reply_to_message.message_id
            )
            if is_from_bot:
                data["reply_to_id"] = replied_message["from_message_id"]
            else:
                data["reply_to_id"] = replied_message["to_message_id"]

        outgoing_message: Message | None = await handler(event, data)
        if not outgoing_message:
            return

        message_data.update(
            to_chat_id=outgoing_message.chat.id,
            to_message_id=outgoing_message.message_id
        )

        await self.mongo.messages.insert_one(message_data)
