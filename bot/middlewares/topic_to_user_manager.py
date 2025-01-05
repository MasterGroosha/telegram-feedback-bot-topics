from typing import Callable, Awaitable, Dict, Any

import structlog
from aiogram.types import TelegramObject, Message
from fluent.runtime import FluentLocalization
from sqlalchemy.ext.asyncio import AsyncSession
from structlog.types import FilteringBoundLogger

from bot.db.models import Topic
from bot.handlers_feedback import MessageConnectionFeedback
from bot.middlewares import ConnectionMiddleware

logger: FilteringBoundLogger = structlog.get_logger()


class GroupToUserMiddleware(ConnectionMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        session: AsyncSession = data["session"]
        l10n: FluentLocalization = data["l10n"]

        result = await session.execute(Topic.find_by_topic_id(event.message_thread_id))
        topic = result.scalar_one_or_none()

        if not topic:
            await logger.aerror(f"No user found for topic {event.message_thread_id}")
            data["error"] = l10n.format_value("error-no-user-found-for-topic")
        else:
            await logger.adebug(f"Found user for topic {topic.topic_id}: {topic.user_id}")
            data["user_id"] = topic.user_id

        # If it is a reply to some other message, try to find it.
        if (reply := event.reply_to_message) is not None:
            data["reply_to_message_id"] = await self.find_replied_message_pair(
                reply_message=reply,
                session=session,
            )

        result = await handler(event, data)

        if isinstance(result, MessageConnectionFeedback):
            await self.create_new_message_connection(
                message_connection=result,
                session=session,
            )

        return result
