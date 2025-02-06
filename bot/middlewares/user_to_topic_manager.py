from typing import Callable, Awaitable, Dict, Any

import structlog
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import ForumTopic, TelegramObject, Message, User
from fluent.runtime import FluentLocalization
from sqlalchemy.ext.asyncio import AsyncSession
from structlog.types import FilteringBoundLogger

from bot.db.models import Topic
from bot.handlers_feedback import MessageConnectionFeedback
from bot.middlewares import ConnectionMiddleware

logger: FilteringBoundLogger = structlog.get_logger()


class TopicFinderUserToGroup(ConnectionMiddleware):
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
        l10n: FluentLocalization = data["l10n"]

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
                data["error"] = l10n.format_value("error-failed-to-create-topic")
            else:
                data["topic_id"] = created_topic.message_thread_id
                data["new_topic_created"] = True
        else:
            await logger.adebug(f"Found topic for user {user.id}: {topic.topic_id}")
            data["topic_id"] = topic.topic_id

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
