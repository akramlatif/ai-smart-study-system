from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.schemas.profile import LearnerProfile
from app.services.learner_profile import LearnerProfileService

router = APIRouter(tags=["profile"])


@router.get("/users/{user_id}/profile", response_model=LearnerProfile)
async def get_learner_profile(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Return the adaptive learner profile for a user."""
    # Users can only view their own profile
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    service = LearnerProfileService(db)
    profile = await service.build_profile(user_id)
    return profile
