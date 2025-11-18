from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base


class Notification(Base):
    """
    Sistema de Notificações
    RF169-RF182: 8 tipos de notificações
    """

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    notification_type = Column(String(50), nullable=False, index=True)
    # Tipos: comment_on_thread, friend_request_received, friend_request_accepted,
    #        new_mentee, event_reminder_24h, event_reminder_1h, badge_earned,
    #        upvote_received, mention

    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    link = Column(String(500), nullable=True)  # URL para navegar ao clicar
    is_read = Column(Boolean, default=False, nullable=False, index=True)

    # Referências opcionais
    reference_id = Column(Integer, nullable=True)  # ID do thread, comment, user, etc.
    reference_type = Column(String(50), nullable=True)  # 'thread', 'comment', 'user', 'event'

    created_at = Column(DateTime(timezone=False), server_default=func.now())
    read_at = Column(DateTime(timezone=False), nullable=True)

    # Relacionamento
    user = relationship("User")


class NotificationPreference(Base):
    """
    Preferências de notificação do usuário
    """

    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    # Preferências (True = ativo, False = desativado)
    comment_on_thread = Column(Boolean, default=True, nullable=False)
    friend_request_received = Column(Boolean, default=True, nullable=False)
    friend_request_accepted = Column(Boolean, default=True, nullable=False)
    new_mentee = Column(Boolean, default=True, nullable=False)
    event_reminder = Column(Boolean, default=True, nullable=False)
    badge_earned = Column(Boolean, default=True, nullable=False)
    upvote_received = Column(Boolean, default=True, nullable=False)
    mention = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())

    # Relacionamento
    user = relationship("User")
