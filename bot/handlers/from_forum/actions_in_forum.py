import structlog
from aiogram import F, Router, Bot
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message
from fluent.runtime import FluentLocalization

from bot.db.models import Ban
from bot.user_topic_context import UserTopicContext

logger: structlog.BoundLogger = structlog.get_logger()


async def cmd_note(message: Message):
    """
    Handler to messages which start with "!note" command.
    Such messages should be ignored.

    :param message: any message which text or caption starts with "!note"
    """
    return


async def cmd_ban(
        message: Message,
        l10n: FluentLocalization,
        context: UserTopicContext,
        bot: Bot,
        forum_chat_id: int
):
    ban_entry: Ban | None = context.ban_entry
    if ban_entry is not None:
        if ban_entry.is_banned:
            await message.reply(l10n.format_value("already-banned"))
            return
        if ban_entry.is_shadowbanned:
            await message.reply(l10n.format_value("already-shadowbanned-before"))
            return
    try:
        await context.ban_or_shadowban(
            existing_object=ban_entry,
            user_id=context.topic_entry.user_id,
            is_shadowban=False
        )
    except Exception:
        await message.reply(l10n.format_value("any-ban-error"))
    else:
        await message.reply(l10n.format_value("banned-successfully"))
        with suppress(TelegramBadRequest):
            await context.update_first_topic_message(
                bot=bot,
                l10n=l10n,
                chat_id=forum_chat_id
            )


async def cmd_shadowban(
        message: Message,
        l10n: FluentLocalization,
        context: UserTopicContext,
        bot: Bot,
        forum_chat_id: int
):
    ban_entry: Ban | None = context.ban_entry
    if ban_entry is not None:
        if ban_entry.is_shadowbanned:
            await message.reply(l10n.format_value("already-shadowbanned"))
            return

    try:
        await context.ban_or_shadowban(
            existing_object=ban_entry,
            user_id=context.topic_entry.user_id,
            is_shadowban=True
        )
    except Exception:
        await message.reply(l10n.format_value("any-ban-error"))
    else:
        await message.reply(l10n.format_value("shadowbanned-successfully"))
        with suppress(TelegramBadRequest):
            await context.update_first_topic_message(
                bot=bot,
                l10n=l10n,
                chat_id=forum_chat_id
            )


async def cmd_unban(
        message: Message,
        l10n: FluentLocalization,
        context: UserTopicContext,
        bot: Bot,
        forum_chat_id: int
):
    ban_entry: Ban | None = context.ban_entry
    if ban_entry is None:
        await message.reply(l10n.format_value("unban-not-needed"))
        return
    try:
        await context.unban(ban_entry)
    except Exception:
        await message.reply(l10n.format_value("any-unban-error"))
    else:
        await message.reply(l10n.format_value("unbanned-successfully"))
        with suppress(TelegramBadRequest):
            await context.update_first_topic_message(
                bot=bot,
                l10n=l10n,
                chat_id=forum_chat_id
            )


async def cmd_update(
        message: Message,
        l10n: FluentLocalization,
        context: UserTopicContext,
        bot: Bot,
        forum_chat_id: int
):
    try:
        await context.update_first_topic_message(
            bot=bot,
            l10n=l10n,
            chat_id=forum_chat_id
        )
        await message.reply(l10n.format_value("user-info-update-success"))
    except TelegramBadRequest:
        await message.reply(l10n.format_value("user-info-update-error"))


def get_router() -> Router:
    router = Router(name="actions_in_forum")
    router.message.register(cmd_note, F.text, Command("note", prefix="/!"))
    router.message.register(cmd_ban, F.text, Command("ban"))
    router.message.register(cmd_shadowban, F.text, Command("shadowban"))
    router.message.register(cmd_unban, F.text, Command("unban"))
    router.message.register(cmd_update, F.text, Command("update"))

    return router
