from aiogram import Router

from bot.handlers.from_users import router as users_router
from bot.handlers.from_forum import router as forum_router
from bot.handlers.message_edits import router as edit_router

router = Router(name="Talk Router [common]")

router.include_routers(users_router, forum_router, edit_router)
