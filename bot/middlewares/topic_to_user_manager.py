from typing import Callable, Awaitable, Dict, Any

import structlog
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from sqlalchemy.ext.asyncio import AsyncSession
from structlog.types import FilteringBoundLogger

from bot.db.models import MessageConnection, Topic
from bot.handlers_feedback import MessageConnectionFeedback

logger: FilteringBoundLogger = structlog.get_logger()


class GroupToUserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        session: AsyncSession = data["session"]

        result = await session.execute(Topic.find_by_topic_id(event.message_thread_id))
        topic = result.scalar_one_or_none()

        if not topic:
            await logger.aerror(f"No user found for topic {event.message_thread_id}")
            data["error"] = "No user found for this topic"
        else:
            await logger.adebug(f"Found user for topic {topic.topic_id}: {topic.user_id}")
            data["user_id"] = topic.user_id

        result = await handler(event, data)

        if isinstance(result, MessageConnectionFeedback):
            await self.create_new_message_connection(
                message_connection=result,
                session=session,
            )

        return result


    # todo: this code duplicates user_to_topic_manager.py
    @staticmethod
    async def create_new_message_connection(
            message_connection: MessageConnectionFeedback,
            session: AsyncSession,
    ):
        new_obj = MessageConnection(
            from_chat_id=message_connection.from_chat_id,
            from_message_id=message_connection.from_message_id,
            to_chat_id=message_connection.to_chat_id,
            to_message_id=message_connection.to_message_id,
        )
        session.add(new_obj)
        try:
            await session.commit()
            await logger.adebug(
                f"Successfully saved messages pair to database",
                details=new_obj.as_dict(),
            )
        except:
            await logger.aexception("Failed to save messages pair to database")
