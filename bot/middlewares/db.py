from typing import Callable, Awaitable, Dict, Any

import structlog
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from bot.user_topic_context import UserTopicContext

logger: structlog.BoundLogger = structlog.get_logger()


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        session: AsyncSession
        async with self.session_pool() as session:
            context: UserTopicContext = data["context"]
            context.session = session

            await logger.adebug(
                event="Added session to context"
            )

            return await handler(event, data)
