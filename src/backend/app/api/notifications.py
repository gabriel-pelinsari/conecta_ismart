import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.notification import Notification, NotificationPreference
from app.schemas.notification import (
    NotificationOut,
    NotificationPreferenceOut,
    NotificationPreferenceUpdate,
    UnreadCountOut,
)
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/", response_model=List[NotificationOut])
def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    📬 Lista notificações do usuário

    - Ordenado por data (mais recente primeiro)
    - Opção para filtrar apenas não lidas
    - Suporta paginação
    """
    logger.info(f"📬 User {current_user.id} listing notifications (unread_only={unread_only})")

    query = db.query(Notification).filter(Notification.user_id == current_user.id)

    if unread_only:
        query = query.filter(Notification.is_read == False)

    notifications = (
        query.order_by(Notification.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return notifications


@router.get("/unread-count", response_model=UnreadCountOut)
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    🔢 Retorna número de notificações não lidas

    - Útil para exibir badge no ícone de notificações
    """
    count = NotificationService.get_unread_count(db, current_user.id)

    return UnreadCountOut(unread_count=count)


@router.put("/{notification_id}/read", response_model=dict)
def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    ✅ Marca notificação como lida

    - Apenas o dono da notificação pode marcá-la como lida
    """
    logger.info(f"✅ User {current_user.id} marking notification {notification_id} as read")

    success = NotificationService.mark_as_read(db, notification_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada",
        )

    return {"status": "success", "message": "Notificação marcada como lida"}


@router.post("/mark-all-read", response_model=dict)
def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    ✅ Marca todas as notificações como lidas

    - Atualiza todas as notificações não lidas do usuário
    """
    logger.info(f"✅ User {current_user.id} marking all notifications as read")

    count = NotificationService.mark_all_as_read(db, current_user.id)

    return {
        "status": "success",
        "message": f"{count} notificações marcadas como lidas",
        "count": count,
    }


@router.delete("/{notification_id}", response_model=dict)
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    🗑️ Deleta uma notificação

    - Apenas o dono pode deletar
    """
    logger.info(f"🗑️ User {current_user.id} deleting notification {notification_id}")

    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada",
        )

    db.delete(notification)
    db.commit()

    return {"status": "success", "message": "Notificação deletada"}


@router.get("/preferences", response_model=NotificationPreferenceOut)
def get_notification_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    ⚙️ Retorna preferências de notificação do usuário

    - Cria preferências padrão se não existirem
    """
    logger.info(f"⚙️ User {current_user.id} getting notification preferences")

    prefs = NotificationService.get_or_create_preferences(db, current_user.id)

    return NotificationPreferenceOut(
        comment_on_thread=prefs.comment_on_thread,
        friend_request_received=prefs.friend_request_received,
        friend_request_accepted=prefs.friend_request_accepted,
        new_mentee=prefs.new_mentee,
        event_reminder=prefs.event_reminder,
        badge_earned=prefs.badge_earned,
        upvote_received=prefs.upvote_received,
        mention=prefs.mention,
    )


@router.put("/preferences", response_model=NotificationPreferenceOut)
def update_notification_preferences(
    preferences: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    ⚙️ Atualiza preferências de notificação

    - Atualiza apenas os campos fornecidos
    - Cria preferências padrão se não existirem
    """
    logger.info(f"⚙️ User {current_user.id} updating notification preferences")

    prefs = NotificationService.get_or_create_preferences(db, current_user.id)

    # Atualizar apenas campos fornecidos
    update_data = preferences.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(prefs, field):
            setattr(prefs, field, value)

    db.commit()
    db.refresh(prefs)

    return NotificationPreferenceOut(
        comment_on_thread=prefs.comment_on_thread,
        friend_request_received=prefs.friend_request_received,
        friend_request_accepted=prefs.friend_request_accepted,
        new_mentee=prefs.new_mentee,
        event_reminder=prefs.event_reminder,
        badge_earned=prefs.badge_earned,
        upvote_received=prefs.upvote_received,
        mention=prefs.mention,
    )


@router.get("/types", response_model=dict)
def get_notification_types():
    """
    📋 Lista todos os tipos de notificação disponíveis

    - Útil para UI de configurações
    """
    return {
        "notification_types": NotificationService.NOTIFICATION_TYPES,
    }
