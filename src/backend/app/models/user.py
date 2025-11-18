from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.thread import Thread

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    # Allow null until user completes registration and sets a password
    hashed_password = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
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
    threads = relationship("Thread", back_populates="author", cascade="all, delete-orphan")


class UserStats(Base):
    __tablename__ = "user_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    total_posts = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    total_votes_received = Column(Integer, default=0)
    total_friendships = Column(Integer, default=0)
    badges_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=False), server_default=func.now())

    user = relationship("User", back_populates="stats")
