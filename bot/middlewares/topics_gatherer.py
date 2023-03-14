from typing import Any, Awaitable, Callable, Dict

import structlog
from aiogram import BaseMiddleware, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import TelegramObject, Message, User, ForumTopic
from cachetools import LRUCache
from redis.asyncio.client import Redis

log: structlog.BoundLogger = structlog.get_logger()


class TopicsMiddleware(BaseMiddleware):
    def __init__(self, redis: Redis, cache: LRUCache):
        self.redis = redis
        self.cache = cache

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

        user: User = data["event_from_user"]
        if user.id in self.cache:
            log.debug("User %s found in local cache", user.id)
            data["thread_id"] = self.cache[user.id]
            return await handler(event, data)

        redis_hash_name = f"ids_{user.id % 10}"

        value = await self.redis.hget(redis_hash_name, str(user.id))
        if value:
            log.debug(type(value))
            log.debug("Found key in Redis")
            self.cache[user.id] = int(value)
            data["thread_id"] = int(value)
        else:
            # Creating new forum topic
            bot: Bot = data["bot"]
            try:
                new_topic: ForumTopic = await bot.create_forum_topic(data["forum_chat_id"], f"id{user.id}")
            except TelegramBadRequest as ex:
                log.error(
                    event="Could not create new topic",
                    error_type=ex.__class__.__name__, message=ex.message,
                    method=ex.method.__class__.__name__, method_args=ex.method.dict()
                )
                data["thread_id"] = 0  # default topic
            else:
                log.debug("Created new topic with id %s", new_topic.message_thread_id)
                await self.redis.hset(name=redis_hash_name, key=str(user.id), value=str(new_topic.message_thread_id))
                self.cache[user.id] = new_topic.message_thread_id
                data["thread_id"] = new_topic.message_thread_id

        return await handler(event, data)
