from aiogram import F, Router
from aiogram.enums import ChatType

from . import (
    pm_commands, pm_talk,
    group_commands,
)

from bot.middlewares import TopicFinderUserToGroup


def get_routers(
        supergroup_id: int,
) -> list[Router]:
    pm_router = Router()
    pm_router.message.filter(F.chat.type == ChatType.PRIVATE)
    pm_router.include_routers(
        pm_commands.router,
        pm_talk.router
    )
    pm_talk.router.message.middleware(TopicFinderUserToGroup())

    group_router = Router()
    group_router.message.filter(F.chat.id == supergroup_id)
    group_router.include_router(group_commands.router)


    return [
        pm_router,
        group_router,
    ]

