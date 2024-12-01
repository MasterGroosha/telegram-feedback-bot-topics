import structlog
from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message, MessageId
from structlog.types import FilteringBoundLogger

from bot.handlers_feedback import MessageConnectionFeedback

router = Router()
logger: FilteringBoundLogger = structlog.get_logger()


@router.message(F.text)
async def any_text_message(
        message: Message,
        user_id: int | None = None,
        error: str | None = None,
):
    if error is not None:
        await message.answer(error)
        return

    try:
        result: MessageId = await message.copy_to(
            chat_id=user_id,
        )
        return MessageConnectionFeedback(
            from_chat_id=message.chat.id,
            from_message_id=message.message_id,
            to_chat_id=user_id,
            to_message_id=result.message_id,
        )
    except TelegramAPIError as ex:
        reason = "Failed to send message from forum group to private chat"
        await logger.aexception(reason)
        await message.reply(f"{reason}, because {ex.__class__.__name__}: {str(ex)}")
