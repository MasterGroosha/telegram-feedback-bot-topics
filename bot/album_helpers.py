from aiogram.types import Message, InputMediaPhoto, InputMediaVideo, InputMediaAudio, InputMediaDocument


def make_album_part(message: Message) \
        -> InputMediaPhoto | InputMediaVideo | InputMediaAudio | InputMediaDocument | None:
    if message.photo:
        return InputMediaPhoto(media=message.photo[-1].file_id, caption=message.caption)
    if message.video:
        return InputMediaVideo(media=message.video.file_id, caption=message.caption)
    if message.audio:
        return InputMediaAudio(media=message.audio.file_id, caption=message.caption)
    if message.document:
        return InputMediaDocument(media=message.document.file_id, caption=message.caption)
    return None


def make_new_album(messages: list[Message]) \
        -> list[InputMediaPhoto | InputMediaVideo | InputMediaAudio | InputMediaDocument]:
    media = list()
    for message in messages:
        item = make_album_part(message)
        if item is not None:
            media.append(item)
    return media
