import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.repositories.progress import ProgressRepository
from app.schemas.progress import UserMetrics

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
