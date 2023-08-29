from aiogram import Router, F

from . import from_forum
from . import from_users
from . import message_edits
from bot.config_reader import BotSettings


def get_shared_router(bot_config: BotSettings) -> Router:
    shared_router = Router(name="Shared Router")

    # Add filters
    from_users.router.message.filter(F.chat.type == "private")
    from_forum.router.message.filter(F.chat.id == bot_config.forum_supergroup_id)

    # Attach routers to this router
    shared_router.include_routers(
        from_users.router,
        from_forum.router,
        message_edits.router
    )
    return shared_router
