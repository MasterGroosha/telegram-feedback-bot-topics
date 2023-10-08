import structlog
from aiogram import Router, F, Bot
from aiogram.filters import MagicData
from aiogram.types import Message, InputMediaPhoto, InputMediaVideo, InputMediaAudio, InputMediaDocument
from fluent.runtime import FluentLocalization

from bot.topic_context import MessageDirection, TopicContext

router = Router(name="copy_messages")
log: structlog.BoundLogger = structlog.get_logger()


# TODO: отправлять ошибку, которая пришла из мидлвари
# TODO: и уходить в errors_handler, если он есть
@router.message(MagicData(F.error))
async def error_in_transfer(
        message: Message,
        error: str,
        l10n: FluentLocalization
):
    await message.answer(l10n.format_value(error))


def make_album_part(message: Message) \
        -> InputMediaPhoto | InputMediaVideo | InputMediaAudio | InputMediaDocument | None:
    caption = message.caption
    if message.photo:
        return InputMediaPhoto(media=message.photo[-1].file_id, caption=caption)
    if message.video:
        return InputMediaVideo(media=message.video.file_id, caption=caption)
    if message.audio:
        return InputMediaAudio(media=message.audio.file_id, caption=caption)
    if message.document:
        return InputMediaDocument(media=message.document.file_id, caption=caption)
    return None


def make_new_album(messages: list[Message]) \
        -> list[InputMediaPhoto | InputMediaVideo | InputMediaAudio | InputMediaDocument]:
    media = list()
    for message in messages:
        item = make_album_part(message)
        if item is not None:
            media.append(item)
    return media


@router.message()
async def any_message(
        message: Message,
        bot: Bot,
        context: TopicContext,
        forum_chat_id: int,
        reply_to_id: int | None = None,
        album: list[Message] | None = None
):
    """
    Handler to any other message in PM with user

    :param message: message from Telegram
    :param bot: bot object
    :param context: topic, related to this handler
    :param forum_chat_id: forum supergroup's ID
    :param reply_to_id: if not None, this message should be a reply in forum supergroup topic
    :param album: if original message was album (group of messages), they will be here
    :return: sent message(s) object(s) to save in DB later
    """

    kwargs = {
        "reply_to_message_id": reply_to_id,
        "allow_sending_without_reply": True,
    }

    if context.direction == MessageDirection.TO_USER:
        kwargs.update(chat_id=context.topic.user_id)
    else:
        kwargs.update(
            chat_id=forum_chat_id,
            message_thread_id=context.topic.topic_id
        )

    if album:
        # Re-sort album parts to prevent disorder (apparently it happens!)
        album.sort(key=lambda m: m.message_id)

        new_album = make_new_album(album)
        kwargs.update(media=new_album)
        msgs: list[Message] = await bot.send_media_group(**kwargs)
        return msgs
    else:
        msg: Message = await message.send_copy(**kwargs)
        return [msg]


@router.edited_message()
async def any_edited_message(
        message: Message,
        bot: Bot,
        edit_chat_id: int | None = None,
        edit_message_id: int | None = None
):
    """
    Handler to edited message anywhere.
    Updates corresponding message in other chat
    (either forum supergroup or PM)

    :param message: message from Telegram
    :param bot: bot instance
    :param edit_chat_id: chat id to edit message in
    :param edit_message_id: message id to edit in edit_chat_id
    """
    if not edit_message_id:
        return

    kwargs = {
        "chat_id": edit_chat_id,
        "message_id": edit_message_id
    }

    if message.text:
        method = bot.edit_message_text
        kwargs.update(text=message.text)
    else:
        method = bot.edit_message_caption
        kwargs.update(caption=message.caption)

    await method(**kwargs)
