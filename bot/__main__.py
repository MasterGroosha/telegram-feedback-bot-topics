import asyncio

import structlog
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from bot.config_reader import config, FSMModeEnum
from bot.handlers import talk
from bot.middlewares import TopicsManagementMiddleware, RepliesMiddleware, EditedMessagesMiddleware, DbSessionMiddleware

# from cachetools import LRUCache

log: structlog.BoundLogger = structlog.get_logger()


async def main():
    engine = create_async_engine(url=config.postgres_dsn, echo=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    if config.fsm_mode == FSMModeEnum.MEMORY:
        storage = MemoryStorage()
    else:
        storage = RedisStorage.from_url(
            url=f"{config.redis.dsn}/{config.redis.fsm_db_id}",
            connection_kwargs={"decode_responses": True}
        )

    # bans_cache = LRUCache(maxsize=5000)
    # shadowbans_cache = LRUCache(maxsize=5000)

    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher(forum_chat_id=config.forum_supergroup_id, storage=storage)

    # Ensure that we always have PostgreSQL connection in middlewares
    dp.message.outer_middleware(DbSessionMiddleware(sessionmaker))
    dp.edited_message.outer_middleware(DbSessionMiddleware(sessionmaker))

    talk.router.message.outer_middleware(TopicsManagementMiddleware())
    talk.router.message.middleware(RepliesMiddleware())
    talk.router.edited_message.middleware(EditedMessagesMiddleware())

    dp.include_router(talk.router)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


asyncio.run(main())
