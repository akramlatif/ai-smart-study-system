import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.repositories.session import SessionRepository
from app.repositories.topic import TopicRepository

router = APIRouter(tags=["dashboard"])


@router.get("/users/{user_id}/sessions")
async def get_user_sessions(
    user_id: str,
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    repo = SessionRepository(db)
    sessions = await repo.get_user_sessions(uuid.UUID(user_id), limit=limit, offset=offset)

    result = []
    for s in sessions:
        result.append({
            "id": str(s.id),
            "user_id": str(s.user_id),
            "previous_id": str(s.previous_id) if s.previous_id else None,
            "created_at": s.created_at.isoformat(),
            "ended_at": s.ended_at.isoformat() if s.ended_at else None,
            "interaction_count": s.interaction_count,
        })
    return result


@router.get("/users/{user_id}/synthesis-suggestions")
async def get_synthesis_suggestions(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    # Get recent sessions and their topics
    session_repo = SessionRepository(db)
    sessions = await session_repo.get_user_sessions(uuid.UUID(user_id), limit=5)

    suggestions = []
    topic_repo = TopicRepository(db)
    for session in sessions:
        topics = await topic_repo.get_by_session(session.id)
        for topic in topics:
            if topic.is_main:
                suggestions.append({
                    "topic": topic.name,
                    "relevance_tag": "high_relevance" if topic.confidence >= 0.85 else "review_needed",
                    "last_studied": session.created_at.isoformat(),
                })

    return suggestions[:10]
