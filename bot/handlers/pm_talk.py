from aiogram import F, Router
from aiogram.types import Message

router = Router()


@router.message(F.text)
async def any_text_message(message: Message):
    await message.answer("Any text message in PM")
