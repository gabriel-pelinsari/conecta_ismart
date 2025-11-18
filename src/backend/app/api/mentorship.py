import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.mentorship import Mentorship, MentorshipQueue
from app.models.profile import Profile
from app.schemas.mentorship import (
    MentorshipOut,
    MentorshipRequestResponse,
    MentorOut,
    QueuePositionOut,
)
from app.services.mentorship_service import MentorshipService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mentorship", tags=["mentorship"])


@router.post("/request-mentor", response_model=MentorshipRequestResponse)
def request_mentor(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    🎓 Solicitar mentor

    - Tenta fazer auto-matching
    - Se não encontrar, adiciona à fila
    - Baseado em compatibilidade de interesses
    """
    logger.info(f"🎓 User {current_user.id} requesting mentor")

    result = MentorshipService.request_mentor(db, current_user.id)

    return MentorshipRequestResponse(**result)


@router.get("/available-mentors", response_model=List[MentorOut])
def list_available_mentors(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    📋 Listar mentores disponíveis

    - Mostra mentores elegíveis (4º semestre+)
    - Com slots disponíveis (< 3 mentorados)
    - Ordenado por compatibilidade
    """
    logger.info(f"📋 User {current_user.id} listing available mentors")

    # Buscar perfis de potenciais mentores
    profiles = db.query(Profile).filter(Profile.user_id != current_user.id).all()

    available_mentors = []

    for profile in profiles:
        # Verificar elegibilidade
        is_eligible, _ = MentorshipService.is_eligible_mentor(db, profile.user_id)

        if not is_eligible:
            continue

        # Contar mentorados ativos
        active_mentees = (
            db.query(Mentorship)
            .filter(
                Mentorship.mentor_id == profile.user_id,
                Mentorship.status == "active",
            )
            .count()
        )

        available_mentors.append(
            MentorOut(
                user_id=profile.user_id,
                full_name=profile.full_name,
                university=profile.university,
                course=profile.course,
                semester=profile.semester,
                photo_url=profile.photo_url,
                active_mentees=active_mentees,
                available_slots=MentorshipService.MAX_MENTEES_PER_MENTOR
                - active_mentees,
            )
        )

    return available_mentors


@router.get("/my-mentees", response_model=List[MentorshipOut])
def get_my_mentees(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    👥 Meus mentorados (se for mentor)

    - Lista mentorados ativos
    - Inclui informações do perfil
    """
    logger.info(f"👥 User {current_user.id} viewing their mentees")

    mentorships = (
        db.query(Mentorship)
        .filter(
            Mentorship.mentor_id == current_user.id,
            Mentorship.status == "active",
        )
        .all()
    )

    result = []
    for mentorship in mentorships:
        mentee_profile = (
            db.query(Profile).filter(Profile.user_id == mentorship.mentee_id).first()
        )

        mentorship_out = MentorshipOut.model_validate(mentorship)
        if mentee_profile:
            mentorship_out.mentee_name = mentee_profile.full_name
            mentorship_out.mentee_photo = mentee_profile.photo_url

        result.append(mentorship_out)

    return result


@router.get("/my-mentor", response_model=MentorshipOut)
def get_my_mentor(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    🎓 Meu mentor (se for mentorado)

    - Retorna mentor ativo
    - Inclui informações do perfil
    """
    logger.info(f"🎓 User {current_user.id} viewing their mentor")

    mentorship = (
        db.query(Mentorship)
        .filter(
            Mentorship.mentee_id == current_user.id,
            Mentorship.status == "active",
        )
        .first()
    )

    if not mentorship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Você não tem um mentor ativo",
        )

    mentor_profile = (
        db.query(Profile).filter(Profile.user_id == mentorship.mentor_id).first()
    )

    mentorship_out = MentorshipOut.model_validate(mentorship)
    if mentor_profile:
        mentorship_out.mentor_name = mentor_profile.full_name
        mentorship_out.mentor_photo = mentor_profile.photo_url

    return mentorship_out


@router.post("/complete/{mentorship_id}", response_model=dict)
def complete_mentorship(
    mentorship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    ✅ Finalizar mentoria

    - Mentor ou mentee podem finalizar
    """
    logger.info(f"✅ User {current_user.id} completing mentorship {mentorship_id}")

    try:
        MentorshipService.complete_mentorship(
            db=db,
            mentorship_id=mentorship_id,
            user_id=current_user.id,
        )

        return {
            "status": "success",
            "message": "Mentoria finalizada com sucesso",
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/queue/my-position", response_model=QueuePositionOut)
def get_my_queue_position(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    📊 Minha posição na fila de espera
    """
    logger.info(f"📊 User {current_user.id} checking queue position")

    queue_entry = (
        db.query(MentorshipQueue)
        .filter(MentorshipQueue.user_id == current_user.id)
        .first()
    )

    if not queue_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Você não está na fila de espera",
        )

    # Calcular posição na fila
    position = (
        db.query(MentorshipQueue)
        .filter(MentorshipQueue.requested_at < queue_entry.requested_at)
        .count()
        + 1
    )

    total_in_queue = db.query(MentorshipQueue).count()

    return QueuePositionOut(
        position=position,
        total_in_queue=total_in_queue,
        requested_at=queue_entry.requested_at,
    )


@router.get("/stats", response_model=dict)
def get_mentorship_stats(
    db: Session = Depends(get_db),
):
    """
    📊 Estatísticas do sistema de mentoria

    - Total de mentorias ativas
    - Pessoas na fila
    - Mentores disponíveis
    """
    active_mentorships = (
        db.query(Mentorship).filter(Mentorship.status == "active").count()
    )

    in_queue = db.query(MentorshipQueue).count()

    # Contar mentores com slots disponíveis
    all_profiles = db.query(Profile).all()
    available_mentors = 0

    for profile in all_profiles:
        is_eligible, _ = MentorshipService.is_eligible_mentor(db, profile.user_id)
        if is_eligible:
            available_mentors += 1

    return {
        "active_mentorships": active_mentorships,
        "in_queue": in_queue,
        "available_mentors": available_mentors,
    }
