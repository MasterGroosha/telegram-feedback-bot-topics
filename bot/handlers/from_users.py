import structlog
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.config_reader import config

router = Router(name="Users router")
log: structlog.BoundLogger = structlog.get_logger()

# This router should only work in PM
router.message.filter(F.chat.type == "private")


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("% start command message %")


@router.message()
async def any_message(message: Message, topic_id: int, reply_to_id: int | None = None):
    msg: Message = await message.send_copy(
        chat_id=config.forum_supergroup_id,
        message_thread_id=topic_id,
        reply_to_message_id=reply_to_id
    )
    return msg
