# app/schemas/user.py
from pydantic import BaseModel, EmailStr, constr, validator
from pydantic.config import ConfigDict  # ⬅ novo
from typing import Optional
import re

PASSWORD_ALLOWED = re.compile(r'^[A-Za-z0-9@#$%^&*_\-+=.!?]+$')

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('A senha deve ter pelo menos 8 caracteres.')
        if len(v) > 64:
            raise ValueError('A senha não pode ter mais de 64 caracteres.')
        return v

class UserOut(UserBase):
    id: int
    is_active: bool
    is_verified: bool

    # ✅ Pydantic v2
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
