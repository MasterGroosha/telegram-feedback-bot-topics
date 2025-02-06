from typing import Callable, Awaitable, Dict, Any

import structlog
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from sqlalchemy.ext.asyncio import AsyncSession
from structlog.types import FilteringBoundLogger

from bot.db.models import MessageConnection
from bot.handlers_feedback import MessageConnectionFeedback

logger: FilteringBoundLogger = structlog.get_logger()


class ConnectionMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        raise NotImplementedError()

    @staticmethod
    async def create_new_message_connection(
            message_connection: MessageConnectionFeedback,
            session: AsyncSession,
    ):
        new_obj = MessageConnection(
            from_chat_id=message_connection.from_chat_id,
            from_message_id=message_connection.from_message_id,
            to_chat_id=message_connection.to_chat_id,
            to_message_id=message_connection.to_message_id,
        )
        session.add(new_obj)
        try:
            await session.commit()
            await logger.adebug(
                f"Successfully saved messages pair to database",
                details=new_obj.as_dict(),
            )
        except:
            await logger.aexception("Failed to save messages pair to database")


    @staticmethod
    async def find_message_pair(
            message: Message,
            session: AsyncSession,
    ) -> MessageConnection | None:
        query = MessageConnection.find_pair_message(
            message.chat.id,
            message.message_id,
            originated_from_user=True,
        )
        search_result = await session.execute(query)
        pair = search_result.scalar_one_or_none()
        if pair is not None:
            await logger.adebug(
                "Found pair message",
                details=pair.as_dict(),
            )
            return pair
        return None


    @staticmethod
    async def find_replied_message_pair(
            reply_message: Message,
            session: AsyncSession,
    ) -> MessageConnection | None:
        is_reply_to_user_message = not reply_message.from_user.is_bot
        query = MessageConnection.find_pair_message(
            reply_message.chat.id,
            reply_message.message_id,
            is_reply_to_user_message,
        )
        search_result = await session.execute(query)
        reply_pair = search_result.scalar_one_or_none()
        if reply_pair is not None:
            await logger.adebug(
                "Found reply message",
                details=reply_pair.as_dict(),
            )
            if is_reply_to_user_message:
                reply_id = reply_pair.to_message_id
            else:
                reply_id = reply_pair.from_message_id
            return reply_id
        return None