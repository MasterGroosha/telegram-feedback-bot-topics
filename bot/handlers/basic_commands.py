import structlog
from aiogram import Router, F
from aiogram.enums.chat_type import ChatType
from aiogram.filters import Command
from aiogram.types import Message

router = Router()
router.message.filter(F.chat.type == ChatType.PRIVATE)
log: structlog.BoundLogger = structlog.get_logger()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("% Start command text %")
