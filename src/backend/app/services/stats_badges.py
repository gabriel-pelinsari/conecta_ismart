from app.schemas.profile import ProfileStats, ProfileBadge
from typing import List
from sqlalchemy.orm import Session
from app.models.user import UserStats
from app.models.gamification import Badge, UserBadge

def get_user_stats(user_id: int, db: Session) -> ProfileStats:
    """Busca estatísticas reais do usuário"""
    stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
    
    if not stats:
        stats = UserStats(
            user_id=user_id,
            threads_count=0,
            comments_count=0,
            events_count=0
        )
        db.add(stats)
        db.commit()
        db.refresh(stats)
    
    return ProfileStats(
        threads_count=stats.threads_count,
        comments_count=stats.comments_count,
        events_count=stats.events_count
    )

def get_user_badges(user_id: int, db: Session) -> List[ProfileBadge]:
    """Busca badges conquistadas pelo usuário"""
    badges = (
        db.query(Badge)
        .join(UserBadge)
        .filter(UserBadge.user_id == user_id)
        .all()
    )
    
    return [
        ProfileBadge(
            key=badge.code,
            name=badge.name,
            icon_url=badge.icon
        )
        for badge in badges
    ]