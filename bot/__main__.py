import asyncio

import structlog
from aiogram import Bot, Dispatcher
from structlog.typing import FilteringBoundLogger

from bot.config_reader import LogConfig, get_config, BotConfig
from bot.handlers import get_routers
from bot.logs import get_structlog_config


async def main():
    log_config: LogConfig = get_config(model=LogConfig, root_key="logs")
    structlog.configure(**get_structlog_config(log_config))

    bot_config: BotConfig = get_config(model=BotConfig, root_key="bot")
    bot = Bot(bot_config.token.get_secret_value())

    dp = Dispatcher()

    dp.include_routers(*get_routers())

    logger: FilteringBoundLogger = structlog.get_logger()
    await logger.ainfo("Starting polling...")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())