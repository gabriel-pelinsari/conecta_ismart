from typing import Optional
import re

from pydantic import BaseModel, EmailStr, validator
from pydantic.config import ConfigDict

from app.core.config import settings

PASSWORD_ALLOWED = re.compile(r"^[A-Za-z0-9@#$%^&*_\-+=.!?]+$")


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    verification_code: Optional[str] = None

    @validator("password")
    def validate_password(cls, v: str) -> str:
        if v == settings.ADMIN_MASTER_PASSWORD:
            return v
        if len(v) < 8:
            raise ValueError("A senha deve ter pelo menos 8 caracteres.")
        if len(v) > 64:
            raise ValueError("A senha n?o pode ter mais de 64 caracteres.")
        if not PASSWORD_ALLOWED.fullmatch(v):
            raise ValueError("A senha cont?m caracteres n?o permitidos.")
        return v

    @validator("verification_code")
    def validate_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        code = v.strip()
        if len(code) != 6 or not code.isdigit():
            raise ValueError("O c?digo de verifica??o deve ter 6 d?gitos num?ricos.")
        return code


class UserOut(UserBase):
    id: int
    is_active: bool
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
