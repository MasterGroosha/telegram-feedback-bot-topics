import structlog
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message


router = Router(name="Users router")
log: structlog.BoundLogger = structlog.get_logger()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Handler to /start commands in PM with user

    :param message: message from Telegram
    """
    await message.answer("% start command message %")


@router.message()
async def any_message(
        message: Message,
        topic_id: int,
        forum_chat_id: int,
        reply_to_id: int | None = None):
    """
    Handler to any other message in PM with user

    :param message: message from Telegram
    :param topic_id: forum supergroup's topic to send message to
    :param forum_chat_id: forum supergroup's ID
    :param reply_to_id: if not None, this message should be a reply in forum supergroup topic
    :return: sent message object to save in DB later
    """
    msg: Message = await message.send_copy(
        chat_id=forum_chat_id,
        message_thread_id=topic_id,
        reply_to_message_id=reply_to_id,
        allow_sending_without_reply=True
    )
    return msg
