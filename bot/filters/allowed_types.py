from aiogram.enums import ContentType
from aiogram.filters import BaseFilter
from aiogram.types import Message


class ForwardableTypesFilter(BaseFilter):
    types_with_caption: set = {
        ContentType.ANIMATION,
        ContentType.AUDIO,
        ContentType.DOCUMENT,
        ContentType.PAID_MEDIA,
        ContentType.PHOTO,
        ContentType.VIDEO,
        ContentType.VOICE,
    }
    types_without_caption: set = {
        ContentType.CONTACT,
        ContentType.LOCATION,
        ContentType.STICKER,
        ContentType.STORY,
        ContentType.VENUE,
        ContentType.VIDEO_NOTE,
    }

    async def __call__(self, message: Message) -> bool | dict:
        # Most likely, a message contain just text,
        # so check this first before other types.
        if message.text is not None:
            return True

        # Next, check for media, which can contain caption.
        # If there is caption, we need to return its length.
        if message.content_type in self.types_with_caption:
            if message.caption is None:
                return True
            return {"caption_length": len(message.caption)}

        # Finally, media, which have no captions and which are "static" (unlike dice),
        # can be forwarded without any issues
        if message.content_type in self.types_without_caption:
            return True

        # All other types (games, polls, dice, invoices, service messages etc.)
        # Are not allowed
        return False
