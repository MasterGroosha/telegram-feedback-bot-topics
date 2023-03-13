import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.config_reader import config
from bot.handlers import handlers_queue


async def main():
    # Настройка логирования в stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()
    dp.include_routers(*handlers_queue)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


asyncio.run(main())
