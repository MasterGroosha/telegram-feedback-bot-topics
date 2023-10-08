from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import Ban, Topic, Message


async def find_topic_entry(
        session: AsyncSession,
        *,
        user_id: int = None,
        topic_id: int = None
) -> Topic | None:
    """
    Поиск топика по user_id или topic_id

    :param session: сессия SQLAlchemy
    :param user_id: [keyword-only] айди юзера в Telegram
    :param topic_id: [keyword-only] айди топика в Telegram
    :return: объект Topic или None, если топик не найден
    """
    if user_id is None and topic_id is None:
        raise ValueError("You must specify either user_id or topic_id filter")
    if user_id and topic_id:
        raise ValueError("Exactly one filter is required")

    if user_id is not None:
        statement = select(Topic).where(Topic.user_id == user_id)
    else:
        statement = select(Topic).where(Topic.topic_id == topic_id)
    return await session.scalar(statement)


async def get_message_pair(
        session: AsyncSession,
        is_from_bot: bool,
        chat_id: int,
        message_id: int
) -> Message | None:
    """
    Поиск пары сообщений (отправлено юзером - отправлено ботом)

    :param session: сессия SQLAlchemy
    :param is_from_bot: флаг, указывающий на то, кем было отправлено сообщение: юзером или ботом
    :param chat_id: айди чата в Telegram
    :param message_id: айди сообщения в Telegram
    :return: объект Message или None, если не удалось найти сообщение по заданному фильтру
    """
    if is_from_bot:
        statement = select(Message).where(Message.to_chat_id == chat_id, Message.to_message_id == message_id)
    else:
        statement = select(Message).where(Message.from_chat_id == chat_id, Message.from_message_id == message_id)
    return await session.scalar(statement)


async def add_messages_pairs(
        session: AsyncSession,
        messages_data: list[dict],
):
    """
    Создание новой записи о пары сообщений

    :param session: SQLAlchemy session
    :param messages_data: list of messages' properties
    """
    for item in messages_data:
        new_message_data = Message(
            incoming=item["incoming"],
            from_chat_id=item["from_chat_id"],
            from_message_id=item["from_message_id"],
            to_chat_id=item["to_chat_id"],
            to_message_id=item["to_message_id"]
        )
        session.add(new_message_data)
    await session.commit()


async def get_ban_status(
        session: AsyncSession,
        user_id: int
) -> Ban | None:
    statement = select(Ban).where(Ban.user_id == user_id)
    return await session.scalar(statement)


async def ban_or_shadowban(
        session: AsyncSession,
        existing_object: Ban | None,
        user_id: int,
        is_shadowban: bool = False
):
    # Choose attribute to update
    if is_shadowban:
        attr = "is_shadowbanned"
    else:
        attr = "is_banned"

    # Update existing object if passed
    if existing_object:
        setattr(existing_object, attr, True)
    else:
        new_ban = Ban(
            user_id=user_id
        )
        setattr(new_ban, attr, True)
        session.add(new_ban)

    try:
        await session.commit()
    except Exception as ex:
        # todo: log error
        raise ex
