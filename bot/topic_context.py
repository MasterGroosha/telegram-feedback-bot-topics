from enum import Enum, auto

from aiogram import html
from aiogram.types import User
from fluent.runtime import FluentLocalization
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import Ban, Topic


class MessageDirection(str, Enum):
    TO_USER = auto()
    TO_FORUM = auto()


class TopicContext:
    def __init__(
            self,
            direction: MessageDirection,
            session: AsyncSession,
            topic: Topic,
            user: User | None = None
    ):
        self.direction = direction
        self.session = session
        self.topic = topic
        self.user = user

    @staticmethod
    def make_first_topic_message(
            l10n: FluentLocalization,
            user: User,
            ban_entry: Ban | None = None
    ) -> str:
        # Objects for "no" and "yes" strings
        no = l10n.format_value("no", {"capitalization": "lowercase"})
        yes = l10n.format_value("yes", {"capitalization": "lowercase"})

        username = f"@{user.username}" if user.username else no
        language_code = user.language_code if user.language_code else no
        has_premium = yes if user.is_premium else no

        if ban_entry is None:
            ban_status = no
        else:
            if ban_entry.is_shadowbanned:
                ban_type = l10n.format_value("status-shadowban")
            elif ban_entry.is_banned:
                ban_type = l10n.format_value("status-ban")
            else:
                ban_type = l10n.format_value("status-unknown")
            ban_status = f"{yes} ({ban_type})"

        text = l10n.format_value(
            "new-topic-intro",
            {
                "name": html.quote(user.full_name),
                "ban_status": ban_status,
                "id": user.id,
                "username": username,
                "language_code": language_code,
                "has_premium": has_premium
            }
        )
        return text
