from aiogram import F, Router
from aiogram.types import Message, MessageId, ReplyParameters

from bot.handlers_feedback import MessageConnectionFeedback

router = Router()


@router.message(F.text)
async def any_text_message(
        message: Message,
        forum_chat_id: int,
        topic_id: int | None = None,
        error: str | None = None,
        reply_to_message_id: int | None = None,
):
    if error is not None:
        await message.answer(error)
        return

    # If message is reply to another message, set parameters
    reply_parameters = None
    if reply_to_message_id is not None:
        reply_parameters = ReplyParameters(
            message_id=reply_to_message_id,
            allow_sending_without_reply=True,
        )

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
