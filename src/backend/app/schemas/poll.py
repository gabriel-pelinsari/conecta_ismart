from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PollOptionOut(BaseModel):
    id: int
    label: str
    votes_count: int = 0

    class Config:
        from_attributes = True


class PollCreatorOut(BaseModel):
    user_id: int
    nickname: Optional[str] = None
    full_name: Optional[str] = None
    university: Optional[str] = None


class PollCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    audience: str = Field(default="geral", pattern="^(geral|faculdade)$")
    options: List[str] = Field(
        ..., min_length=2, description="Lista de op��es da enquete"
    )


class PollVoteRequest(BaseModel):
    option_label: Optional[str] = Field(
        None, description="Label da op��o selecionada ou vazio para remover o voto"
    )


class PollOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    audience: str
    created_at: datetime
    creator: PollCreatorOut
    options: List[PollOptionOut]
    user_vote: Optional[str] = None

    class Config:
        from_attributes = True
