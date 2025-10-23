from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(64), unique=True, nullable=False)
    name = Column(String(120), nullable=False)
    description = Column(Text)
    icon = Column(Text)

    users = relationship("UserBadge", back_populates="badge", cascade="all, delete-orphan")


class UserBadge(Base):
    __tablename__ = "user_badges"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    badge_id = Column(Integer, ForeignKey("badges.id", ondelete="CASCADE"), primary_key=True)
    awarded_at = Column(DateTime(timezone=False), server_default=func.now())

    user = relationship("User", back_populates="badges")
    badge = relationship("Badge", back_populates="users")
