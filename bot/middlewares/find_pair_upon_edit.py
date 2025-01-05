from typing import Callable, Awaitable, Dict, Any

import structlog
from aiogram.types import TelegramObject, Message
from fluent.runtime import FluentLocalization
from sqlalchemy.ext.asyncio import AsyncSession
from structlog.types import FilteringBoundLogger

from bot.middlewares import ConnectionMiddleware

logger: FilteringBoundLogger = structlog.get_logger()


class FindPairToEditMiddleware(ConnectionMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        session: AsyncSession = data["session"]
        l10n: FluentLocalization = data["l10n"]

        pair = await self.find_message_pair(
            message=event,
            session=session,
        )
        if pair is None:
            data["error"] = l10n.format_value("error-cannot-find-pair-to-edit")
        else:
            data["edit_chat_id"] = pair.to_chat_id
            data["edit_message_id"] = pair.to_message_id

        return await handler(event, data)
