from aiogram import F, Router
from aiogram.types import Message

router = Router()


@router.message(F.text)
async def cmd_start(message: Message):
    await message.answer("Hello world")
