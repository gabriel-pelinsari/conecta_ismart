from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class UniversityGroupBase(BaseModel):
    """Base schema for university group"""
    university_name: str = Field(..., max_length=100)
    name: str = Field(..., max_length=200)
    description: Optional[str] = None


class UniversityGroupOut(BaseModel):
    """Schema for university group output"""
    id: int
    university_name: str
    name: str
    description: Optional[str] = None
    member_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UniversityGroupMemberOut(BaseModel):
    """Schema for group member information"""
    user_id: int
    full_name: str
    nickname: Optional[str] = None
    course: Optional[str] = None
    semester: Optional[str] = None
    photo_url: Optional[str] = None
    joined_at: datetime

    class Config:
        from_attributes = True


class UniversityGroupStatsOut(BaseModel):
    """Schema for group statistics"""
    total_members: int
    active_members: int  # Members who posted in last 30 days
    threads_count: int
    events_count: int


class MyGroupOut(BaseModel):
    """Schema for user's own group"""
    group: Optional[UniversityGroupOut] = None
    is_member: bool
    joined_at: Optional[datetime] = None
