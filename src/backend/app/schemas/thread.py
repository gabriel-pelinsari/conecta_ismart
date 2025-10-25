# app/schemas/thread.py
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict  # ⬅ novo
from datetime import datetime
from app.schemas.user import UserOut

# === VOTOS ===
class VoteIn(BaseModel):
    value: int  # 1 para upvote, -1 para downvote

# === COMENTÁRIOS ===
class CommentBase(BaseModel):
    content: str = Field(..., min_length=3, max_length=5000)

class CommentCreate(CommentBase):
    pass

class CommentOut(CommentBase):
    id: int
    thread_id: int
    user_id: int
    created_at: datetime
    author: UserOut
    upvotes: int = 0
    downvotes: int = 0

    # ✅ Pydantic v2
    model_config = ConfigDict(from_attributes=True)

# === THREADS ===
class ThreadBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=10)
    category: str = Field(..., pattern="^(geral|faculdade)$")  # ✅ regex → pattern
    tags: Optional[List[str]] = []

class ThreadCreate(ThreadBase):
    pass

class ThreadOut(ThreadBase):
    id: int
    user_id: int
    university: Optional[str]
    created_at: datetime
    author: UserOut
    upvotes: int = 0
    downvotes: int = 0
    is_reported: bool = False
    top_comments: List[CommentOut] = []

    # ✅ Pydantic v2
    model_config = ConfigDict(from_attributes=True)
