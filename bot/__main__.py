import asyncio

import structlog
from aiogram import Bot, Dispatcher
from cachetools import LRUCache
from redis.asyncio import Redis

from bot.config_reader import config
from bot.handlers import basic_commands, from_users
from bot.middlewares import TopicsMiddleware, BansMiddleware

log: structlog.BoundLogger = structlog.get_logger()


async def main():
    redis_connection = Redis.from_url(config.redis_dsn)
    # Raises ConnectionError, if Redis is not reachable
    await redis_connection.ping()

    local_cache = LRUCache(maxsize=5000)
    bans_cache = LRUCache(maxsize=5000)
    shadowbans_cache = LRUCache(maxsize=5000)

    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher(forum_chat_id=config.forum_supergroup_id)

    from_users.router.message.middleware(BansMiddleware(redis_connection, bans_cache, shadowbans_cache))
    from_users.router.message.middleware(TopicsMiddleware(redis_connection, local_cache))
    dp.include_router(basic_commands.router)
    dp.include_router(from_users.router)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


asyncio.run(main())
