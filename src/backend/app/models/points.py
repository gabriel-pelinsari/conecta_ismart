from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class PointHistory(Base):
    """Histórico de pontos ganhos/perdidos pelo usuário"""
    __tablename__ = "point_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    points = Column(Integer, nullable=False)  # Pode ser positivo ou negativo
    action_type = Column(String(50), nullable=False)  # 'create_thread', 'comment', 'upvote_received', etc.
    description = Column(Text, nullable=True)
    reference_id = Column(Integer, nullable=True)  # ID do thread, comment, etc.
    reference_type = Column(String(50), nullable=True)  # 'thread', 'comment', 'event'
    created_at = Column(DateTime(timezone=False), server_default=func.now())

    # Relacionamento com User será adicionado depois se necessário
