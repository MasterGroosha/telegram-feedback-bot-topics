import asyncio
from typing import Any, Callable, Dict, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from cachetools import TTLCache


class AlbumsMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.albums_cache = TTLCache(ttl=60.0, maxsize=1000)

    async def delayed_albums_gathering(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            first_event: Message,
            data: Dict[str, Any],
            waiting_time_seconds: int = 3,
    ) -> Awaitable:
        """
        A task which tries to gather all album parts and pushes them to middleware data
        :param handler: aiogram handler
        :param first_event: first message of album
        :param data: aiogram middleware data
        :param waiting_time_seconds: how many seconds to wait until pushing data to handler
        """
        await asyncio.sleep(waiting_time_seconds)
        data["album"] = self.albums_cache[first_event.media_group_id]
        return await handler(first_event, data)

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            print("%s used not for Message, but for %s", self.__class__.__name__, type(event))
            return await handler(event, data)

        event: Message

        # If there is no media_group, just pass through
        if event.media_group_id is None:
            return await handler(event, data)

        # If album cache already exists, add message to it
        if event.media_group_id in self.albums_cache:
            self.albums_cache[event.media_group_id].append(event)

        # If no media_group_id in cache, initialize a new one
        else:
            self.albums_cache[event.media_group_id] = [event]
            # Create delayed task to push the whole album to handler
            asyncio.create_task(self.delayed_albums_gathering(
                handler,
                event,
                data
            ))
        # Drop updates; they will be handled by task
        return
