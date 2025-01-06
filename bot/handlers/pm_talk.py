import structlog
from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import (
    Message, MessageId, ReplyParameters, User,
    InputMediaAnimation, InputMediaAudio, InputMediaDocument, InputMediaPhoto, InputMediaVideo,
)
from fluent.runtime import FluentLocalization
from structlog.types import FilteringBoundLogger

from bot.filters import ForwardableTypesFilter, ServiceMessagesFilter
from bot.handlers_feedback import MessageConnectionFeedback

router = Router()
logger: FilteringBoundLogger = structlog.get_logger()


def get_user_data(
        l10n: FluentLocalization,
        user: User,
) -> dict:
    premium_key = "yes" if user.is_premium else "no"
    premium = l10n.format_value(premium_key, {"case": "lower"})

    language_key = "unknown" if user.language_code is None else user.language_code
    language = l10n.format_value(language_key, {"case": "lower"})
    if user.username is not None:
        username = f"@{user.username}"
    else:
        username = l10n.format_value("no", {"case": "lower"})
    return {
        "full_name": user.full_name,
        "username": username,
        "premium": premium,
        "language": language,
    }


@router.message(ForwardableTypesFilter())
async def any_forwardable_message(
        message: Message,
        bot: Bot,
        forum_chat_id: int,
        l10n: FluentLocalization,
        topic_id: int | None = None,
        new_topic_created: bool | None = None,
        error: str | None = None,
        reply_to_message_id: int | None = None,
        caption_length: int | None = None,
):
    if error is not None:
        await message.answer(error)
        return

    # If message has caption, and it's too long, then we cannot copy it.
    # Actually, we should be able to copy it, but since it's forum topic, we cannot.
    # See https://github.com/tdlib/telegram-bot-api/issues/334#issuecomment-1311709507
    if caption_length is not None and caption_length > 1023:
        await message.reply(l10n.format_value("error-caption-too-long"))
        return

    if new_topic_created is True:
        user_info = get_user_data(l10n, message.from_user)
        user_info_text = l10n.format_value(
            "user-info",
            {
                "full_name": user_info["full_name"],
                "username": user_info["username"],
                "premium": user_info["premium"],
                "language": user_info["language"],
            })
        try:
            await bot.send_message(
                chat_id=forum_chat_id,
                message_thread_id=topic_id,
                text=user_info_text
            )
        except TelegramAPIError:
            reason = "Failed to send intro info message from forum group to private chat"
            await logger.aexception(reason)

    # If message is reply to another message, set parameters
    reply_parameters = None
    if reply_to_message_id is not None:
        reply_parameters = ReplyParameters(
            message_id=reply_to_message_id,
            allow_sending_without_reply=True,
        )

    try:
        result: MessageId = await message.copy_to(
            chat_id=forum_chat_id,
            message_thread_id=topic_id,
            reply_parameters=reply_parameters,
        )
        return MessageConnectionFeedback(
            from_chat_id=message.chat.id,
            from_message_id=message.message_id,
            to_chat_id=forum_chat_id,
            to_message_id=result.message_id,
        )
    except TelegramAPIError:
        reason = "Failed to send message from forum group to private chat"
        await logger.aexception(reason)
        await message.reply(l10n.format_value("error-from-pm-to-group"))


@router.message(ServiceMessagesFilter())
async def any_service_message(
        message: Message,
):
    return


@router.message()
async def any_non_forwardable_message(
        message: Message,
        l10n: FluentLocalization,
):
    await message.reply(l10n.format_value("error-non-forwardable-type"))


@router.edited_message(F.text)
async def edited_text_message(
        message: Message,
        bot: Bot,
        error: str | None = None,
        edit_chat_id: int | None = None,
        edit_message_id: int | None = None,
):
    if error is not None:
        await message.answer(error)
        return
    try:
        await bot.edit_message_text(
            chat_id=edit_chat_id,
            message_id=edit_message_id,
            text=message.text,
            entities=message.entities,
        )
    except TelegramAPIError:
        error = "Failed to edit text message on group side"
        await logger.aexception(error)


@router.edited_message()  # All other types of editable media
async def edited_media_message(
        message: Message,
        bot: Bot,
        error: str | None = None,
        edit_chat_id: int | None = None,
        edit_message_id: int | None = None,
):
    if error is not None:
        await message.answer(error)
        return

    if message.animation:
        new_media = InputMediaAnimation(media=message.animation.file_id)
    elif message.audio:
        new_media = InputMediaAudio(media=message.audio.file_id)
    elif message.document:
        new_media = InputMediaDocument(media=message.document.file_id)
    elif message.photo:
        new_media = InputMediaPhoto(media=message.photo[-1].file_id)
    elif message.video:
        new_media = InputMediaVideo(media=message.video.file_id)
    else:
        return

    if message.caption:
        new_media.caption = message.caption
        new_media.caption_entities = message.caption_entities

    try:
        await bot.edit_message_media(
            chat_id=edit_chat_id,
            message_id=edit_message_id,
            media=new_media,
        )
    except TelegramAPIError:
        error = "Failed to edit media message on group side"
        await logger.aexception(error)
