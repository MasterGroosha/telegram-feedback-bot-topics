from aiogram import F, Router
from aiogram.enums import ChatType

from . import (
    pm_commands, pm_talk,
    group_commands, group_talk
)

from bot.middlewares import TopicFinderUserToGroup, GroupToUserMiddleware, FindPairToEditMiddleware


def get_routers(
        supergroup_id: int,
) -> list[Router]:
    pm_router = Router()
    pm_router.message.filter(F.chat.type == ChatType.PRIVATE)
    pm_router.edited_message.filter(F.chat.type == ChatType.PRIVATE)
    pm_router.include_routers(
        pm_commands.router,
        pm_talk.router
    )
    pm_talk.router.message.middleware(TopicFinderUserToGroup(forum_chat_id=supergroup_id))
    pm_talk.router.edited_message.middleware(FindPairToEditMiddleware())

    group_router = Router()
    group_router.message.filter(F.chat.id == supergroup_id)
    group_router.edited_message.filter(F.chat.id == supergroup_id)
    group_router.include_routers(
        group_commands.router,
        group_talk.router
    )
    group_talk.router.message.middleware(GroupToUserMiddleware())
    group_talk.router.edited_message.middleware(FindPairToEditMiddleware())


    return [
        pm_router,
        group_router,
    ]

