from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class NotificationOut(BaseModel):
    """Schema for notification output"""

    id: int
    notification_type: str
    title: str
    content: str
    link: Optional[str] = None
    is_read: bool
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationPreferenceOut(BaseModel):
    """Schema for notification preferences output"""

    comment_on_thread: bool
    friend_request_received: bool
    friend_request_accepted: bool
    new_mentee: bool
    event_reminder: bool
    badge_earned: bool
    upvote_received: bool
    mention: bool

    class Config:
        from_attributes = True


class NotificationPreferenceUpdate(BaseModel):
    """Schema for updating notification preferences"""

    comment_on_thread: Optional[bool] = None
    friend_request_received: Optional[bool] = None
    friend_request_accepted: Optional[bool] = None
    new_mentee: Optional[bool] = None
    event_reminder: Optional[bool] = None
    badge_earned: Optional[bool] = None
    upvote_received: Optional[bool] = None
    mention: Optional[bool] = None


class UnreadCountOut(BaseModel):
    """Schema for unread count"""

    unread_count: int
