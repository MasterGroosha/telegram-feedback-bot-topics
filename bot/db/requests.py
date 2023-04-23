from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import Topic, Message


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


async def add_topic(
        session: AsyncSession,
        user_id: int,
        topic_id: int,
        first_message_id: int
):
    """
    Добавление топика в БД

    :param session: сессия SQLAlchemy
    :param user_id: айди юзера в Telegram
    :param topic_id: айди топика в Telegram
    :param first_message_id: айди первого сообщения в созданном топике
    """
    new_topic = Topic(user_id=user_id, topic_id=topic_id, first_message_id=first_message_id)
    session.add(new_topic)
    await session.commit()


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


async def add_message_pair(
        session: AsyncSession,
        incoming: bool,
        from_chat_id: int,
        from_message_id: int,
        to_chat_id: int,
        to_message_id: int
):
    """
    Создание новой записи о пары сообщений

    :param session: сессия SQLAlchemy
    :param incoming: если сообщение отправлено юзером в супергруппу-форум, то True. Иначе False
    :param from_chat_id: айди чата, откуда отправлено сообщения
    :param from_message_id: айди отправленного сообщения
    :param to_chat_id: айди чата, куда пришла копия сообщения
    :param to_message_id: айди сообщения-копии
    """
    new_message_data = Message(
        incoming=incoming,
        from_chat_id=from_chat_id,
        from_message_id=from_message_id,
        to_chat_id=to_chat_id,
        to_message_id=to_message_id
    )
    session.add(new_message_data)
    await session.commit()
