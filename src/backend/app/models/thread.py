# backend/app/models/thread.py

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Thread(Base):
    __tablename__ = "threads"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # 'geral' ou 'faculdade'
    tags = Column(String(200), default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    university = Column(String(100))  # Copiado do perfil do usuário
    is_reported = Column(Boolean, default=False)

    author = relationship("User", back_populates="threads", lazy="joined")
    comments = relationship("Comment", back_populates="thread", cascade="all, delete-orphan")
    votes = relationship("ThreadVote", back_populates="thread", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    thread_id = Column(Integer, ForeignKey("threads.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    thread = relationship("Thread", back_populates="comments")
    author = relationship("User")
    votes = relationship("CommentVote", back_populates="comment", cascade="all, delete-orphan")


class ThreadVote(Base):
    __tablename__ = "thread_votes"
    __table_args__ = (UniqueConstraint('user_id', 'thread_id', name='unique_user_thread_vote'),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    thread_id = Column(Integer, ForeignKey("threads.id"))
    value = Column(Integer)  # +1 ou -1

    thread = relationship("Thread", back_populates="votes")


class CommentVote(Base):
    __tablename__ = "comment_votes"
    __table_args__ = (UniqueConstraint('user_id', 'comment_id', name='unique_user_comment_vote'),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    comment_id = Column(Integer, ForeignKey("comments.id"))
    value = Column(Integer)  # +1 ou -1

    comment = relationship("Comment", back_populates="votes")
