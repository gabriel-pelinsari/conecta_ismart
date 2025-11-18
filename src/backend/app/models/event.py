from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base


class Event(Base):
    """
    Sistema de Eventos
    RF079-RF096: Criar, editar, cancelar eventos
    """

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(String(50), nullable=False, index=True)
    # Tipos: 'workshop', 'meetup', 'study_group', 'networking', 'webinar', 'other'

    start_datetime = Column(DateTime(timezone=False), nullable=False, index=True)
    end_datetime = Column(DateTime(timezone=False), nullable=False)

    location = Column(String(300), nullable=True)  # Pode ser online ou presencial
    is_online = Column(Boolean, default=False, nullable=False)
    online_link = Column(String(500), nullable=True)  # Link Zoom, Meet, etc.

    university = Column(String(100), nullable=True, index=True)  # Evento específico de universidade
    max_participants = Column(Integer, nullable=True)  # Limite de participantes (null = ilimitado)

    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_cancelled = Column(Boolean, default=False, nullable=False)
    cancelled_reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    creator = relationship("User", foreign_keys=[created_by])
    participants = relationship("EventParticipant", back_populates="event", cascade="all, delete-orphan")


class EventParticipant(Base):
    """
    Participantes de eventos
    Status: confirmed, maybe, declined, attended
    """

    __tablename__ = "event_participants"

    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    status = Column(String(20), default="confirmed", nullable=False)
    # Status: 'confirmed', 'maybe', 'declined', 'attended'

    attended = Column(Boolean, default=False, nullable=False)  # Marcado pelo criador
    joined_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    event = relationship("Event", back_populates="participants")
    user = relationship("User")
