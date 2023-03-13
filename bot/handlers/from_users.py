from aiogram import Router, F, Bot
from aiogram.filters import Command, MagicData
from aiogram.types import Message
from bot.middlewares import TopicsMiddleware
import structlog

router = Router()
log: structlog.BoundLogger = structlog.get_logger()

# This router should only work in PM
router.message.filter(F.chat.type == "private")


@router.message()
async def any_message(message: Message, forum_chat_id: int, thread_id: int, bot: Bot):
    await message.copy_to(chat_id=forum_chat_id, message_thread_id=thread_id)


