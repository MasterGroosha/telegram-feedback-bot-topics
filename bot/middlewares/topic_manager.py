from typing import cast, Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from bot.db.models import Topic


class TopicFinderUserToGroup(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        session: AsyncSession = data["session"]
        user_id = event.from_user.id

        result = await session.execute(Topic.find_by_user_id(user_id))
        topic = result.scalar_one_or_none()

        return await handler(event, data)
        # cast(Message, event)
        # topic_object = await Topic.find_by_user_id()
