import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="forum_router")
log: structlog.BoundLogger = structlog.get_logger()


@router.message(Command(commands="note", prefix="!"))
async def note(message: Message):
    """
    Handler to messages which start with "!note" command.
    Such messages should be ignored.

    :param message: any message which text or caption starts with "!note"
    """
    return


@router.message(Command("ban"))
async def cmd_ban(message: Message):
    pass


@router.message(Command("shadowban"))
async def cmd_shadowban(message: Message):
    pass
