from pydantic import BaseModel, EmailStr
from typing import List
from uuid import UUID
from datetime import datetime

# Schema para resposta de email pendente
class PendingEmailResponse(BaseModel):
    id: UUID
    email: str
    created_at: datetime
    expires_at: datetime
    
    class Config:
        from_attributes = True

# Schema para upload em massa
class EmailListResponse(BaseModel):
    success_count: int
    error_count: int
    errors: List[dict] = []
    message: str
    
    class Config:
        from_attributes = True