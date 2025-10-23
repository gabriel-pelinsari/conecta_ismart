from app.schemas.profile import ProfileStats, ProfileBadge
from typing import List

def get_user_stats(user_id: int) -> ProfileStats:
    # TODO: integrar com threads, comments, events
    return ProfileStats(threads_count=0, comments_count=0, events_count=0)

def get_user_badges(user_id: int) -> List[ProfileBadge]:
    # TODO: integrar com badges reais
    return []
