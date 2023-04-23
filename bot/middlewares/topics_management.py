from textwrap import dedent
from typing import Any, Awaitable, Callable, Dict
from typing import NamedTuple

import structlog
from aiogram import BaseMiddleware, Bot
from aiogram.enums import ContentType, MessageEntityType
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import TelegramObject, Message, ForumTopic, User
from cachetools import LRUCache
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import Topic
from bot.db.requests import find_topic_entry

log: structlog.BoundLogger = structlog.get_logger()


class NewTopicData(NamedTuple):
    topic_id: int | None
    first_message_id: int | None


class TopicsManagementMiddleware(BaseMiddleware):
    def __init__(self):
        self.cache = LRUCache(maxsize=10)

    async def find_topic_by_user(self, session: AsyncSession, user_id: int) -> Topic | None:
        # Search in cache // O(1)
        if user_id in self.cache:
            log.debug("User %s found in local cache", user_id)
            return self.cache[user_id]
        user_topic_data: Topic | None = await find_topic_entry(session, user_id=user_id)
        if user_topic_data:
            # Update cache
            self.cache[user_id] = user_topic_data
            return user_topic_data

    async def find_user_by_topic(self, session: AsyncSession, topic_id: int) -> int | None:
        # Search in cache // O(n), best effort
        value: Topic
        for key, value in self.cache.items():
            if value.topic_id == topic_id:
                log.debug("Topic %s found in local cache", topic_id)
                return key
        # Search in database
        user_topic_data: Topic | None = await find_topic_entry(session, topic_id=topic_id)
        if user_topic_data:
            # Update cache
            self.cache[user_topic_data.user_id] = user_topic_data
            return user_topic_data.user_id

    @staticmethod
    def is_service_message(message: Message) -> bool:
        return message.content_type in {
            ContentType.NEW_CHAT_MEMBERS, ContentType.LEFT_CHAT_MEMBER,
            ContentType.NEW_CHAT_TITLE,
            ContentType.NEW_CHAT_PHOTO, ContentType.DELETE_CHAT_PHOTO,
            ContentType.GROUP_CHAT_CREATED, ContentType.SUPERGROUP_CHAT_CREATED, ContentType.CHANNEL_CHAT_CREATED,
            ContentType.MESSAGE_AUTO_DELETE_TIMER_CHANGED,
            ContentType.MIGRATE_TO_CHAT_ID, ContentType.MIGRATE_FROM_CHAT_ID,
            ContentType.PINNED_MESSAGE,
            ContentType.SUCCESSFUL_PAYMENT,
            ContentType.USER_SHARED, ContentType.CHAT_SHARED,
            ContentType.WRITE_ACCESS_ALLOWED,
            ContentType.PROXIMITY_ALERT_TRIGGERED,
            ContentType.FORUM_TOPIC_CREATED, ContentType.FORUM_TOPIC_EDITED,
            ContentType.FORUM_TOPIC_CLOSED, ContentType.FORUM_TOPIC_REOPENED,
            ContentType.GENERAL_FORUM_TOPIC_HIDDEN, ContentType.GENERAL_FORUM_TOPIC_UNHIDDEN,
            ContentType.VIDEO_CHAT_SCHEDULED, ContentType.VIDEO_CHAT_STARTED,
            ContentType.VIDEO_CHAT_ENDED, ContentType.VIDEO_CHAT_PARTICIPANTS_INVITED,
            ContentType.WEB_APP_DATA,
            ContentType.UNKNOWN
        }

    def prepare_first_topic_message(self, user: User) -> str:
        username = f"@{user.username}" if user.username else "no"
        premium = "yes" if user.is_premium else "no"
        language_code = user.language_code if user.language_code else "no"

        text = f""" \
        New user chat!
        
        {user.full_name}
        ├── Telegram ID: {user.id}
        ├── Username: {username}
        ├── Language: {premium}
        └── Premium: {language_code}
        """
        return dedent(text)

    async def create_new_topic(self, session: AsyncSession, bot: Bot, supergroup_id: int, message: Message):
        try:
            new_topic: ForumTopic = await bot.create_forum_topic(supergroup_id, message.from_user.full_name[:127])
            first_topic_message = await bot.send_message(
                supergroup_id,
                message_thread_id=new_topic.message_thread_id,
                text=self.prepare_first_topic_message(message.from_user)
            )
        except TelegramBadRequest as ex:
            log.error(
                event="Could not create new topic",
                error_type=ex.__class__.__name__, message=ex.message,
                method=ex.method.__class__.__name__, method_args=ex.method.dict()
            )
            return NewTopicData(None, None)

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
            return NewTopicData(None, None)

        log.debug("Created new topic with id %s", new_topic.message_thread_id)
        self.cache[message.from_user.id] = db_topic
        return NewTopicData(
            topic_id=new_topic.message_thread_id,
            first_message_id=first_topic_message.message_id
        )

    @staticmethod
    def is_start_message(message: Message):
        if message.entities is None:
            return False
        if message.entities[0].type == MessageEntityType.BOT_COMMAND and \
                message.entities[0].extract_from(message.text) == "/start":
            return True
        return False

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

        # Ignore "service messages" and other irrelevant content types
        if self.is_service_message(event):
            return

        session: AsyncSession = data["session"]

        if event.chat.id == data["forum_chat_id"]:
            # If the message comes from forum supergroup, find relevant user id
            user_id: int | None = await self.find_user_by_topic(session, event.message_thread_id)
            data.update(user_id=user_id)
        else:
            if self.is_start_message(event):
                return await handler(event, data)

            topic_info: Topic | None = await self.find_topic_by_user(session, event.from_user.id)
            if topic_info:
                data.update(
                    topic_id=topic_info.topic_id,
                    first_message_id=topic_info.first_message_id
                )
            else:
                new_topic: NewTopicData = await self.create_new_topic(
                    session=session,
                    bot=data["bot"],
                    supergroup_id=data["forum_chat_id"],
                    message=event
                )
                data.update(
                    topic_id=new_topic.topic_id,
                    first_message_id=new_topic.first_message_id
                )

        return await handler(event, data)
