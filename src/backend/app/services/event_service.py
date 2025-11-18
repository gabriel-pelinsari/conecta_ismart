"""
Serviço de Eventos
RF079-RF096: Gerenciamento completo de eventos
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import logging
from typing import Optional, List, Dict
from datetime import datetime, timedelta

from app.models.event import Event, EventParticipant
from app.services.notification_service import NotificationService
from app.services.gamification import GamificationService

logger = logging.getLogger(__name__)


class EventService:
    """Serviço para gerenciamento de eventos"""

    EVENT_TYPES = [
        "workshop",
        "meetup",
        "study_group",
        "networking",
        "webinar",
        "other",
    ]

    @staticmethod
    def can_user_join(db: Session, event_id: int, user_id: int) -> tuple[bool, str]:
        """
        Verifica se o usuário pode entrar no evento

        Returns:
            (can_join: bool, reason: str)
        """
        event = db.query(Event).filter(Event.id == event_id).first()

        if not event:
            return False, "Evento não encontrado"

        if event.is_cancelled:
            return False, "Evento cancelado"

        # Verificar se já está participando
        existing = (
            db.query(EventParticipant)
            .filter(
                EventParticipant.event_id == event_id,
                EventParticipant.user_id == user_id,
            )
            .first()
        )

        if existing and existing.status != "declined":
            return False, "Você já está participando deste evento"

        # Verificar limite de participantes
        if event.max_participants:
            confirmed_count = (
                db.query(EventParticipant)
                .filter(
                    EventParticipant.event_id == event_id,
                    EventParticipant.status == "confirmed",
                )
                .count()
            )

            if confirmed_count >= event.max_participants:
                return False, "Evento lotado"

        # Verificar se o evento já passou
        if event.start_datetime < datetime.utcnow():
            return False, "Evento já iniciado"

        return True, "OK"

    @staticmethod
    def rsvp_event(
        db: Session,
        event_id: int,
        user_id: int,
        status: str = "confirmed",
    ) -> EventParticipant:
        """
        RSVP para um evento

        Args:
            status: 'confirmed', 'maybe', 'declined'
        """
        # Verificar se já existe registro
        existing = (
            db.query(EventParticipant)
            .filter(
                EventParticipant.event_id == event_id,
                EventParticipant.user_id == user_id,
            )
            .first()
        )

        # Verificar se pode entrar
        can_join, reason = EventService.can_user_join(db, event_id, user_id)

        if not can_join:
            reason_lower = reason.lower()
            if existing:
                blocked_keywords = ["cancelado", "não encontrado", "nao encontrado", "iniciado"]
                if any(keyword in reason_lower for keyword in blocked_keywords):
                    raise ValueError(reason)
            elif status != "declined":
                raise ValueError(reason)

        if existing:
            # Atualizar status
            existing.status = status
            existing.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing

        # Criar novo registro
        participant = EventParticipant(
            event_id=event_id,
            user_id=user_id,
            status=status,
        )

        db.add(participant)
        db.commit()
        db.refresh(participant)

        logger.info(f"User {user_id} RSVP'd to event {event_id} with status {status}")

        return participant

    @staticmethod
    def mark_attendance(
        db: Session, event_id: int, user_id: int, creator_id: int
    ) -> bool:
        """
        Marca presença de um participante
        Apenas o criador do evento pode fazer isso
        Atribui +20 pontos ao participante
        """
        event = db.query(Event).filter(Event.id == event_id).first()

        if not event:
            raise ValueError("Evento não encontrado")

        if event.created_by != creator_id:
            raise ValueError("Apenas o criador pode marcar presença")

        participant = (
            db.query(EventParticipant)
            .filter(
                EventParticipant.event_id == event_id,
                EventParticipant.user_id == user_id,
            )
            .first()
        )

        if not participant:
            raise ValueError("Participante não encontrado")

        if participant.attended:
            return False  # Já marcado

        # Marcar presença
        participant.attended = True
        db.commit()

        # Atribuir pontos
        GamificationService.award_points(
            db=db,
            user_id=user_id,
            action_type="event_participation",
            reference_id=event_id,
            reference_type="event",
            description=f"Participação no evento: {event.title}",
        )

        logger.info(f"User {user_id} attendance marked for event {event_id}")

        return True

    @staticmethod
    def send_event_reminders(db: Session, hours_before: int = 24):
        """
        Envia lembretes de eventos que começam em X horas

        Args:
            hours_before: 24 para lembrete de 24h, 1 para lembrete de 1h
        """
        # Calcular janela de tempo
        now = datetime.utcnow()
        target_time_start = now + timedelta(hours=hours_before - 0.5)
        target_time_end = now + timedelta(hours=hours_before + 0.5)

        # Buscar eventos nessa janela
        events = (
            db.query(Event)
            .filter(
                Event.start_datetime >= target_time_start,
                Event.start_datetime <= target_time_end,
                Event.is_cancelled == False,
            )
            .all()
        )

        reminder_count = 0

        for event in events:
            # Buscar participantes confirmados
            participants = (
                db.query(EventParticipant)
                .filter(
                    EventParticipant.event_id == event.id,
                    EventParticipant.status == "confirmed",
                )
                .all()
            )

            for participant in participants:
                NotificationService.notify_event_reminder(
                    db=db,
                    user_id=participant.user_id,
                    event_id=event.id,
                    event_title=event.title,
                    hours_before=hours_before,
                )
                reminder_count += 1

        logger.info(
            f"Sent {reminder_count} event reminders ({hours_before}h before)"
        )

        return reminder_count

    @staticmethod
    def get_event_stats(db: Session, event_id: int) -> Dict:
        """
        Retorna estatísticas de um evento
        """
        # Contar participantes por status
        stats = (
            db.query(
                EventParticipant.status, func.count(EventParticipant.user_id)
            )
            .filter(EventParticipant.event_id == event_id)
            .group_by(EventParticipant.status)
            .all()
        )

        status_counts = {status: count for status, count in stats}

        # Contar presenças marcadas
        attended_count = (
            db.query(EventParticipant)
            .filter(
                EventParticipant.event_id == event_id,
                EventParticipant.attended == True,
            )
            .count()
        )

        return {
            "confirmed": status_counts.get("confirmed", 0),
            "maybe": status_counts.get("maybe", 0),
            "declined": status_counts.get("declined", 0),
            "attended": attended_count,
            "total_rsvp": sum(status_counts.values()),
        }

    @staticmethod
    def get_upcoming_events(
        db: Session,
        university: Optional[str] = None,
        event_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Event]:
        """
        Retorna eventos futuros (não cancelados)
        """
        query = db.query(Event).filter(
            Event.start_datetime >= datetime.utcnow(),
            Event.is_cancelled == False,
        )

        if university:
            query = query.filter(Event.university == university)

        if event_type:
            query = query.filter(Event.event_type == event_type)

        return (
            query.order_by(Event.start_datetime.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_user_events(
        db: Session,
        user_id: int,
        status: Optional[str] = None,
        include_past: bool = False,
    ) -> List[Event]:
        """
        Retorna eventos do usuário
        """
        query = (
            db.query(Event)
            .join(EventParticipant)
            .filter(EventParticipant.user_id == user_id)
        )

        if status:
            query = query.filter(EventParticipant.status == status)

        if not include_past:
            query = query.filter(Event.start_datetime >= datetime.utcnow())

        return query.order_by(Event.start_datetime.asc()).all()
