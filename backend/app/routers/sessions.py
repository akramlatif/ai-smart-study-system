from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import get_redis
from app.core.security import get_current_user_id
from app.repositories.session import SessionRepository
from app.schemas.session import SessionResponse, StudySession, SessionSummary
import app.services.session_manager as session_manager

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis: Any = Depends(get_redis),
):
    session = await session_manager.create_session(user_id, db, redis)
    return SessionResponse(session_id=session.id, created_at=session.created_at)


@router.get("/{session_id}", response_model=StudySession)
async def get_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis: Any = Depends(get_redis),
):
    session = await session_manager.get_session(session_id, db, redis)
    if not session or session.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    return session


@router.get("/{session_id}/summary", response_model=SessionSummary)
async def get_session_summary(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis: Any = Depends(get_redis),
):
    session = await session_manager.get_session(session_id, db, redis)
    if not session or session.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    return await session_manager.get_summary(session_id, db, redis)


@router.post("/{session_id}/reset")
async def reset_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis: Any = Depends(get_redis),
):
    session = await session_manager.get_session(session_id, db, redis)
    if not session or session.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    new_session = await session_manager.reset_session(session_id, user_id, db, redis)
    return {"new_session_id": new_session.id, "previous_session_id": session_id}


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis: Any = Depends(get_redis),
):
    session = await session_manager.get_session(session_id, db, redis)
    if not session or session.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    repo = SessionRepository(db)
    await repo.end_session(session_id)
    await redis.delete(f"session:{session_id}")
    return {"deleted": True}
