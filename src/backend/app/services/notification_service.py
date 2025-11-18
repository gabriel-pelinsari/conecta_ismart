"""
Serviço de Notificações
RF169-RF182: Gerenciamento completo de notificações
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging
from typing import Optional, List, Dict
from datetime import datetime

from app.models.notification import Notification, NotificationPreference

logger = logging.getLogger(__name__)


class NotificationService:
    """Serviço para gerenciamento de notificações"""

    # Tipos de notificação suportados
    NOTIFICATION_TYPES = {
        "comment_on_thread": "Novo comentário em discussão",
        "friend_request_received": "Solicitação de amizade recebida",
        "friend_request_accepted": "Solicitação de amizade aceita",
        "new_mentee": "Novo mentee atribuído",
        "event_reminder_24h": "Lembrete de evento (24h)",
        "event_reminder_1h": "Lembrete de evento (1h)",
        "badge_earned": "Nova conquista de badge",
        "upvote_received": "Recebeu upvote",
        "mention": "Mencionado em comentário",
    }

    @staticmethod
    def get_or_create_preferences(db: Session, user_id: int) -> NotificationPreference:
        """
        Retorna as preferências do usuário ou cria com valores padrão
        """
        prefs = (
            db.query(NotificationPreference)
            .filter(NotificationPreference.user_id == user_id)
            .first()
        )

        if not prefs:
            prefs = NotificationPreference(user_id=user_id)
            db.add(prefs)
            db.commit()
            db.refresh(prefs)
            logger.info(f"Created notification preferences for user {user_id}")

        return prefs

    @staticmethod
    def is_notification_enabled(
        db: Session, user_id: int, notification_type: str
    ) -> bool:
        """
        Verifica se o usuário tem o tipo de notificação ativado
        """
        prefs = NotificationService.get_or_create_preferences(db, user_id)

        # Obter o valor da preferência dinamicamente
        if hasattr(prefs, notification_type):
            return getattr(prefs, notification_type)

        # Se o tipo não existe, retorna True (ativo por padrão)
        return True

    @staticmethod
    def create_notification(
        db: Session,
        user_id: int,
        notification_type: str,
        title: str,
        content: str,
        link: Optional[str] = None,
        reference_id: Optional[int] = None,
        reference_type: Optional[str] = None,
    ) -> Optional[Notification]:
        """
        Cria uma notificação se o usuário tem esse tipo ativado

        Returns:
            Notification object se criada, None se usuário tem tipo desativado
        """
        # Verificar se o tipo é válido
        if notification_type not in NotificationService.NOTIFICATION_TYPES:
            logger.warning(f"Invalid notification type: {notification_type}")
            return None

        # Verificar se o usuário tem esse tipo de notificação ativado
        if not NotificationService.is_notification_enabled(db, user_id, notification_type):
            logger.debug(
                f"User {user_id} has {notification_type} notifications disabled"
            )
            return None

        # Criar notificação
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            content=content,
            link=link,
            reference_id=reference_id,
            reference_type=reference_type,
            is_read=False,
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        logger.info(
            f"Created notification for user {user_id}: {notification_type} - {title}"
        )

        return notification

    @staticmethod
    def notify_comment_on_thread(
        db: Session,
        thread_id: int,
        thread_title: str,
        commenter_name: str,
        participants: List[int],
    ):
        """
        Notifica participantes de uma discussão sobre novo comentário
        """
        for user_id in participants:
            NotificationService.create_notification(
                db=db,
                user_id=user_id,
                notification_type="comment_on_thread",
                title=f"Novo comentário em '{thread_title}'",
                content=f"{commenter_name} comentou em uma discussão que você participa",
                link=f"/threads/{thread_id}",
                reference_id=thread_id,
                reference_type="thread",
            )

    @staticmethod
    def notify_friend_request(
        db: Session, recipient_id: int, requester_name: str, requester_id: int
    ):
        """
        Notifica sobre solicitação de amizade recebida
        """
        NotificationService.create_notification(
            db=db,
            user_id=recipient_id,
            notification_type="friend_request_received",
            title="Nova solicitação de amizade",
            content=f"{requester_name} enviou uma solicitação de amizade",
            link=f"/profile/{requester_id}",
            reference_id=requester_id,
            reference_type="user",
        )

    @staticmethod
    def notify_friend_request_accepted(
        db: Session, requester_id: int, accepter_name: str, accepter_id: int
    ):
        """
        Notifica que solicitação de amizade foi aceita
        """
        NotificationService.create_notification(
            db=db,
            user_id=requester_id,
            notification_type="friend_request_accepted",
            title="Solicitação de amizade aceita",
            content=f"{accepter_name} aceitou sua solicitação de amizade",
            link=f"/profile/{accepter_id}",
            reference_id=accepter_id,
            reference_type="user",
        )

    @staticmethod
    def notify_new_mentee(
        db: Session, mentor_id: int, mentee_name: str, mentee_id: int
    ):
        """
        Notifica mentor sobre novo mentee atribuído
        """
        NotificationService.create_notification(
            db=db,
            user_id=mentor_id,
            notification_type="new_mentee",
            title="Novo mentee atribuído",
            content=f"{mentee_name} foi atribuído(a) como seu mentee",
            link=f"/mentorship/mentees",
            reference_id=mentee_id,
            reference_type="user",
        )

    @staticmethod
    def notify_event_reminder(
        db: Session,
        user_id: int,
        event_id: int,
        event_title: str,
        hours_before: int,
    ):
        """
        Lembrete de evento (24h ou 1h antes)
        """
        notification_type = (
            "event_reminder_24h" if hours_before == 24 else "event_reminder_1h"
        )
        time_str = "24 horas" if hours_before == 24 else "1 hora"

        NotificationService.create_notification(
            db=db,
            user_id=user_id,
            notification_type=notification_type,
            title=f"Lembrete: {event_title}",
            content=f"O evento começa em {time_str}",
            link=f"/events/{event_id}",
            reference_id=event_id,
            reference_type="event",
        )

    @staticmethod
    def notify_badge_earned(
        db: Session, user_id: int, badge_name: str, badge_id: int
    ):
        """
        Notifica sobre conquista de badge
        """
        NotificationService.create_notification(
            db=db,
            user_id=user_id,
            notification_type="badge_earned",
            title="Nova conquista desbloqueada!",
            content=f"Você ganhou o badge: {badge_name}",
            link="/profile/badges",
            reference_id=badge_id,
            reference_type="badge",
        )

    @staticmethod
    def notify_upvote_received(
        db: Session,
        user_id: int,
        content_type: str,
        content_id: int,
        content_title: str,
    ):
        """
        Notifica sobre upvote recebido em thread ou comentário
        """
        NotificationService.create_notification(
            db=db,
            user_id=user_id,
            notification_type="upvote_received",
            title="Seu conteúdo recebeu um upvote",
            content=f"Seu {content_type} '{content_title}' recebeu um upvote",
            link=f"/{content_type}s/{content_id}",
            reference_id=content_id,
            reference_type=content_type,
        )

    @staticmethod
    def notify_mention(
        db: Session,
        user_id: int,
        mentioner_name: str,
        thread_id: int,
        comment_id: int,
    ):
        """
        Notifica sobre menção em comentário
        """
        NotificationService.create_notification(
            db=db,
            user_id=user_id,
            notification_type="mention",
            title="Você foi mencionado",
            content=f"{mentioner_name} mencionou você em um comentário",
            link=f"/threads/{thread_id}#comment-{comment_id}",
            reference_id=comment_id,
            reference_type="comment",
        )

    @staticmethod
    def mark_as_read(db: Session, notification_id: int, user_id: int) -> bool:
        """
        Marca notificação como lida
        Retorna True se sucesso, False se não encontrada ou não pertence ao usuário
        """
        notification = (
            db.query(Notification)
            .filter(
                Notification.id == notification_id, Notification.user_id == user_id
            )
            .first()
        )

        if not notification:
            return False

        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.commit()

        return True

    @staticmethod
    def mark_all_as_read(db: Session, user_id: int) -> int:
        """
        Marca todas as notificações do usuário como lidas
        Retorna número de notificações atualizadas
        """
        count = (
            db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)
            .update({"is_read": True, "read_at": datetime.utcnow()})
        )

        db.commit()

        return count

    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        """
        Retorna número de notificações não lidas
        """
        return (
            db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)
            .count()
        )

    @staticmethod
    def delete_old_notifications(db: Session, days: int = 30) -> int:
        """
        Deleta notificações antigas (lidas e com mais de X dias)
        Retorna número de notificações deletadas
        """
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        count = (
            db.query(Notification)
            .filter(Notification.is_read == True, Notification.created_at < cutoff_date)
            .delete()
        )

        db.commit()

        logger.info(f"Deleted {count} old notifications (older than {days} days)")

        return count
