"""
Serviço de Gamificação - Gerenciamento de Pontos e Níveis
RF098-RF120: Sistema de pontos, níveis e badges
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging
from typing import Optional, List, Dict
from datetime import datetime

from app.models.user import UserStats
from app.models.points import PointHistory

logger = logging.getLogger(__name__)


class GamificationService:
    """Serviço para gerenciamento de pontos e níveis"""

    # Constantes de pontuação (RF098-RF105)
    POINTS = {
        "create_thread": 10,
        "create_comment": 5,
        "upvote_received": 2,
        "thread_marked_useful": 15,
        "event_participation": 20,
        "complete_profile": 50,
    }

    # Níveis baseados em pontos (RF106-RF109)
    LEVELS = [
        {"name": "Novato", "min_points": 0, "max_points": 100},
        {"name": "Colaborador", "min_points": 101, "max_points": 500},
        {"name": "Conector", "min_points": 501, "max_points": 1000},
        {"name": "Embaixador", "min_points": 1001, "max_points": float("inf")},
    ]

    @staticmethod
    def get_level_from_points(points: int) -> str:
        """Retorna o nível baseado nos pontos"""
        for level in GamificationService.LEVELS:
            if level["min_points"] <= points <= level["max_points"]:
                return level["name"]
        return "Novato"

    @staticmethod
    def get_next_level_info(current_points: int) -> Optional[Dict]:
        """
        Retorna informações sobre o próximo nível

        Returns:
            {
                "next_level": "Colaborador",
                "points_needed": 45,
                "progress_percentage": 55
            }
        """
        current_level = None
        for level in GamificationService.LEVELS:
            if level["min_points"] <= current_points <= level["max_points"]:
                current_level = level
                break

        if not current_level or current_level["name"] == "Embaixador":
            return None

        # Encontrar próximo nível
        next_level_idx = GamificationService.LEVELS.index(current_level) + 1
        if next_level_idx >= len(GamificationService.LEVELS):
            return None

        next_level = GamificationService.LEVELS[next_level_idx]

        points_in_current_level = current_points - current_level["min_points"]
        total_points_in_level = current_level["max_points"] - current_level["min_points"]
        progress_percentage = (points_in_current_level / total_points_in_level) * 100

        return {
            "next_level": next_level["name"],
            "points_needed": next_level["min_points"] - current_points,
            "progress_percentage": round(progress_percentage, 2),
        }

    @staticmethod
    def award_points(
        db: Session,
        user_id: int,
        action_type: str,
        reference_id: Optional[int] = None,
        reference_type: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict:
        """
        Atribui pontos a um usuário por uma ação

        Args:
            db: Sessão do banco
            user_id: ID do usuário
            action_type: Tipo de ação (deve estar em POINTS)
            reference_id: ID da referência (thread_id, comment_id, etc.)
            reference_type: Tipo da referência ('thread', 'comment', etc.)
            description: Descrição opcional

        Returns:
            {
                "points_awarded": 10,
                "total_points": 110,
                "old_level": "Novato",
                "new_level": "Colaborador",
                "level_up": True
            }
        """
        # Verificar se o tipo de ação é válido
        if action_type not in GamificationService.POINTS:
            logger.warning(f"Invalid action type: {action_type}")
            return {
                "points_awarded": 0,
                "total_points": 0,
                "old_level": "Novato",
                "new_level": "Novato",
                "level_up": False,
            }

        points_to_award = GamificationService.POINTS[action_type]

        # Buscar ou criar UserStats
        stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
        if not stats:
            stats = UserStats(user_id=user_id, points=0, level="Novato")
            db.add(stats)
            db.flush()

        # Nível antigo
        old_level = stats.level
        old_points = stats.points

        # Atualizar pontos
        stats.points += points_to_award
        new_level = GamificationService.get_level_from_points(stats.points)
        stats.level = new_level

        # Registrar no histórico
        point_record = PointHistory(
            user_id=user_id,
            points=points_to_award,
            action_type=action_type,
            description=description or f"Pontos por {action_type}",
            reference_id=reference_id,
            reference_type=reference_type,
        )
        db.add(point_record)
        db.commit()

        level_up = old_level != new_level

        if level_up:
            logger.info(
                f"User {user_id} leveled up! {old_level} → {new_level} "
                f"({old_points} → {stats.points} points)"
            )

        return {
            "points_awarded": points_to_award,
            "total_points": stats.points,
            "old_level": old_level,
            "new_level": new_level,
            "level_up": level_up,
        }

    @staticmethod
    def get_user_points_summary(db: Session, user_id: int) -> Dict:
        """
        Retorna resumo completo dos pontos do usuário

        Returns:
            {
                "total_points": 150,
                "current_level": "Colaborador",
                "next_level_info": {...},
                "points_by_action": {...}
            }
        """
        # Buscar stats
        stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
        if not stats:
            return {
                "total_points": 0,
                "current_level": "Novato",
                "next_level_info": GamificationService.get_next_level_info(0),
                "points_by_action": {},
            }

        # Agrupar pontos por tipo de ação
        points_by_action = (
            db.query(
                PointHistory.action_type,
                func.sum(PointHistory.points).label("total"),
                func.count(PointHistory.id).label("count"),
            )
            .filter(PointHistory.user_id == user_id)
            .group_by(PointHistory.action_type)
            .all()
        )

        action_summary = {
            action: {"total_points": total, "count": count}
            for action, total, count in points_by_action
        }

        return {
            "total_points": stats.points,
            "current_level": stats.level,
            "next_level_info": GamificationService.get_next_level_info(stats.points),
            "points_by_action": action_summary,
        }

    @staticmethod
    def get_point_history(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> List[PointHistory]:
        """Retorna histórico de pontos do usuário"""
        return (
            db.query(PointHistory)
            .filter(PointHistory.user_id == user_id)
            .order_by(PointHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_leaderboard(
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Dict]:
        """
        Retorna ranking de usuários por pontos

        Returns:
            [
                {
                    "rank": 1,
                    "user_id": 123,
                    "points": 500,
                    "level": "Colaborador"
                },
                ...
            ]
        """
        # Buscar top usuários por pontos
        top_users = (
            db.query(UserStats)
            .filter(UserStats.points > 0)
            .order_by(UserStats.points.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        leaderboard = []
        for idx, stats in enumerate(top_users, start=skip + 1):
            leaderboard.append(
                {
                    "rank": idx,
                    "user_id": stats.user_id,
                    "points": stats.points,
                    "level": stats.level,
                }
            )

        return leaderboard

    @staticmethod
    def check_profile_completion_bonus(db: Session, user_id: int) -> bool:
        """
        Verifica se o usuário completou o perfil e atribui bônus se necessário

        Perfil completo = 100% preenchido:
        - full_name, university, course, semester, bio
        - Pelo menos 1 interesse
        - Foto de perfil

        Returns:
            True se o bônus foi atribuído (primeira vez)
            False se já tinha recebido ou perfil incompleto
        """
        from app.models.profile import Profile
        from app.models.social import UserInterest

        # Verificar se já recebeu o bônus
        already_awarded = (
            db.query(PointHistory)
            .filter(
                PointHistory.user_id == user_id,
                PointHistory.action_type == "complete_profile",
            )
            .first()
        )

        if already_awarded:
            return False

        # Verificar completude do perfil
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            return False

        # Campos obrigatórios
        if not all(
            [
                profile.full_name,
                profile.university,
                profile.course,
                profile.semester,
                profile.bio,
                profile.photo_url,
            ]
        ):
            return False

        # Pelo menos 1 interesse
        has_interests = (
            db.query(UserInterest)
            .filter(UserInterest.user_id == user_id)
            .count()
            > 0
        )

        if not has_interests:
            return False

        # Perfil completo! Atribuir bônus
        GamificationService.award_points(
            db=db,
            user_id=user_id,
            action_type="complete_profile",
            description="Bônus por completar 100% do perfil",
        )

        logger.info(f"User {user_id} completed profile and received bonus!")
        return True
