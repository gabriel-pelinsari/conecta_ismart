import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.event import Event, EventParticipant
from app.models.profile import Profile
from app.schemas.event import (
    EventCreate,
    EventUpdate,
    EventOut,
    EventRSVP,
    EventStatsOut,
    ParticipantOut,
)
from app.services.event_service import EventService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/events", tags=["events"])


@router.post("/", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    📅 Criar novo evento

    - Qualquer usuário pode criar eventos
    - Validação de datas (end > start)
    """
    logger.info(f"📅 User {current_user.id} creating event: {event_data.title}")

    # Validar datas
    if event_data.end_datetime <= event_data.start_datetime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data de término deve ser posterior à data de início",
        )

    # Criar evento
    new_event = Event(
        title=event_data.title,
        description=event_data.description,
        event_type=event_data.event_type,
        start_datetime=event_data.start_datetime,
        end_datetime=event_data.end_datetime,
        location=event_data.location,
        is_online=event_data.is_online,
        online_link=event_data.online_link,
        university=event_data.university,
        max_participants=event_data.max_participants,
        created_by=current_user.id,
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    # Criar resposta
    event_out = EventOut.model_validate(new_event)
    event_out.participant_count = 0

    return event_out


@router.get("/", response_model=List[EventOut])
def list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    event_type: Optional[str] = Query(None),
    university: Optional[str] = Query(None),
    include_past: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    📋 Listar eventos

    - Filtrar por tipo, universidade
    - Por padrão mostra apenas eventos futuros
    - Ordenado por data de início
    """
    logger.info(f"📋 Listing events (type={event_type}, uni={university})")

    query = db.query(Event).filter(Event.is_cancelled == False)

    if event_type:
        query = query.filter(Event.event_type == event_type)

    if university:
        query = query.filter(Event.university == university)

    if not include_past:
        query = query.filter(Event.start_datetime >= datetime.utcnow())

    events = query.order_by(Event.start_datetime.asc()).offset(skip).limit(limit).all()

    # Enriquecer com contagens
    result = []
    for event in events:
        stats = EventService.get_event_stats(db, event.id)
        event_out = EventOut.model_validate(event)
        event_out.participant_count = stats["total_rsvp"]

        # Verificar RSVP do usuário
        participant = (
            db.query(EventParticipant)
            .filter(
                EventParticipant.event_id == event.id,
                EventParticipant.user_id == current_user.id,
            )
            .first()
        )
        event_out.user_rsvp_status = participant.status if participant else None

        result.append(event_out)

    return result


@router.get("/{event_id}", response_model=EventOut)
def get_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    🔍 Ver detalhes de um evento
    """
    logger.info(f"🔍 User {current_user.id} viewing event {event_id}")

    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado",
        )

    stats = EventService.get_event_stats(db, event_id)
    event_out = EventOut.model_validate(event)
    event_out.participant_count = stats["total_rsvp"]

    # Verificar RSVP do usuário
    participant = (
        db.query(EventParticipant)
        .filter(
            EventParticipant.event_id == event_id,
            EventParticipant.user_id == current_user.id,
        )
        .first()
    )
    event_out.user_rsvp_status = participant.status if participant else None

    return event_out


@router.put("/{event_id}", response_model=EventOut)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    ✏️ Atualizar evento

    - Apenas o criador pode atualizar
    """
    logger.info(f"✏️ User {current_user.id} updating event {event_id}")

    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado",
        )

    if event.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o criador pode atualizar o evento",
        )

    # Atualizar campos fornecidos
    update_data = event_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)

    # Validar datas se ambas fornecidas
    if event.end_datetime <= event.start_datetime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data de término deve ser posterior à data de início",
        )

    db.commit()
    db.refresh(event)

    event_out = EventOut.model_validate(event)
    stats = EventService.get_event_stats(db, event_id)
    event_out.participant_count = stats["total_rsvp"]

    return event_out


@router.delete("/{event_id}", response_model=dict)
def cancel_event(
    event_id: int,
    reason: Optional[str] = Query(None, max_length=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    ❌ Cancelar evento

    - Apenas o criador pode cancelar
    - Motivo opcional
    """
    logger.info(f"❌ User {current_user.id} cancelling event {event_id}")

    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado",
        )

    if event.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o criador pode cancelar o evento",
        )

    event.is_cancelled = True
    event.cancelled_reason = reason
    db.commit()

    # TODO: Notificar participantes sobre cancelamento

    return {"status": "success", "message": "Evento cancelado"}


@router.post("/{event_id}/rsvp", response_model=dict)
def rsvp_to_event(
    event_id: int,
    rsvp_data: EventRSVP,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    ✅ Confirmar presença em evento

    - Status: confirmed, maybe, declined
    - Verifica limite de participantes
    """
    logger.info(f"✅ User {current_user.id} RSVPing to event {event_id}: {rsvp_data.status}")

    try:
        participant = EventService.rsvp_event(
            db=db,
            event_id=event_id,
            user_id=current_user.id,
            status=rsvp_data.status,
        )

        return {
            "status": "success",
            "message": f"RSVP registrado como '{rsvp_data.status}'",
            "rsvp_status": participant.status,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{event_id}/participants", response_model=List[ParticipantOut])
def list_event_participants(
    event_id: int,
    status_filter: Optional[str] = Query(None, pattern="^(confirmed|maybe|declined)$"),
    db: Session = Depends(get_db),
):
    """
    👥 Listar participantes de um evento

    - Filtrar por status
    - Inclui informações do perfil
    """
    logger.info(f"👥 Listing participants for event {event_id}")

    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado",
        )

    query = db.query(EventParticipant).filter(EventParticipant.event_id == event_id)

    if status_filter:
        query = query.filter(EventParticipant.status == status_filter)

    participants = query.all()

    # Enriquecer com dados do perfil
    result = []
    for participant in participants:
        profile = (
            db.query(Profile).filter(Profile.user_id == participant.user_id).first()
        )

        result.append(
            ParticipantOut(
                user_id=participant.user_id,
                full_name=profile.full_name if profile else None,
                photo_url=profile.photo_url if profile else None,
                status=participant.status,
                attended=participant.attended,
                joined_at=participant.joined_at,
            )
        )

    return result


@router.get("/{event_id}/stats", response_model=EventStatsOut)
def get_event_statistics(
    event_id: int,
    db: Session = Depends(get_db),
):
    """
    📊 Estatísticas do evento

    - Contagem por status
    - Presenças marcadas
    """
    stats = EventService.get_event_stats(db, event_id)
    return EventStatsOut(**stats)


@router.post("/{event_id}/mark-attendance/{user_id}", response_model=dict)
def mark_participant_attendance(
    event_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    ✅ Marcar presença de participante (Criador only)

    - Atribui +20 pontos ao participante
    - Apenas criador do evento pode marcar
    """
    logger.info(f"✅ User {current_user.id} marking attendance for user {user_id} at event {event_id}")

    try:
        marked = EventService.mark_attendance(
            db=db,
            event_id=event_id,
            user_id=user_id,
            creator_id=current_user.id,
        )

        if marked:
            return {
                "status": "success",
                "message": "Presença marcada e pontos atribuídos",
            }
        else:
            return {
                "status": "already_marked",
                "message": "Presença já estava marcada",
            }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/my/events", response_model=List[EventOut])
def get_my_events(
    status_filter: Optional[str] = Query(None, pattern="^(confirmed|maybe|declined)$"),
    include_past: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    📅 Meus eventos

    - Eventos que estou participando
    - Filtrar por status de RSVP
    """
    events = EventService.get_user_events(
        db=db,
        user_id=current_user.id,
        status=status_filter,
        include_past=include_past,
    )

    result = []
    for event in events:
        stats = EventService.get_event_stats(db, event.id)
        event_out = EventOut.model_validate(event)
        event_out.participant_count = stats["total_rsvp"]

        # Pegar status do usuário
        participant = (
            db.query(EventParticipant)
            .filter(
                EventParticipant.event_id == event.id,
                EventParticipant.user_id == current_user.id,
            )
            .first()
        )
        event_out.user_rsvp_status = participant.status if participant else None

        result.append(event_out)

    return result
