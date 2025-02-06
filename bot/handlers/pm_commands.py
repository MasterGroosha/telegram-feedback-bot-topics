from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from fluent.runtime import FluentLocalization

router = Router()


@router.message(CommandStart())
async def cmd_start(
        message: Message,
        l10n: FluentLocalization,
):
    await message.answer(l10n.format_value("user-start"))
