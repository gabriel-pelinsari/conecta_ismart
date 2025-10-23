from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.schemas.interest import InterestOut

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    nickname = Column(String(50))
    university = Column(String(100))
    course = Column(String(100))
    semester = Column(String(20))
    bio = Column(Text)
    photo_url = Column(String(255))
    linkedin = Column(String(255))
    instagram = Column(String(255))
    whatsapp = Column(String(50))
    show_whatsapp = Column(Boolean, default=False, nullable=False)
    is_public = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now())

    user = relationship("User", back_populates="profile")

