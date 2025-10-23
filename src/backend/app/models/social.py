from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.user import User
from sqlalchemy import String

class Friendship(Base):
    __tablename__ = "friendships"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    friend_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    accepted_at = Column(DateTime(timezone=False))

    user = relationship("User", foreign_keys=[user_id], back_populates="friendships")
    friend = relationship("User", foreign_keys=[friend_id], back_populates="friends")


class Interest(Base):
    __tablename__ = "interests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), unique=True, nullable=False)

    users = relationship("UserInterest", back_populates="interest", cascade="all, delete-orphan")


class UserInterest(Base):
    __tablename__ = "user_interests"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    interest_id = Column(Integer, ForeignKey("interests.id", ondelete="CASCADE"), primary_key=True)

    user = relationship("User", back_populates="interests")
    interest = relationship("Interest", back_populates="users")
