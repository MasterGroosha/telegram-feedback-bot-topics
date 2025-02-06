from datetime import datetime, timezone

from pydantic import BaseModel


class MessageConnectionFeedback(BaseModel):
    from_chat_id: int
    from_message_id: int
    to_chat_id: int
    to_message_id: int
    created_at: datetime = datetime.now(timezone.utc)
