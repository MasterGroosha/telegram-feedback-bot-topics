from aiogram import F, Router

from bot.config_reader import BotSettings
from bot.middlewares import (
    AlbumsMiddleware, TopicsManagementMiddleware,
    MessageConnectionsMiddleware, EditedMessagesMiddleware
)
from . import actions_in_forum
from . import actions_in_pm
from . import message_edits
from . import transfer_messages


def get_router(bot_config: BotSettings) -> Router:
    main_router = Router(name="all_updates_router")

    actions_in_forum.router.message.filter(F.chat.id == bot_config.forum_supergroup_id)
    actions_in_pm.router.message.filter(F.chat.type == "private")

    if bot_config.albums_preserve_enabled:
        transfer_messages.router.message.outer_middleware(
            AlbumsMiddleware(bot_config.albums_wait_time_seconds)
        )
    transfer_messages.router.message.outer_middleware(
        TopicsManagementMiddleware()
    )
    transfer_messages.router.message.outer_middleware(
        MessageConnectionsMiddleware()
    )
    transfer_messages.router.edited_message.outer_middleware(
        EditedMessagesMiddleware()
    )

    # Attach other routers to main router
    main_router.include_routers(
        actions_in_forum.router,
        actions_in_pm.router,
        transfer_messages.router,
        message_edits.router
    )
    return main_router
