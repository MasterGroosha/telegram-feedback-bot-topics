import structlog
from aiogram import Router, Bot
from aiogram.types import Message

router = Router(name="Edited messages router")
log: structlog.BoundLogger = structlog.get_logger()


@router.edited_message()
async def any_edited_message(
        message: Message,
        bot: Bot,
        edit_chat_id: int | None = None,
        edit_message_id: int | None = None
):
    if edit_message_id:
        await bot.edit_message_text(
            chat_id=edit_chat_id,
            message_id=edit_message_id,
            text=message.text
        )
