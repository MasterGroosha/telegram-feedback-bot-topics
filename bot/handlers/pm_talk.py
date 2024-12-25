import structlog
from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import (
    Message, MessageId, ReplyParameters,
    InputMediaAnimation, InputMediaAudio, InputMediaDocument, InputMediaPhoto, InputMediaVideo,
)
from structlog.types import FilteringBoundLogger

from bot.filters import ForwardableTypesFilter
from bot.handlers_feedback import MessageConnectionFeedback

router = Router()
logger: FilteringBoundLogger = structlog.get_logger()

@router.message(ForwardableTypesFilter())
async def any_forwardable_message(
        message: Message,
        forum_chat_id: int,
        topic_id: int | None = None,
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
        await message.reply(
            "The caption of this message is too long. "
            "Please try again with shorter caption."
        )
        return

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
        await message.reply(
            f"Failed to deliver your message. Please try again later."
        )


@router.message()
async def any_non_forwardable_message(
        message: Message,
):
    await message.reply(
        "Cannot forward this type of message. "
        "Try something else."
    )


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
