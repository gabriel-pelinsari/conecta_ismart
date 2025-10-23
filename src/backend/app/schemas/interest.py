from pydantic import BaseModel, Field
from typing import List

class InterestBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)

class InterestCreate(InterestBase):
    pass

class InterestOut(InterestBase):
    id: int
    
    class Config:
        from_attributes = True

class UserInterestsOut(BaseModel):
    """Lista de interesses do usuário"""
    interests: List[InterestOut] = []