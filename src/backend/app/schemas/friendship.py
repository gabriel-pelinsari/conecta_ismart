from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class FriendshipBase(BaseModel):
    """Base schema for friendship"""
    pass


class FriendOut(BaseModel):
    """Schema for friend information"""
    user_id: int
    full_name: str
    nickname: Optional[str] = None
    university: Optional[str] = None
    course: Optional[str] = None
    semester: Optional[str] = None
    photo_url: Optional[str] = None
    status: str  # 'accepted', 'pending'
    created_at: datetime

    class Config:
        from_attributes = True


class FriendRequestOut(BaseModel):
    """Schema for pending friend request"""
    user_id: int
    full_name: str
    nickname: Optional[str] = None
    university: Optional[str] = None
    photo_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FriendshipResponse(BaseModel):
    """Generic friendship operation response"""
    status: str
    message: str


class FriendListResponse(BaseModel):
    """Response for list of friends"""
    friends: List[FriendOut]
    total: int
