import asyncio

import structlog
from aiogram import Bot, Dispatcher
from structlog.typing import FilteringBoundLogger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from bot.config_reader import get_config, LogConfig, BotConfig, DbConfig
from bot.handlers import get_routers
from bot.logs import get_structlog_config
from bot.middlewares import DbSessionMiddleware


async def main():
    log_config: LogConfig = get_config(model=LogConfig, root_key="logs")
    structlog.configure(**get_structlog_config(log_config))

    bot_config: BotConfig = get_config(model=BotConfig, root_key="bot")
    bot = Bot(bot_config.token.get_secret_value())
    dp = Dispatcher()

    db_config: DbConfig = get_config(model=DbConfig, root_key="db")

    engine = create_async_engine(
        url=str(db_config.dsn),
    )
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))

    Sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    dp.update.outer_middleware(DbSessionMiddleware(Sessionmaker))

    dp.include_routers(*get_routers(supergroup_id=bot_config.supergroup_id))

    logger: FilteringBoundLogger = structlog.get_logger()
    await logger.ainfo("Starting polling...")

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
