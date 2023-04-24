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

    await bot.edit_message_text(
        chat_id=edit_chat_id,
        message_id=edit_message_id,
        text=message.text
    )
