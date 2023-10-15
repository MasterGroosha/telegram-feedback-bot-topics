from typing import Any, Awaitable, Callable, Dict

import structlog
from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Message

from bot.user_topic_context import UserTopicContext

logger: structlog.BoundLogger = structlog.get_logger()


class MessageConnectionsMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        await logger.adebug("Called MessageConnectionsMiddleware")
        # If someone accidentally tried to add this middleware
        # to anything but messages, just ignore it
        if not isinstance(event, Message):
            await logger.awarn("%s used not for Message, but for %s", self.__class__.__name__, type(event))
            return await handler(event, data)

        event: Message

        if "error" in data:
            return await handler(event, data)

        # Flag. which states, whether message coming TO forum or FROM forum
        is_incoming_message: bool = (event.chat.id != data["forum_chat_id"])
        await logger.adebug("is_incoming_message", value=is_incoming_message)

        """
        If message itself is reply, the following logic is applied:
        0. If message is reply to FORUM_TOPIC_CREATED service message, ignore
        1. Find out, which message is in reply: from user (their own message) or from bot ( == from another party)
        2. Prepare filters to search in database:
        2a. If message comes from bot, then user replies to other person's message in other chat.
            Thus, we use this replied message's id as "TO:"
        2b. If message comes from user, then user replies to their own message in the same chat.
            This, we use this replied message's id as "FROM:"
        3. Pass the other message ID to handlers
        """

        context: UserTopicContext = data["context"]

        if event.reply_to_message and not event.reply_to_message.forum_topic_created:
            bot: Bot = data["bot"]
            is_from_bot: bool = event.reply_to_message.from_user.id == bot.id
            replied_message = await context.get_message_pair(
                is_from_bot=is_from_bot,
                chat_id=event.reply_to_message.chat.id,
                message_id=event.reply_to_message.message_id
            )
            await logger.adebug("Is replied message found?", result=bool(replied_message))
            if replied_message is not None:
                if is_from_bot:
                    context.reply_to_id = replied_message.from_message_id
                else:
                    context.reply_to_id = replied_message.to_message_id

        outgoing_messages: list[Message] | None = await handler(event, data)
        if not outgoing_messages:
            return

        messages_data = list()
        from_id = event.message_id
        for item in outgoing_messages:
            messages_data.append({
                "incoming": is_incoming_message,
                "from_chat_id": event.chat.id,
                "from_message_id": from_id,
                "to_chat_id": item.chat.id,
                "to_message_id": item.message_id
            })
            from_id += 1

        # Writing data to database
        await context.add_messages_pairs(messages_data)
