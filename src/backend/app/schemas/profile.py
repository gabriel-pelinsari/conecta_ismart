from typing import Optional, List
from pydantic import BaseModel, AnyUrl, Field

# ---- Stats & Badges (MVP placeholders) ----
class ProfileStats(BaseModel):
    threads_count: int = 0
    comments_count: int = 0
    events_count: int = 0

class ProfileBadge(BaseModel):
    key: str
    name: str
    icon_url: Optional[AnyUrl] = None

# ---- Base payloads ----
class ProfileBase(BaseModel):
    full_name: str = Field(..., max_length=100)
    nickname: Optional[str] = Field(None, max_length=50)
    university: Optional[str] = Field(None, max_length=100)
    course: Optional[str] = Field(None, max_length=100)
    semester: Optional[str] = Field(None, max_length=20)
    bio: Optional[str] = Field(None, max_length=1000)
    linkedin: Optional[str] = None
    instagram: Optional[str] = None
    whatsapp: Optional[str] = None
    show_whatsapp: bool = False
    is_public: bool = True

class ProfileUpdate(ProfileBase):
    pass

# ---- Responses ----
class ProfilePublicOut(BaseModel):
    user_id: int
    full_name: str
    nickname: Optional[str]
    university: Optional[str]
    course: Optional[str]
    semester: Optional[str]
    bio: Optional[str]
    photo_url: Optional[str]
    # socials são OMITIDAS aqui por padrão
    stats: ProfileStats = ProfileStats()
    badges: List[ProfileBadge] = []

class ProfilePrivateOut(ProfilePublicOut):
    # inclui socials para dono/amigo
    linkedin: Optional[str]
    instagram: Optional[str]
    whatsapp: Optional[str]
    show_whatsapp: bool
