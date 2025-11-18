from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class MentorshipOut(BaseModel):
    """Schema for mentorship output"""

    id: int
    mentor_id: int
    mentee_id: int
    status: str
    compatibility_score: Optional[float] = None
    matched_at: datetime
    completed_at: Optional[datetime] = None

    # Enriched fields
    mentor_name: Optional[str] = None
    mentee_name: Optional[str] = None
    mentor_photo: Optional[str] = None
    mentee_photo: Optional[str] = None

    class Config:
        from_attributes = True


class MentorshipRequestResponse(BaseModel):
    """Response for mentor request"""

    status: str
    message: str
    mentor_id: Optional[int] = None
    compatibility: Optional[float] = None


class MentorOut(BaseModel):
    """Schema for available mentor"""

    user_id: int
    full_name: str
    university: Optional[str] = None
    course: Optional[str] = None
    semester: Optional[str] = None
    photo_url: Optional[str] = None
    active_mentees: int
    available_slots: int


class QueuePositionOut(BaseModel):
    """Schema for queue position"""

    position: int
    total_in_queue: int
    requested_at: datetime
