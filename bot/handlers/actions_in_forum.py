import structlog
from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from fluent.runtime import FluentLocalization
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.requests import get_ban_status,ban_or_shadowban

router = Router(name="forum_router")
logger: structlog.BoundLogger = structlog.get_logger()


@router.message(Command(commands="note", prefix="!"))
async def note(message: Message):
    """
    Handler to messages which start with "!note" command.
    Such messages should be ignored.

    :param message: any message which text or caption starts with "!note"
    """
    return


@router.message(Command("ban", "shadowban"))
async def cmd_ban_or_shadowban(
        message: Message,
        command: CommandObject,
        session: AsyncSession,
        l10n: FluentLocalization
):
    need_to_ban = (command.command == "ban")
    need_to_shadowban = not need_to_ban

    banned_user = await get_ban_status(session, message.from_user.id)
    ban_kwargs = {"session": session, "user_id": message.from_user.id}

    # If user was not previously banned
    if banned_user is None:
        try:
            await ban_or_shadowban(
                session=session,
                existing_object=None,
                user_id=message.from_user.id,
                is_shadowban=need_to_shadowban
            )
        except Exception as ex:
            await logger.aerror(
                event="Failed to ban user",
                is_ban=need_to_ban,
                is_shadowban=need_to_shadowban,
                user_id=message.from_user.id,
                exception_type=type(ex),
                exception_text=str(ex)
            )
            await message.answer(l10n.format_value("any-ban-error"))
        else:
            if need_to_ban:
                success_message_code = "banned-successfully"
            else:
                success_message_code = "shadowbanned-successfully"
            await message.answer(l10n.format_value(success_message_code))
        return

    # If user was previously banned

    if need_to_ban:
        if banned_user.is_shadowbanned:
            await message.answer(l10n.format_value("shadowbanned-before"))
        if banned_user.is_banned:
            await message.answer(l10n.format_value("already-banned"))
        return
    else:  # need_to_shadowban
        if banned_user.is_shadowbanned:
            await message.answer(l10n.format_value("already-shadowbanned"))
        else:
            ban_kwargs.update(is_shadowban=True)
            try:
                await ban_or_shadowban(
                    session=session,
                    existing_object=banned_user,
                    user_id=message.from_user.id,
                    is_shadowban=True
                )
            except Exception as ex:
                await logger.aerror(
                    event="Failed to ban user",
                    is_ban=False,
                    is_shadowban=True,
                    user_id=message.from_user.id,
                    exception_type=type(ex),
                    exception_text=str(ex)
                )
                await message.answer(l10n.format_value("any-ban-error"))
            else:
                await message.answer(l10n.format_value("shadowbanned-successfully"))
