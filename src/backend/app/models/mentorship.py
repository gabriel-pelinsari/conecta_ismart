from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.base import Base


class Mentorship(Base):
    """
    Sistema de Mentoria
    RF068-RF078: Mentor-mentee matching e gerenciamento
    """

    __tablename__ = "mentorships"

    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    mentee_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    status = Column(String(20), default="active", nullable=False)
    # Status: 'active', 'completed', 'cancelled'

    compatibility_score = Column(Float, nullable=True)  # Score de compatibilidade (0-100)
    matched_at = Column(DateTime(timezone=False), server_default=func.now())
    completed_at = Column(DateTime(timezone=False), nullable=True)
    cancelled_at = Column(DateTime(timezone=False), nullable=True)
    cancellation_reason = Column(String(500), nullable=True)

    # Relacionamentos
    mentor = relationship("User", foreign_keys=[mentor_id])
    mentee = relationship("User", foreign_keys=[mentee_id])


class MentorshipQueue(Base):
    """
    Fila de espera para mentorados sem mentor
    """

    __tablename__ = "mentorship_queue"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    requested_at = Column(DateTime(timezone=False), server_default=func.now())
    priority_score = Column(Float, default=0.0, nullable=False)  # Prioridade na fila

    # Relacionamento
    user = relationship("User")
