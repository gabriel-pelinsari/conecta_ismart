from typing import Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime


class PointHistoryOut(BaseModel):
    """Schema for point history entry"""
    id: int
    points: int
    action_type: str
    description: Optional[str] = None
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NextLevelInfo(BaseModel):
    """Information about next level"""
    next_level: str
    points_needed: int
    progress_percentage: float


class PointsSummary(BaseModel):
    """Complete points summary for user"""
    total_points: int
    current_level: str
    next_level_info: Optional[NextLevelInfo] = None
    points_by_action: Dict[str, Dict[str, int]]


class LevelInfo(BaseModel):
    """Information about a level"""
    name: str
    min_points: int
    max_points: float


class LeaderboardEntry(BaseModel):
    """Entry in the leaderboard"""
    rank: int
    user_id: int
    points: int
    level: str
    full_name: Optional[str] = None
    photo_url: Optional[str] = None


class PointsAwardResponse(BaseModel):
    """Response when points are awarded"""
    points_awarded: int
    total_points: int
    old_level: str
    new_level: str
    level_up: bool
