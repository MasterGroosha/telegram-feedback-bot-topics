from uuid import uuid4

from sqlalchemy import UniqueConstraint, select
from sqlalchemy.dialects.postgresql import UUID, BIGINT, BOOLEAN, INTEGER
from sqlalchemy.orm import mapped_column, Mapped

from bot.db.base import Base


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        UniqueConstraint(
            'from_chat_id', 'from_message_id', 'to_chat_id', 'to_message_id',
            name='unique_messages_ids_combinations'
        ),
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    from_chat_id: Mapped[int] = mapped_column(BIGINT, nullable=False)
    from_message_id: Mapped[int] = mapped_column(BIGINT, nullable=False)
    to_chat_id: Mapped[int] = mapped_column(BIGINT, nullable=False)
    to_message_id: Mapped[int] = mapped_column(BIGINT, nullable=False)
    incoming: Mapped[bool] = mapped_column(BOOLEAN, nullable=False)


class Topic(Base):
    __tablename__ = "topics"
    __table_args__ = (
        UniqueConstraint(
            'user_id', 'topic_id',
            name='unique_topics_pairs'
        ),
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(BIGINT, nullable=False)
    topic_id: Mapped[int] = mapped_column(INTEGER, nullable=False)
    first_message_id: Mapped[int] = mapped_column(INTEGER, nullable=False)

    @classmethod
    def find_by_user_id(cls, user_id: int):
        return select(cls).where(Topic.user_id == user_id)
