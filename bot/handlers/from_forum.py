import structlog
from aiogram import Router, F
from aiogram.filters import MagicData, Command
from aiogram.types import Message

from bot.config_reader import config

router = Router(name="Forum Router")
log: structlog.BoundLogger = structlog.get_logger()

# This router should only work in forum supergroup
router.message.filter(F.chat.id == config.forum_supergroup_id)


@router.message(MagicData(F.user_id.is_(None)))
async def no_user_id(message: Message):
    """
    Handler to messages when no `user_id` is passed via middlewares.
    This basically means that our code could not find user_id to send message to.

    :param message: message from Telegram
    """
    await message.answer("Error: couldn't find corresponding user_id. Message cannot be delivered")


@router.message(Command(commands="note", prefix="!"))
async def note(message: Message):
    """
    Handler to messages which start with "!note" command.
    Such messages should be ignored.

    :param message: any message which text or caption starts with "!note"
    """
    return


@router.message()
async def any_message(message: Message, user_id: int, reply_to_id: int | None = None):
    """
    Handler to messages from forum supergroup when user_id is known,
    hence bot sends message to user's PM

    :param message: message from Telegram
    :param user_id: user id to send message to
    :param reply_to_id: if not None, this message should be a reply in user's PM
    :return: sent message object to save in DB later
    """
    msg: Message = await message.send_copy(
        chat_id=user_id,
        reply_to_message_id=reply_to_id,
        allow_sending_without_reply=True
    )
    return msg
