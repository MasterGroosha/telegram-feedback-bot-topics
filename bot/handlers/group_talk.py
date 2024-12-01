from aiogram import F, Router
from aiogram.types import Message, MessageId

from bot.handlers_feedback import MessageConnectionFeedback

router = Router()


@router.message(F.text)
async def any_text_message(
        message: Message,
        user_id: int | None = None,
        error: str | None = None,
):
    if error is not None:
        await message.answer(error)
        return
    result: MessageId = await message.copy_to(
        chat_id=user_id,
    )
    return MessageConnectionFeedback(
        from_chat_id=message.chat.id,
        from_message_id=message.message_id,
        to_chat_id=user_id,
        to_message_id=result.message_id,
    )
