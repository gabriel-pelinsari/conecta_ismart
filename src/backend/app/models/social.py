from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    func,
    Text,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.user import User


class Friendship(Base):
    __tablename__ = "friendships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    friend_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), server_default="pending", nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint("user_id", "friend_id", name="unique_friendship_pair"),)

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


class UniversityGroup(Base):
    """RF052 - Grupos automáticos por universidade"""

    __tablename__ = "university_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    university_name = Column("university", String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())

    members = relationship("UniversityGroupMember", back_populates="group", cascade="all, delete-orphan")


class UniversityGroupMember(Base):
    """Membros dos grupos de universidade"""

    __tablename__ = "university_group_members"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("university_groups.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    joined_at = Column(DateTime(timezone=False), server_default=func.now())

    __table_args__ = (UniqueConstraint("group_id", "user_id", name="unique_group_member"),)

    group = relationship("UniversityGroup", back_populates="members")
    user = relationship("User")
