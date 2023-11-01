from typing import Any, Awaitable, Callable, Dict

import structlog
from aiogram import BaseMiddleware, Bot
from aiogram.enums import ContentType, ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import TelegramObject, Message, ForumTopic
from cachetools import LRUCache
from fluent.runtime import FluentLocalization
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import Topic
from bot.user_topic_context import UserTopicContext

log: structlog.BoundLogger = structlog.get_logger()


class TopicsManagementMiddleware(BaseMiddleware):
    def __init__(self):
        self.cache = LRUCache(maxsize=10)

    async def find_topic(
            self,
            session: AsyncSession,
            *,
            user_id: int = None,
            topic_id: int = None
    ) -> Topic | None:
        """
        Search for topic using user_id or topic_id

        :param session: SQLAlchemy session
        :param user_id: [keyword-only] Telegram User ID
        :param topic_id: [keyword-only] Telegram Forum Topic ID
        :return: None, if topic not found; Topic object otherwise
        """
        if user_id is not None:
            if user_id in self.cache:
                log.debug("User %s found in local cache", user_id)
                return self.cache[user_id]
            statement = select(Topic).where(Topic.user_id == user_id)
        else:
            value: Topic
            for key, value in self.cache.items():
                if value.topic_id == topic_id:
                    log.debug("Topic %s found in local cache", topic_id)
                    return value
            statement = select(Topic).where(Topic.topic_id == topic_id)
        entry = await session.scalar(statement)
        if entry is not None:
            self.cache[entry.user_id] = entry
        return entry

    async def create_new_topic(
            self,
            session: AsyncSession,
            bot: Bot,
            supergroup_id: int,
            message: Message,
            l10n: FluentLocalization
    ) -> Topic | None:
        try:
            new_topic: ForumTopic = await bot.create_forum_topic(supergroup_id, message.from_user.full_name[:127])
            first_topic_message = await bot.send_message(
                supergroup_id,
                message_thread_id=new_topic.message_thread_id,
                text=UserTopicContext.make_first_topic_message(l10n, message.from_user),
                parse_mode=ParseMode.HTML
            )
        except TelegramBadRequest as ex:
            log.error(
                event="Could not create new topic",
                error_type=ex.__class__.__name__, message=ex.message,
                method=ex.method.__class__.__name__, method_args=ex.method.dict()
            )
            return None

        db_topic: Topic = Topic(
            user_id=message.from_user.id,
            topic_id=new_topic.message_thread_id,
            first_message_id=first_topic_message.message_id
        )
        session.add(db_topic)
        try:
            await session.commit()
        except Exception as ex:
            log.error(
                event="Could not save new topic to DB",
                error_type=ex.__class__.__name__, message=str(ex),
                topic_id=new_topic.message_thread_id,
                user_id=message.from_user.id
            )
            return None

        log.debug("Created new topic with id %s", new_topic.message_thread_id)
        self.cache[message.from_user.id] = db_topic
        return db_topic

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        # If someone accidentally tried to add this middleware
        # to anything but messages or edited messages, just ignore it
        if not isinstance(event, Message):
            log.warn("%s used not for Message, but for %s", self.__class__.__name__, type(event))
            return await handler(event, data)

        event: Message
        context: UserTopicContext = data["context"]

        # If message comes from supergroup:
        if event.chat.id == data["forum_chat_id"]:
            # If this topic id is in "ignored" list, well, ignore it!
            if event.message_thread_id in data["topics_to_ignore"]:
                return

            # If the message comes from forum supergroup, find relevant user id
            topic: Topic | None = await self.find_topic(
                context.session,
                topic_id=event.message_thread_id
            )
            if topic is not None:
                context.topic_entry = topic
            else:
                data.update(error="error-cannot-find-user")

        # If message comes from user:
        else:
            topic: Topic | None = await self.find_topic(
                context.session,
                user_id=event.from_user.id
            )
            if topic:
                context.topic_entry = topic
            else:
                l10n = data["l10n"]
                new_topic: Topic | None = await self.create_new_topic(
                    session=context.session,
                    bot=data["bot"],
                    supergroup_id=data["forum_chat_id"],
                    message=event,
                    l10n=l10n
                )
                if new_topic is not None:
                    context.topic_entry = new_topic
                else:
                    data.update(error="error-cannot-deliver-to-forum")

        return await handler(event, data)
