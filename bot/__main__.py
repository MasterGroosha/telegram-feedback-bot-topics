import asyncio

import structlog
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from bot.config_reader import parse_settings, FSMModeEnum, Settings
from bot.handlers import get_shared_router
from bot.middlewares import TopicsManagementMiddleware, RepliesMiddleware, EditedMessagesMiddleware, DbSessionMiddleware

# from cachetools import LRUCache

logger: structlog.BoundLogger = structlog.get_logger()


async def main():
    config: Settings = parse_settings()
    engine = create_async_engine(url=str(config.postgres.dsn), echo=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    if config.bot.fsm_mode == FSMModeEnum.MEMORY:
        storage = MemoryStorage()
    else:
        storage = RedisStorage.from_url(
            url=config.redis.dsn,
            connection_kwargs={"decode_responses": True}
        )

    # bans_cache = LRUCache(maxsize=5000)
    # shadowbans_cache = LRUCache(maxsize=5000)

    bot = Bot(token=config.bot.token.get_secret_value())
    dp = Dispatcher(forum_chat_id=config.bot.forum_supergroup_id, storage=storage)

    # Ensure that we always have PostgreSQL connection in middlewares
    dp.message.outer_middleware(DbSessionMiddleware(sessionmaker))
    dp.edited_message.outer_middleware(DbSessionMiddleware(sessionmaker))

    talk_router = get_shared_router(config.bot)
    talk_router.message.outer_middleware(TopicsManagementMiddleware())
    talk_router.message.middleware(RepliesMiddleware())
    talk_router.edited_message.middleware(EditedMessagesMiddleware())

    dp.include_router(talk_router)

    await logger.ainfo("Starting Bot")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


asyncio.run(main())
