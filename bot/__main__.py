import asyncio

import motor.motor_asyncio
import structlog
from aiogram import Bot, Dispatcher
# from cachetools import LRUCache

from bot.config_reader import config
from bot.handlers import from_users, from_forum, message_edits
from bot.middlewares import TopicsManagementMiddleware, RepliesMiddleware, EditedMessagesMiddleware

log: structlog.BoundLogger = structlog.get_logger()


async def main():
    mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(config.mongo_dsn)
    mongodb_connection = mongodb_client.bot

    # bans_cache = LRUCache(maxsize=5000)
    # shadowbans_cache = LRUCache(maxsize=5000)

    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher(forum_chat_id=config.forum_supergroup_id, mongo=mongodb_connection)

    # from_users.router.message.middleware(BansMiddleware(redis_connection, bans_cache, shadowbans_cache))
    dp.message.outer_middleware(TopicsManagementMiddleware(mongodb_connection))
    dp.message.middleware(RepliesMiddleware(mongodb_connection))
    dp.edited_message.middleware(EditedMessagesMiddleware(mongodb_connection))

    dp.include_router(message_edits.router)
    dp.include_router(from_users.router)
    dp.include_router(from_forum.router)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


asyncio.run(main())
