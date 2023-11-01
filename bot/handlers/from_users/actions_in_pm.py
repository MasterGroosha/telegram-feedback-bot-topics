from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from fluent.runtime import FluentLocalization

from bot.handlers.message_edits import any_edited_message


async def cmd_start(message: Message, l10n: FluentLocalization):
    """
    Handler to /start commands in PM with user

    :param message: message from Telegram
    :param l10n: FluentLocalization object
    """
    await message.answer(l10n.format_value("start-text"))


def get_router() -> Router:
    router = Router(name="actions_in_pm")
    router.message.register(cmd_start, F.text, CommandStart())

    return router
