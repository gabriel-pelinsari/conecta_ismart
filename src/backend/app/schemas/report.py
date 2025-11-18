from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ReportCreate(BaseModel):
    """Schema for creating a report"""

    target_type: str = Field(..., pattern="^(thread|comment|user)$")
    target_id: int = Field(..., gt=0)
    category: str = Field(
        ...,
        pattern="^(spam|offensive|harassment|inappropriate|fake|other)$",
    )
    description: Optional[str] = Field(None, max_length=1000)


class ReportOut(BaseModel):
    """Schema for report output"""

    id: int
    reporter_id: int
    target_type: str
    target_id: int
    category: str
    description: Optional[str] = None
    status: str
    admin_notes: Optional[str] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReportUpdate(BaseModel):
    """Schema for updating report status (admin only)"""

    status: str = Field(..., pattern="^(pending|reviewed|approved|rejected)$")
    admin_notes: Optional[str] = Field(None, max_length=1000)


class ReportResponse(BaseModel):
    """Generic report operation response"""

    status: str
    message: str
    report_id: Optional[int] = None
