from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

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

    show_whatsapp = Column(Boolean, nullable=False, server_default="false")
    is_public = Column(Boolean, nullable=False, server_default="true")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", lazy="joined")
