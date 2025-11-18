"""
Serviço de Mentoria
RF068-RF078: Auto-matching de mentores e mentorados
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import logging
from typing import Optional, List, Dict, Tuple
from datetime import datetime

from app.models.mentorship import Mentorship, MentorshipQueue
from app.models.profile import Profile
from app.models.social import UserInterest, Interest
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class MentorshipService:
    """Serviço para gerenciamento de mentorias"""

    MAX_MENTEES_PER_MENTOR = 3  # RF072: Limite de 3 mentorados por mentor
    MIN_SEMESTER_FOR_MENTOR = 4  # RF068: A partir do 4º semestre

    @staticmethod
    def is_eligible_mentor(db: Session, user_id: int) -> Tuple[bool, str]:
        """
        Verifica se o usuário é elegível para ser mentor

        Returns:
            (is_eligible: bool, reason: str)
        """
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()

        if not profile:
            return False, "Perfil não encontrado"

        if not profile.semester:
            return False, "Semestre não configurado no perfil"

        # Extrair número do semestre (ex: "4º" -> 4, "10º" -> 10)
        try:
            semester_num = int(profile.semester.replace("º", "").replace("°", "").strip())
        except ValueError:
            return False, "Formato de semestre inválido"

        if semester_num < MentorshipService.MIN_SEMESTER_FOR_MENTOR:
            return (
                False,
                f"Necessário estar pelo menos no {MentorshipService.MIN_SEMESTER_FOR_MENTOR}º semestre",
            )

        # Verificar se já tem 3 mentorados ativos
        active_mentees = (
            db.query(Mentorship)
            .filter(
                Mentorship.mentor_id == user_id,
                Mentorship.status == "active",
            )
            .count()
        )

        if active_mentees >= MentorshipService.MAX_MENTEES_PER_MENTOR:
            return False, f"Limite de {MentorshipService.MAX_MENTEES_PER_MENTOR} mentorados atingido"

        return True, "Elegível"

    @staticmethod
    def calculate_compatibility(
        db: Session, mentor_id: int, mentee_id: int
    ) -> float:
        """
        Calcula compatibilidade entre mentor e mentee baseado em interesses
        Usa similaridade de Jaccard (mais simples que cosine)

        Returns:
            Score de 0 a 100
        """
        # Buscar interesses do mentor
        mentor_interests = set(
            db.query(UserInterest.interest_id)
            .filter(UserInterest.user_id == mentor_id)
            .all()
        )
        mentor_interests = {i[0] for i in mentor_interests}

        # Buscar interesses do mentee
        mentee_interests = set(
            db.query(UserInterest.interest_id)
            .filter(UserInterest.user_id == mentee_id)
            .all()
        )
        mentee_interests = {i[0] for i in mentee_interests}

        if not mentor_interests or not mentee_interests:
            return 0.0

        # Similaridade de Jaccard
        intersection = mentor_interests.intersection(mentee_interests)
        union = mentor_interests.union(mentee_interests)

        if not union:
            return 0.0

        similarity = len(intersection) / len(union)

        # Converter para escala 0-100
        return round(similarity * 100, 2)

    @staticmethod
    def find_best_mentor(db: Session, mentee_id: int) -> Optional[int]:
        """
        Encontra o melhor mentor disponível para um mentorado

        Critérios:
        1. Estar no 4º semestre ou superior
        2. Ter menos de 3 mentorados ativos
        3. Maior compatibilidade de interesses
        4. Mesma universidade (preferencial)
        """
        # Buscar perfil do mentee
        mentee_profile = db.query(Profile).filter(Profile.user_id == mentee_id).first()

        if not mentee_profile:
            return None

        # Buscar mentores elegíveis (4º semestre+)
        # Nota: Aqui fazemos uma query simplificada, assumindo semestres como "1º", "2º", etc.
        potential_mentors = (
            db.query(Profile)
            .filter(
                Profile.user_id != mentee_id,
                Profile.semester.isnot(None),
            )
            .all()
        )

        eligible_mentors = []

        for mentor_profile in potential_mentors:
            # Verificar elegibilidade
            is_eligible, _ = MentorshipService.is_eligible_mentor(
                db, mentor_profile.user_id
            )

            if not is_eligible:
                continue

            # Calcular compatibilidade
            compatibility = MentorshipService.calculate_compatibility(
                db, mentor_profile.user_id, mentee_id
            )

            # Bônus se mesma universidade
            university_bonus = 10 if mentor_profile.university == mentee_profile.university else 0

            total_score = compatibility + university_bonus

            eligible_mentors.append(
                {
                    "mentor_id": mentor_profile.user_id,
                    "score": total_score,
                    "compatibility": compatibility,
                }
            )

        if not eligible_mentors:
            return None

        # Ordenar por score e pegar o melhor
        eligible_mentors.sort(key=lambda x: x["score"], reverse=True)
        best_mentor = eligible_mentors[0]

        logger.info(
            f"Best mentor for user {mentee_id}: {best_mentor['mentor_id']} "
            f"(score: {best_mentor['score']}, compatibility: {best_mentor['compatibility']}%)"
        )

        return best_mentor["mentor_id"]

    @staticmethod
    def create_mentorship(
        db: Session, mentor_id: int, mentee_id: int
    ) -> Mentorship:
        """
        Cria uma relação de mentoria

        - Verifica elegibilidade do mentor
        - Calcula compatibilidade
        - Notifica ambas as partes
        """
        # Verificar se mentor é elegível
        is_eligible, reason = MentorshipService.is_eligible_mentor(db, mentor_id)

        if not is_eligible:
            raise ValueError(f"Mentor não elegível: {reason}")

        # Verificar se já existe mentoria ativa
        existing = (
            db.query(Mentorship)
            .filter(
                Mentorship.mentor_id == mentor_id,
                Mentorship.mentee_id == mentee_id,
                Mentorship.status == "active",
            )
            .first()
        )

        if existing:
            raise ValueError("Mentoria já existe")

        # Calcular compatibilidade
        compatibility = MentorshipService.calculate_compatibility(db, mentor_id, mentee_id)

        # Criar mentoria
        mentorship = Mentorship(
            mentor_id=mentor_id,
            mentee_id=mentee_id,
            status="active",
            compatibility_score=compatibility,
        )

        db.add(mentorship)

        # Remover da fila se estiver
        db.query(MentorshipQueue).filter(
            MentorshipQueue.user_id == mentee_id
        ).delete()

        db.commit()
        db.refresh(mentorship)

        # Notificar mentor
        mentee_profile = db.query(Profile).filter(Profile.user_id == mentee_id).first()
        if mentee_profile:
            NotificationService.notify_new_mentee(
                db=db,
                mentor_id=mentor_id,
                mentee_name=mentee_profile.full_name,
                mentee_id=mentee_id,
            )

        logger.info(
            f"Created mentorship: mentor={mentor_id}, mentee={mentee_id}, "
            f"compatibility={compatibility}%"
        )

        return mentorship

    @staticmethod
    def request_mentor(db: Session, mentee_id: int) -> Dict:
        """
        Solicita mentor para um mentorado

        1. Tenta fazer auto-matching
        2. Se não encontrar mentor disponível, adiciona à fila

        Returns:
            {
                "status": "matched" ou "queued",
                "mentor_id": int (se matched),
                "message": str
            }
        """
        # Verificar se já tem mentor ativo
        existing = (
            db.query(Mentorship)
            .filter(
                Mentorship.mentee_id == mentee_id,
                Mentorship.status == "active",
            )
            .first()
        )

        if existing:
            return {
                "status": "already_has_mentor",
                "mentor_id": existing.mentor_id,
                "message": "Você já tem um mentor ativo",
            }

        # Tentar encontrar mentor
        best_mentor_id = MentorshipService.find_best_mentor(db, mentee_id)

        if best_mentor_id:
            # Criar mentoria
            mentorship = MentorshipService.create_mentorship(
                db, best_mentor_id, mentee_id
            )

            return {
                "status": "matched",
                "mentor_id": best_mentor_id,
                "compatibility": mentorship.compatibility_score,
                "message": "Mentor encontrado e atribuído!",
            }

        # Não encontrou mentor, adicionar à fila
        # Verificar se já está na fila
        in_queue = (
            db.query(MentorshipQueue)
            .filter(MentorshipQueue.user_id == mentee_id)
            .first()
        )

        if not in_queue:
            queue_entry = MentorshipQueue(
                user_id=mentee_id,
                priority_score=0.0,  # TODO: Calcular prioridade baseado em tempo de espera
            )
            db.add(queue_entry)
            db.commit()

        return {
            "status": "queued",
            "message": "Sem mentores disponíveis no momento. Você foi adicionado à fila de espera.",
        }

    @staticmethod
    def complete_mentorship(
        db: Session, mentorship_id: int, user_id: int
    ) -> bool:
        """
        Finaliza uma mentoria

        - Mentor ou mentee podem finalizar
        """
        mentorship = db.query(Mentorship).filter(Mentorship.id == mentorship_id).first()

        if not mentorship:
            raise ValueError("Mentoria não encontrada")

        if mentorship.mentor_id != user_id and mentorship.mentee_id != user_id:
            raise ValueError("Apenas mentor ou mentee podem finalizar a mentoria")

        if mentorship.status != "active":
            raise ValueError("Mentoria não está ativa")

        mentorship.status = "completed"
        mentorship.completed_at = datetime.utcnow()
        db.commit()

        logger.info(f"Mentorship {mentorship_id} completed by user {user_id}")

        return True

    @staticmethod
    def process_queue(db: Session, limit: int = 10) -> int:
        """
        Processa fila de espera tentando fazer matching

        Chamado periodicamente (ex: cronjob)

        Returns:
            Número de matches realizados
        """
        # Buscar primeiros da fila
        queue_entries = (
            db.query(MentorshipQueue)
            .order_by(MentorshipQueue.requested_at.asc())
            .limit(limit)
            .all()
        )

        matches_made = 0

        for entry in queue_entries:
            # Tentar encontrar mentor
            best_mentor_id = MentorshipService.find_best_mentor(db, entry.user_id)

            if best_mentor_id:
                try:
                    MentorshipService.create_mentorship(
                        db, best_mentor_id, entry.user_id
                    )
                    matches_made += 1
                except ValueError as e:
                    logger.warning(f"Failed to create mentorship: {e}")
                    continue

        logger.info(f"Processed {len(queue_entries)} queue entries, made {matches_made} matches")

        return matches_made
