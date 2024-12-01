from typing import Callable, Awaitable, Dict, Any

import structlog
from aiogram import BaseMiddleware, Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import ForumTopic, TelegramObject, Message, User
from sqlalchemy.ext.asyncio import AsyncSession
from structlog.types import FilteringBoundLogger

from bot.db.models import MessageConnection, Topic
from bot.handlers_feedback import MessageConnectionFeedback

logger: FilteringBoundLogger = structlog.get_logger()


class TopicFinderUserToGroup(BaseMiddleware):
    def __init__(
            self,
            forum_chat_id: int,
    ):
        self.forum_chat_id = forum_chat_id

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        session: AsyncSession = data["session"]
        user: User = event.from_user
        data["forum_chat_id"] = self.forum_chat_id

        result = await session.execute(Topic.find_by_user_id(user.id))
        topic = result.scalar_one_or_none()

        if not topic:
            await logger.adebug(f"No topic found for user {user.id}")
            bot: Bot = data["bot"]
            created_topic: ForumTopic | None = await self.create_topic(
                bot=bot,
                user=user,
                session=session,
            )
            if created_topic is None:
                data["error"] = "Failed to create topic"
            else:
                data["topic_id"] = created_topic.message_thread_id
        else:
            await logger.adebug(f"Found topic for user {user.id}: {topic.topic_id}")
            data["topic_id"] = topic.topic_id

        result = await handler(event, data)

        if isinstance(result, MessageConnectionFeedback):
            await self.create_new_message_connection(
                message_connection=result,
                session=session,
            )

        return result

    async def create_topic(
            self,
            bot: Bot,
            user: User,
            session: AsyncSession,
            topic_color: int = 9367192,  #8EEE98 (mint green)
            topic_emoji: str = "5370870893004203704",  # "person speaking" emoji
    ) -> ForumTopic | None:
        new_topic = None
        try:
            new_topic = await bot.create_forum_topic(
                chat_id=self.forum_chat_id,
                name=f"#id{user.id}",  # todo: make a good topic name,
                icon_color=topic_color,
                icon_custom_emoji_id=topic_emoji,
            )
            await logger.adebug(
                f"Successfully created topic in forum chat",
                topic_id=new_topic.message_thread_id,
                topic_name=new_topic.name,
            )
        except TelegramAPIError as ex:
            await logger.aexception("Failed to create topic")
            # new_topic stays None

        # Try to save in database
        if new_topic is not None:
            try:
                new_topic_in_db = Topic(
                    user_id=user.id,
                    topic_id=new_topic.message_thread_id,
                )
                session.add(new_topic_in_db)

                await session.commit()
                await logger.adebug(
                    f"Successfully saved topic to database",
                    topic_id=new_topic.message_thread_id,
                    topic_name=new_topic.name,
                )
            except:
                await logger.aexception("Failed to save topic to database")

        return new_topic

    # todo: this code duplicates topic_to_user_manager.py
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
