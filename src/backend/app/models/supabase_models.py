"""
Modelos mapeados para o schema EXISTENTE do Supabase
Não cria novas tabelas, apenas mapeia as existentes
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid


class University(Base):
    """Tabela universities (já existe no Supabase)"""
    __tablename__ = "universities"
    __table_args__ = {'extend_existing': True}

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(Text, unique=True, nullable=False)
    address = Column(Text, nullable=True)

    # Relationships
    profiles = relationship("ProfileSupabase", back_populates="university")


class ProfileSupabase(Base):
    """Tabela profiles (já existe no Supabase)"""
    __tablename__ = "profiles"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(Text, nullable=False)
    email = Column(Text, unique=True, nullable=False)
    whatsapp = Column(Text, nullable=True)
    linkedin = Column(Text, nullable=True)
    nickname = Column(Text, nullable=True)
    entry_year = Column(Integer, nullable=False)
    university_id = Column(BigInteger, ForeignKey("universities.id"), nullable=True)
    course = Column(Text, nullable=False)
    bio = Column(Text, nullable=True)
    photo_url = Column(Text, nullable=True)
    featured_song = Column(Text, nullable=True)
    show_linkedin = Column(Boolean, default=False, nullable=False)
    show_email = Column(Boolean, default=False, nullable=False)
    show_whatsapp_to_connections = Column(Boolean, default=False, nullable=False)
    show_university_course = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    university_rel = relationship("University", back_populates="profiles", foreign_keys=[university_id])
    interests = relationship("ProfileInterest", back_populates="profile", cascade="all, delete-orphan")
    connections_sent = relationship(
        "Connection",
        foreign_keys="[Connection.requester_id]",
        back_populates="requester",
        cascade="all, delete-orphan"
    )
    connections_received = relationship(
        "Connection",
        foreign_keys="[Connection.addressee_id]",
        back_populates="addressee",
        cascade="all, delete-orphan"
    )


class Interest(Base):
    """Tabela interests (já existe no Supabase)"""
    __tablename__ = "interests"
    __table_args__ = {'extend_existing': True}

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(Text, unique=True, nullable=False)
    approved = Column(Boolean, default=False, nullable=False)

    # Relationships
    profiles = relationship("ProfileInterest", back_populates="interest", cascade="all, delete-orphan")


class ProfileInterest(Base):
    """Tabela profile_interests (já existe no Supabase)"""
    __tablename__ = "profile_interests"
    __table_args__ = {'extend_existing': True}

    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), primary_key=True)
    interest_id = Column(BigInteger, ForeignKey("interests.id", ondelete="CASCADE"), primary_key=True)

    # Relationships
    profile = relationship("ProfileSupabase", back_populates="interests")
    interest = relationship("Interest", back_populates="profiles")


class Connection(Base):
    """
    Tabela connections (já existe no Supabase)
    Equivalente a 'friendships' no código antigo
    """
    __tablename__ = "connections"
    __table_args__ = {'extend_existing': True}

    requester_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), primary_key=True)
    addressee_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), primary_key=True)
    status = Column(String(20), default="pendente", nullable=False)  # pendente, aceita, rejeitada
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    responded_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    requester = relationship("ProfileSupabase", foreign_keys=[requester_id], back_populates="connections_sent")
    addressee = relationship("ProfileSupabase", foreign_keys=[addressee_id], back_populates="connections_received")


class Score(Base):
    """Tabela scores (já existe no Supabase)"""
    __tablename__ = "scores"
    __table_args__ = {'extend_existing': True}

    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), primary_key=True)
    points = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
