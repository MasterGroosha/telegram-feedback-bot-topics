from enum import Enum, auto

import structlog
from aiogram import html, Bot
from aiogram.enums import ContentType, ParseMode
from aiogram.types import Message, User, ChatMemberMember
from fluent.runtime import FluentLocalization
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import Ban, Message as DBMessage, Topic

logger: structlog.BoundLogger = structlog.get_logger()


class MessageDirection(str, Enum):
    FORUM_TO_USER = auto()
    USER_TO_FORUM = auto()
    UNKNOWN = auto()


class UserTopicContext:
    def __init__(self, caller: User):
        self.caller = caller
        self.message_direction: MessageDirection | None = None
        self.session: AsyncSession | None = None
        self.topic_entry: Topic | None = None
        self.ban_entry: Ban | None = None
        self.edit_chat_id: int | None = None
        self.edit_message_id: int | None = None
        self.reply_to_id: int | None = None
        self.album: list[Message] | None = None

    @staticmethod
    def is_service_message(message: Message) -> bool:
        return message.content_type in {
            ContentType.NEW_CHAT_MEMBERS, ContentType.LEFT_CHAT_MEMBER,
            ContentType.NEW_CHAT_TITLE,
            ContentType.NEW_CHAT_PHOTO, ContentType.DELETE_CHAT_PHOTO,
            ContentType.GROUP_CHAT_CREATED, ContentType.SUPERGROUP_CHAT_CREATED, ContentType.CHANNEL_CHAT_CREATED,
            ContentType.MESSAGE_AUTO_DELETE_TIMER_CHANGED,
            ContentType.MIGRATE_TO_CHAT_ID, ContentType.MIGRATE_FROM_CHAT_ID,
            ContentType.PINNED_MESSAGE,
            ContentType.SUCCESSFUL_PAYMENT,
            ContentType.USER_SHARED, ContentType.CHAT_SHARED,
            ContentType.WRITE_ACCESS_ALLOWED,
            ContentType.PROXIMITY_ALERT_TRIGGERED,
            ContentType.FORUM_TOPIC_CREATED, ContentType.FORUM_TOPIC_EDITED,
            ContentType.FORUM_TOPIC_CLOSED, ContentType.FORUM_TOPIC_REOPENED,
            ContentType.GENERAL_FORUM_TOPIC_HIDDEN, ContentType.GENERAL_FORUM_TOPIC_UNHIDDEN,
            ContentType.VIDEO_CHAT_SCHEDULED, ContentType.VIDEO_CHAT_STARTED,
            ContentType.VIDEO_CHAT_ENDED, ContentType.VIDEO_CHAT_PARTICIPANTS_INVITED,
            ContentType.WEB_APP_DATA,
            ContentType.UNKNOWN
        }

    async def get_ban_entry(
            self,
            user_id: int
    ) -> Ban | None:
        statement = select(Ban).where(Ban.user_id == user_id)
        ban_entry = await self.session.scalar(statement)
        self.ban_entry = ban_entry
        return ban_entry

    async def get_message_pair(
            self,
            is_from_bot: bool,
            chat_id: int,
            message_id: int
    ) -> DBMessage | None:
        """
        Search messages pair (sent by user <--> sent by bot)

        :param is_from_bot: author of message (True - bot; False - user)
        :param chat_id: Telegram chat id
        :param message_id: Telegram message id
        :return: a single Message object or None, if no data found with this filter
        """
        if is_from_bot:
            statement = (
                select(DBMessage)
                .where(
                    DBMessage.to_chat_id == chat_id,
                    DBMessage.to_message_id == message_id
                )
            )
        else:
            statement = (
                select(DBMessage)
                .where(
                    DBMessage.from_chat_id == chat_id,
                    DBMessage.from_message_id == message_id
                )
            )
        return await self.session.scalar(statement)

    async def add_messages_pairs(
            self,
            messages_data: list[dict],
    ):
        """
        Creates new messages connections entries in database

        :param messages_data: list of messages' properties
        """
        for item in messages_data:
            new_message_data = DBMessage(
                incoming=item["incoming"],
                from_chat_id=item["from_chat_id"],
                from_message_id=item["from_message_id"],
                to_chat_id=item["to_chat_id"],
                to_message_id=item["to_message_id"]
            )
            self.session.add(new_message_data)
        try:
            await self.session.commit()
        except Exception as ex:
            await logger.aerror(
                event="Failed to write messages connections to DB",
                exception_type=type(ex),
                exception_text=str(ex),
                messages_count=len(messages_data),
                messages_data=messages_data
            )

    async def ban_or_shadowban(
            self,
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
        if existing_object is not None:
            # Remove "is_banned" if we are going to shadowban to prevent "double ban"
            if attr == "is_shadowbanned" and existing_object.is_banned is True:
                existing_object.is_banned = False
            setattr(existing_object, attr, True)
            new_ban_entry = existing_object
        else:
            new_ban = Ban(
                user_id=user_id
            )
            setattr(new_ban, attr, True)
            self.session.add(new_ban)
            new_ban_entry = new_ban

        try:
            await self.session.commit()
            self.ban_entry = new_ban_entry
        except Exception as ex:
            await logger.aerror(
                event="Failed to (shadow)ban user",
                ban_type=attr.replace("is_", "").replace("ned", ""),
                user_id=user_id,
                exception_type=type(ex),
                exception_text=str(ex)
            )
            raise ex

    async def unban(
            self,
            existing_object: Ban
    ):
        await self.session.delete(existing_object)
        try:
            await self.session.commit()
            self.ban_entry = None
        except Exception as ex:
            await logger.aerror(
                event="Failed to unban user",
                user_id=existing_object.user_id,
                exception_type=type(ex),
                exception_text=str(ex)
            )
            raise ex

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
                ban_type = l10n.format_value("ban-status-shadowban")
            elif ban_entry.is_banned:
                ban_type = l10n.format_value("ban-status-ban")
            else:
                ban_type = l10n.format_value("ban-status-unknown")
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

    async def update_first_topic_message(
            self,
            bot: Bot,
            l10n: FluentLocalization,
            chat_id: int
    ):
        user_chat: ChatMemberMember = await bot.get_chat_member(
            chat_id=self.topic_entry.user_id,
            user_id=self.topic_entry.user_id
        )
        new_first_message_text = self.make_first_topic_message(
            l10n=l10n,
            user=user_chat.user,
            ban_entry=self.ban_entry
        )
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=self.topic_entry.first_message_id,
            text=new_first_message_text,
            parse_mode=ParseMode.HTML
        )
