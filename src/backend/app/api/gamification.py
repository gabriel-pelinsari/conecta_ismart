import logging
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.profile import Profile
from app.schemas.gamification import (
    PointHistoryOut,
    PointsSummary,
    LevelInfo,
    LeaderboardEntry,
)
from app.services.gamification import GamificationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/gamification", tags=["gamification"])


@router.get("/my-points", response_model=PointsSummary)
def get_my_points(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    📊 Retorna resumo completo dos pontos do usuário atual

    - Total de pontos
    - Nível atual
    - Informações sobre próximo nível
    - Pontos agrupados por tipo de ação
    """
    logger.info(f"📊 User {current_user.id} requesting points summary")

    summary = GamificationService.get_user_points_summary(db, current_user.id)

    return PointsSummary(
        total_points=summary["total_points"],
        current_level=summary["current_level"],
        next_level_info=summary["next_level_info"],
        points_by_action=summary["points_by_action"],
    )


@router.get("/history", response_model=List[PointHistoryOut])
def get_points_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    📜 Retorna histórico de pontos do usuário

    - Mostra todas as ações que geraram pontos
    - Ordenado por data (mais recente primeiro)
    - Suporta paginação
    """
    logger.info(f"📜 User {current_user.id} requesting points history")

    history = GamificationService.get_point_history(db, current_user.id, skip, limit)

    return [
        PointHistoryOut(
            id=entry.id,
            points=entry.points,
            action_type=entry.action_type,
            description=entry.description,
            reference_id=entry.reference_id,
            reference_type=entry.reference_type,
            created_at=entry.created_at,
        )
        for entry in history
    ]


@router.get("/levels", response_model=List[LevelInfo])
def get_all_levels():
    """
    📋 Lista todos os níveis disponíveis

    - Mostra requisitos de pontos para cada nível
    - Níveis: Novato, Colaborador, Conector, Embaixador
    """
    logger.info("📋 Listing all levels")

    levels = []
    for level in GamificationService.LEVELS:
        levels.append(
            LevelInfo(
                name=level["name"],
                min_points=level["min_points"],
                max_points=level["max_points"],
            )
        )

    return levels


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
def get_leaderboard(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """
    🏆 Retorna ranking dos usuários por pontos

    - Top usuários ordenados por pontos
    - Inclui rank, pontos e nível
    - Suporta paginação
    """
    logger.info("🏆 Fetching leaderboard")

    leaderboard = GamificationService.get_leaderboard(db, skip, limit)

    # Enriquecer com dados do perfil
    result = []
    for entry in leaderboard:
        profile = (
            db.query(Profile).filter(Profile.user_id == entry["user_id"]).first()
        )

        result.append(
            LeaderboardEntry(
                rank=entry["rank"],
                user_id=entry["user_id"],
                points=entry["points"],
                level=entry["level"],
                full_name=profile.full_name if profile else None,
                photo_url=profile.photo_url if profile else None,
            )
        )

    return result


@router.get("/points-info", response_model=dict)
def get_points_info():
    """
    ℹ️ Retorna informações sobre o sistema de pontos

    - Pontos por tipo de ação
    - Descrição do sistema de níveis
    """
    logger.info("ℹ️ Fetching points system info")

    return {
        "points_per_action": GamificationService.POINTS,
        "levels": [
            {
                "name": level["name"],
                "min_points": level["min_points"],
                "max_points": level["max_points"]
                if level["max_points"] != float("inf")
                else None,
            }
            for level in GamificationService.LEVELS
        ],
        "description": {
            "pt": "Sistema de pontos e níveis do ISMART Conecta. "
            "Ganhe pontos por participar ativamente da comunidade!",
            "actions": {
                "create_thread": "Criar uma nova discussão",
                "create_comment": "Comentar em uma discussão",
                "upvote_received": "Receber um upvote",
                "thread_marked_useful": "Ter sua discussão marcada como útil",
                "event_participation": "Participar de um evento",
                "complete_profile": "Completar 100% do perfil",
            },
        },
    }


@router.post("/check-profile-bonus", response_model=dict)
def check_profile_completion_bonus(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    🎁 Verifica se o usuário completou o perfil e atribui bônus

    - Verifica se perfil está 100% completo
    - Atribui 50 pontos se for a primeira vez
    - Retorna status da verificação
    """
    logger.info(f"🎁 User {current_user.id} checking profile completion bonus")

    bonus_awarded = GamificationService.check_profile_completion_bonus(
        db, current_user.id
    )

    if bonus_awarded:
        return {
            "bonus_awarded": True,
            "points": 50,
            "message": "Parabéns! Você ganhou 50 pontos por completar seu perfil!",
        }
    else:
        return {
            "bonus_awarded": False,
            "points": 0,
            "message": "Perfil incompleto ou bônus já recebido",
        }
