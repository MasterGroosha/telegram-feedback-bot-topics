import structlog
from aiogram import Router, F
from aiogram.filters import MagicData
from aiogram.types import Message

from bot.config_reader import config

router = Router(name="Forum Router")
log: structlog.BoundLogger = structlog.get_logger()

# This router should only work in forum
router.message.filter(F.chat.id == config.forum_supergroup_id)


@router.message(MagicData(F.user_id.is_(None)))
async def no_user_id(message: Message):
    await message.answer("Error: couldn't find corresponding user_id. Message cannot be delivered")


@router.message()
async def any_message(message: Message, user_id: int | None, reply_to_id: int | None = None):
    msg: Message = await message.send_copy(chat_id=user_id, reply_to_message_id=reply_to_id)
    return msg
