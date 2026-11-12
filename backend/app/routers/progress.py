import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.repositories.progress import ProgressRepository
from app.schemas.progress import UserMetrics, WeeklyActivity, StudyStreak

router = APIRouter(tags=["progress"])


@router.get("/progress/metrics", response_model=UserMetrics)
async def get_metrics(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated learning metrics for the current user."""
    progress_repo = ProgressRepository(db)
    metrics = await progress_repo.get_user_metrics(uuid.UUID(user_id))
    return UserMetrics(**metrics)


@router.get("/progress/weekly-activity", response_model=WeeklyActivity)
async def get_weekly_activity(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get sessions and quiz questions per day for the last 7 days."""
    progress_repo = ProgressRepository(db)
    activity = await progress_repo.get_weekly_activity(uuid.UUID(user_id))
    return WeeklyActivity(**activity)


@router.get("/progress/streak", response_model=StudyStreak)
async def get_study_streak(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get the user's current and longest study streaks."""
    progress_repo = ProgressRepository(db)
    streak = await progress_repo.get_study_streak(uuid.UUID(user_id))
    return StudyStreak(**streak)
