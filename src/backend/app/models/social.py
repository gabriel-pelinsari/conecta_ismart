from sqlalchemy import Column, Integer, ForeignKey, DateTime, func, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.user import User
from sqlalchemy import String

class Friendship(Base):
    __tablename__ = "friendships"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    friend_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    status = Column(String(20), default="pending", nullable=False)  # pending, accepted, rejected
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    accepted_at = Column(DateTime(timezone=False), nullable=True)

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
    university_name = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)  # Ex: "USP - Comunidade ISMART"
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())

    members = relationship("UniversityGroupMember", back_populates="group", cascade="all, delete-orphan")


class UniversityGroupMember(Base):
    """Membros dos grupos de universidade"""
    __tablename__ = "university_group_members"

    group_id = Column(Integer, ForeignKey("university_groups.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    joined_at = Column(DateTime(timezone=False), server_default=func.now())

    group = relationship("UniversityGroup", back_populates="members")
    user = relationship("User")
