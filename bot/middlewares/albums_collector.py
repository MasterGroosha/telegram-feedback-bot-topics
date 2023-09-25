import asyncio
from typing import Any, Callable, Dict, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from cachetools import TTLCache


class AlbumsMiddleware(BaseMiddleware):
    def __init__(self, wait_time_seconds: int):
        super().__init__()
        self.wait_time_seconds = wait_time_seconds
        self.albums_cache = TTLCache(
            ttl=float(wait_time_seconds) + 20.0,
            maxsize=1000
        )
        self.lock = asyncio.Lock()

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

        # If there is no media_group
        # just pass update further
        if event.media_group_id is None:
            return await handler(event, data)

        album_id: str = event.media_group_id

        async with self.lock:
            self.albums_cache.setdefault(album_id, list())
            self.albums_cache[album_id].append(event)

        # Wait for some time until other updates are collected
        await asyncio.sleep(self.wait_time_seconds)

        # Find the smallest message_id in batch, this will be our only update
        # which will pass to handlers
        my_message_id = smallest_message_id = event.message_id

        item: Message
        for item in self.albums_cache[album_id]:
            smallest_message_id = min(smallest_message_id, item.message_id)

        # If current message_id in not the smallest, drop the update;
        # it's already saved in self.albums_cache
        if my_message_id != smallest_message_id:
            return

        # If current message_id is the smallest,
        # add all other messages to data and pass to handler
        data.update(album=self.albums_cache[album_id])

        return await handler(event, data)
