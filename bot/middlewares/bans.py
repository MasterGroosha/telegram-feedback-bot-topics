"""
WARNING: THIS MIDDLEWARE IS NOT USED RIGHT NOW
"""


# from asyncio import sleep
# from typing import Any, Awaitable, Callable, Dict, NamedTuple
#
# import structlog
# from aiogram import BaseMiddleware
# from aiogram.exceptions import TelegramForbiddenError
# from aiogram.types import TelegramObject, Message, User
# from cachetools import LRUCache
# from redis.asyncio.client import Redis
#
# log: structlog.BoundLogger = structlog.get_logger()
#
#
# class CacheInfo(NamedTuple):
#     redis_name: str
#     data: LRUCache
#     callback_func: Callable
#
#
# class BansMiddleware(BaseMiddleware):
#     def __init__(self, redis: Redis, bans_cache: LRUCache, shadowbans_cache: LRUCache):
#         self.redis = redis
#         self.banlist = bans_cache
#         self.shadowbanlist = shadowbans_cache
#
#     async def __call__(
#             self,
#             handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
#             event: TelegramObject,
#             data: Dict[str, Any],
#     ) -> Any:
#
#         async def shadowban_noop():
#             # In case of shadowban, do nothing
#             return
#
#         async def ban_notify():
#             await sleep(5.0)
#             # In case of regular ban, try to notify user
#             try:
#                 await event.reply("You were banned, no message can be delivered")
#             except TelegramForbiddenError as ex:
#                 log.warn(
#                     event="Could not send ban message to user",
#                     error_type=ex.__class__.__name__, message=ex.message,
#                     method=ex.method.__class__.__name__, method_args=ex.method.dict()
#                 )
#                 return
#
#         # If someone accidentally tried to add this middleware
#         # to anything but messages, just ignore it
#         if not isinstance(event, Message):
#             log.warn("%s used not for Message, but for %s", self.__class__.__name__, type(event))
#             return await handler(event, data)
#
#         event: Message
#         user: User = data["event_from_user"]
#
#         # Check shadowban and ban lists
#         for cache in [
#             CacheInfo(redis_name="shadowbans", data=self.shadowbanlist, callback_func=shadowban_noop),
#             CacheInfo(redis_name="bans", data=self.banlist, callback_func=ban_notify)
#         ]:
#             # Step 1. Try to find user in local cache
#             if user.id in cache.data:
#                 log.debug("User %s found in local %s cache", user.id, cache.redis_name)
#                 await cache.callback_func()
#                 return  # break update flow
#
#             # Step 2. Try to find user in Redis cache
#             user_in_cache: bool = await self.redis.sismember(cache.redis_name, str(user.id))
#             if user_in_cache:
#                 log.debug("User %s found in Redis %s cache", user.id, cache.redis_name)
#                 await cache.callback_func()
#                 return  # break update flow
#
#         # Allow update to pass-through
#         return await handler(event, data)
