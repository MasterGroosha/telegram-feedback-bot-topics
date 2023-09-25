from aiogram import Router, F

from . import from_forum
from . import from_users
from . import message_edits
from . import transfer_messages
from bot.config_reader import BotSettings


def get_shared_router() -> Router:
    shared_router = Router(name="Shared Router")

    # Attach routers to this router
    shared_router.include_routers(
        transfer_messages.router,
        # from_users.router,
        # from_forum.router,
        message_edits.router
    )
    return shared_router
