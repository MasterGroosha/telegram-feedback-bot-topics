from typing import Any, Awaitable, Callable, Dict, Optional

import structlog
from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Message
from motor.motor_asyncio import AsyncIOMotorDatabase

log: structlog.BoundLogger = structlog.get_logger()


class RepliesMiddleware(BaseMiddleware):
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

        # Prepare to write message data to MongoDB
        message_data = {
            "incoming": is_incoming_message,
            "from_chat_id": event.chat.id,
            "from_message_id": event.message_id,
        }

        """
        If message itself is reply, the following logic is applied:
        0. If message is reply to FORUM_TOPIC_CREATED service message, ignore
        1. Find out, which message is in reply: from user (their own message) or from bot ( == from another party)
        2. Prepare filters to search in MongoDB:
        2a. If message comes from bot, then user replies to other person's message in other chat.
            Thus, we use this replied message's id as "TO:"
        2b. If message comes from user, then user replies to their own message in the same chat.
            This, we use this replied message's id as "FROM:"
        3. Pass the other message ID to handlers
        """
        if event.reply_to_message and not event.reply_to_message.forum_topic_created:
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

        # Add more message data details
        message_data.update(
            to_chat_id=outgoing_message.chat.id,
            to_message_id=outgoing_message.message_id
        )

        # Writing data to MongoDB
        await self.mongo.messages.insert_one(message_data)
