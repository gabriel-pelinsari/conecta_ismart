from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_code = Column(String(6), nullable=True)
    role = Column(String(20), default="student", nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now())

    profile = relationship("Profile", back_populates="user", uselist=False)
    stats = relationship("UserStats", back_populates="user", uselist=False)
    friendships = relationship(
        "Friendship",
        foreign_keys="[Friendship.user_id]",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    friends = relationship(
        "Friendship",
        foreign_keys="[Friendship.friend_id]",
        back_populates="friend",
        cascade="all, delete-orphan"
    )
    badges = relationship("UserBadge", back_populates="user", cascade="all, delete-orphan")
    interests = relationship("UserInterest", back_populates="user", cascade="all, delete-orphan")


class UserStats(Base):
    __tablename__ = "user_stats"

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    threads_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    events_count = Column(Integer, default=0)

    user = relationship("User", back_populates="stats")