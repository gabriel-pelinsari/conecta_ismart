from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class EventCreate(BaseModel):
    """Schema for creating an event"""

    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    event_type: str = Field(..., pattern="^(workshop|meetup|study_group|networking|webinar|other)$")
    start_datetime: datetime
    end_datetime: datetime
    location: Optional[str] = Field(None, max_length=300)
    is_online: bool = False
    online_link: Optional[str] = Field(None, max_length=500)
    university: Optional[str] = Field(None, max_length=100)
    max_participants: Optional[int] = Field(None, gt=0)


class EventUpdate(BaseModel):
    """Schema for updating an event"""

    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    event_type: Optional[str] = Field(None, pattern="^(workshop|meetup|study_group|networking|webinar|other)$")
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=300)
    is_online: Optional[bool] = None
    online_link: Optional[str] = Field(None, max_length=500)
    max_participants: Optional[int] = Field(None, gt=0)


class EventOut(BaseModel):
    """Schema for event output"""

    id: int
    title: str
    description: Optional[str] = None
    event_type: str
    start_datetime: datetime
    end_datetime: datetime
    location: Optional[str] = None
    is_online: bool
    online_link: Optional[str] = None
    university: Optional[str] = None
    max_participants: Optional[int] = None
    created_by: int
    is_cancelled: bool
    cancelled_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Stats (serão preenchidos se solicitado)
    participant_count: Optional[int] = 0
    user_rsvp_status: Optional[str] = None

    class Config:
        from_attributes = True


class EventRSVP(BaseModel):
    """Schema for RSVP to event"""

    status: str = Field(..., pattern="^(confirmed|maybe|declined)$")


class EventStatsOut(BaseModel):
    """Schema for event statistics"""

    confirmed: int
    maybe: int
    declined: int
    attended: int
    total_rsvp: int


class ParticipantOut(BaseModel):
    """Schema for event participant"""

    user_id: int
    full_name: Optional[str] = None
    photo_url: Optional[str] = None
    status: str
    attended: bool
    joined_at: datetime
