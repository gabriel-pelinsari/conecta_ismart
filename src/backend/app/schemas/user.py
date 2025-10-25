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
    password: constr(min_length=8, max_length=64)
    verification_code: str

    @validator('password')
    def strong_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('A senha deve conter ao menos 1 letra maiúscula.')
        if not re.search(r'\d', v):
            raise ValueError('A senha deve conter ao menos 1 número.')
        if not PASSWORD_ALLOWED.match(v):
            raise ValueError('A senha contém caracteres não permitidos.')
        return v

class UserOut(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    role: str

    # ✅ Pydantic v2
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
