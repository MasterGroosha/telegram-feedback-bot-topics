import asyncio

import structlog
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.fsm.storage.redis import RedisStorage
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from bot.config_reader import parse_settings, FSMModeEnum, Settings
from bot.fluent_loader import get_fluent_localization
from bot.handlers import attach_routers_and_middlewares

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
            url=str(config.redis.dsn),
            connection_kwargs={"decode_responses": True}
        )

    # bans_cache = LRUCache(maxsize=5000)
    # shadowbans_cache = LRUCache(maxsize=5000)

    # Loading localization for bot
    l10n = get_fluent_localization(config.bot.language)

    bot = Bot(token=config.bot.token.get_secret_value())
    dp = Dispatcher(
        forum_chat_id=config.bot.forum_supergroup_id,
        topics_to_ignore=config.bot.ignored_topics_ids,
        storage=storage,
        l10n=l10n
    )
    if not config.bot.albums_preserve_enabled:
        dp.fsm.events_isolation = SimpleEventIsolation()

    attach_routers_and_middlewares(
        dispatcher=dp,
        bot_config=config.bot,
        sessionmaker=sessionmaker
    )

    await logger.ainfo("Starting Bot")
    await bot.delete_webhook()
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


asyncio.run(main())
