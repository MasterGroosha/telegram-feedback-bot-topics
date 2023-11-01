from aiogram import Router, Bot
from aiogram.types import Message

from bot.album_helpers import make_new_album
from bot.handlers.message_edits import any_edited_message
from bot.user_topic_context import UserTopicContext


async def any_message(
        message: Message,
        bot: Bot,
        context: UserTopicContext,
        forum_chat_id: int,
        album: list[Message] | None = None
):
    """
    Handler to any other message in PM with user

    :param message: message from Telegram
    :param bot: bot object
    :param context: topic, related to this handler
    :param forum_chat_id: forum supergroup's ID
    :param album: if original message was album (group of messages), they will be here
    :return: sent message(s) object(s) to save in DB later
    """

    kwargs = {
        "reply_to_message_id": context.reply_to_id,
        "allow_sending_without_reply": True,
    }

    kwargs.update(
        chat_id=forum_chat_id,
        message_thread_id=context.topic_entry.topic_id
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


def get_router() -> Router:
    router = Router(name="free_talk_in_pm")
    router.message.register(any_message)
    router.edited_message.register(any_edited_message)

    return router
