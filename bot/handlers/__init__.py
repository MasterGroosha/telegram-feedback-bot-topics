from aiogram import Dispatcher, F, Router
from aiogram.enums.chat_type import ChatType
from sqlalchemy.ext.asyncio.session import async_sessionmaker as AsyncSessionmaker

from bot.config_reader import BotSettings
from bot.middlewares import (
    AlbumsMiddleware, BansMiddleware, DbSessionMiddleware,
    TopicsManagementMiddleware, UserTopicContextMiddleware,
    MessageConnectionsMiddleware, EditedMessagesMiddleware
)
from . import errors
from .from_forum import actions_in_forum, free_talk_in_forum
from .from_users import actions_in_pm, free_talk_in_pm


def attach_routers_and_middlewares(
        dispatcher: Dispatcher,
        bot_config: BotSettings,
        sessionmaker: AsyncSessionmaker
) -> None:
    # We always want to have UserTopicContext object and database session object
    # in handlers/filters/middlewares
    dispatcher.update.outer_middleware(UserTopicContextMiddleware())
    dispatcher.update.outer_middleware(DbSessionMiddleware(sessionmaker))

    if bot_config.albums_preserve_enabled:
        dispatcher.message.outer_middleware(
            AlbumsMiddleware(bot_config.albums_wait_time_seconds)
        )

    dispatcher.message.outer_middleware(TopicsManagementMiddleware())
    dispatcher.message.outer_middleware(BansMiddleware())

    # dispatcher.edited_message.outer_middleware(EditedMessagesMiddleware())

    # Common routers
    dispatcher.include_router(errors.router)

    # User -> Forum routers
    pm_router = Router(name="from_users")
    pm_router.message.filter(F.chat.type == ChatType.PRIVATE)

    actions_in_pm_router = actions_in_pm.get_router()
    pm_router.include_router(actions_in_pm_router)

    free_talk_in_pm_router = free_talk_in_pm.get_router()
    free_talk_in_pm_router.edited_message.outer_middleware(EditedMessagesMiddleware())
    free_talk_in_pm_router.message.outer_middleware(MessageConnectionsMiddleware())
    pm_router.include_router(free_talk_in_pm_router)

    dispatcher.include_router(pm_router)

    # Forum -> User routers
    forum_router = Router(name="from_forum")
    forum_router.message.filter(F.chat.id == dispatcher.workflow_data["forum_chat_id"])
    forum_router.edited_message.filter(F.chat.id == dispatcher.workflow_data["forum_chat_id"])

    actions_in_forum_router = actions_in_forum.get_router()
    forum_router.include_router(actions_in_forum_router)

    free_talk_in_forum_router = free_talk_in_forum.get_router()
    free_talk_in_forum_router.edited_message.middleware(EditedMessagesMiddleware())
    free_talk_in_forum_router.message.middleware(MessageConnectionsMiddleware())
    forum_router.include_router(free_talk_in_forum_router)

    dispatcher.include_router(forum_router)
