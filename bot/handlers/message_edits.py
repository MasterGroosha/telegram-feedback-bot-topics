from aiogram import Bot
from aiogram.types import Message

from bot.user_topic_context import UserTopicContext


async def any_edited_message(
        message: Message,
        bot: Bot,
        context: UserTopicContext,
):
    """
    Handler to edited message anywhere.
    Updates corresponding message in other chat
    (either forum supergroup or PM)

    :param message: message from Telegram
    :param bot: bot instance
    """
    if not context.edit_message_id:
        return

    kwargs = {
        "chat_id": context.edit_chat_id,
        "message_id": context.edit_message_id
    }

    if message.text:
        method = bot.edit_message_text
        kwargs.update(text=message.text)
    else:
        method = bot.edit_message_caption
        kwargs.update(caption=message.caption)

    await method(**kwargs)
