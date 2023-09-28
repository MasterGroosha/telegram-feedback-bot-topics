import structlog
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from fluent.runtime import FluentLocalization


router = Router(name="pm_router")
log: structlog.BoundLogger = structlog.get_logger()


@router.message(CommandStart())
async def cmd_start(message: Message, l10n: FluentLocalization):
    """
    Handler to /start commands in PM with user

    :param message: message from Telegram
    :param l10n: FluentLocalization object
    """
    await message.answer(l10n.format_value("start-text"))
