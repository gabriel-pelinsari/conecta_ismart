from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base


class Report(Base):
    """
    Sistema de denúncias/reports
    RF183-RF189: Reportar threads, comentários e usuários
    """

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_type = Column(
        String(20), nullable=False, index=True
    )  # 'thread', 'comment', 'user'
    target_id = Column(Integer, nullable=False, index=True)
    category = Column(String(50), nullable=False)  # 'spam', 'offensive', 'harassment', etc.
    description = Column(Text, nullable=True)
    status = Column(
        String(20), default="pending", nullable=False, index=True
    )  # 'pending', 'reviewed', 'approved', 'rejected'
    admin_notes = Column(Text, nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime(timezone=False), nullable=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    reporter = relationship("User", foreign_keys=[reporter_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
