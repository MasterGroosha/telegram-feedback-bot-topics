from aiogram.enums import ContentType
from aiogram.filters import BaseFilter
from aiogram.types import Message


class ServiceMessagesFilter(BaseFilter):
    service_types: set = {
        ContentType.FORUM_TOPIC_CREATED,
        ContentType.FORUM_TOPIC_EDITED,
        ContentType.FORUM_TOPIC_CLOSED,
        ContentType.FORUM_TOPIC_REOPENED,
        ContentType.PINNED_MESSAGE,
        ContentType.MESSAGE_AUTO_DELETE_TIMER_CHANGED,
        ContentType.NEW_CHAT_PHOTO,
        ContentType.DELETE_CHAT_PHOTO,
        ContentType.NEW_CHAT_TITLE,
        ContentType.CHAT_BACKGROUND_SET,
        ContentType.USER_SHARED,
        ContentType.CHAT_SHARED,
    }

    async def __call__(self, message: Message) -> bool | dict:
        return message.content_type in self.service_types
