import structlog
from aiogram import Router, F
from aiogram.types import Message, KeyboardButton
from bot.config_reader import config

router = Router(name="From Users Router")
log: structlog.BoundLogger = structlog.get_logger()

# This router should only work in PM
router.message.filter(F.chat.type == "private")


@router.message()
async def any_message(message: Message, topic_id: int):
    msg: Message = await message.send_copy(chat_id=config.forum_supergroup_id, message_thread_id=topic_id)
    return msg


