from typing import List
from sqlalchemy.orm import Session

from app.schemas.profile import ProfileStats, ProfileBadge
from app.models.user import UserStats
from app.models.gamification import Badge, UserBadge


def _ensure_stats(user_id: int, db: Session) -> UserStats:
    """Garantir que o registro de estat��sticas exista no banco."""
    stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
    if stats:
        return stats

    stats = UserStats(user_id=user_id)
    db.add(stats)
    db.commit()
    db.refresh(stats)
    return stats


def get_user_stats(user_id: int, db: Session) -> ProfileStats:
    """Busca estat��sticas reais do usuǭrio e mapeia para o schema esperado."""
    stats = _ensure_stats(user_id, db)

    # Modelos antigos possuem campos `threads_count`, etc. O atual usa `total_*`.
    threads = getattr(stats, "threads_count", None)
    if threads is None:
        threads = getattr(stats, "total_posts", 0)

    comments = getattr(stats, "comments_count", None)
    if comments is None:
        comments = getattr(stats, "total_comments", 0)

    events = getattr(stats, "events_count", None)
    if events is None:
        events = getattr(stats, "total_friendships", 0)

    return ProfileStats(
        threads_count=threads or 0,
        comments_count=comments or 0,
        events_count=events or 0,
    )


def get_user_badges(user_id: int, db: Session) -> List[ProfileBadge]:
    """Busca badges conquistadas pelo usuǭrio"""
    badges = (
        db.query(Badge)
        .join(UserBadge)
        .filter(UserBadge.user_id == user_id)
        .all()
    )

    results = []
    for badge in badges:
        key = getattr(badge, "code", None) or badge.name or f"badge-{badge.id}"
        icon = getattr(badge, "icon", None)
        if icon is None:
            icon = getattr(badge, "icon_url", None)

        results.append(
            ProfileBadge(
                key=key,
                name=badge.name,
                icon_url=icon,
            )
        )

    return results
