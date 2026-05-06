import uuid
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.repositories.document import DocumentRepository
from app.repositories.session import SessionRepository
from app.schemas.document import DocumentUploadResponse
import app.services.input_handler as input_handler
import app.services.content_extractor as content_extractor

router = APIRouter(tags=["documents"])


@router.post(
    "/sessions/{session_id}/documents",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    session_id: str,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    # Verify session ownership
    session_repo = SessionRepository(db)
    session = await session_repo.get_by_id(uuid.UUID(session_id))
    if not session or str(session.user_id) != user_id:
        raise HTTPException(status_code=404, detail="Session not found.")

    file_bytes = await file.read()
    validation = input_handler.validate_file(
        file.filename or "upload", len(file_bytes), file.content_type or ""
    )
    if not validation.valid:
        raise HTTPException(status_code=422, detail=validation.error_message)

    storage_path = await content_extractor.save_file(
        file_bytes, file.filename or "upload", user_id, session_id
    )

    lower = (file.filename or "").lower()
    if lower.endswith(".pdf"):
        result = content_extractor.extract_pdf(storage_path)
        file_type = "pdf"
    else:
        result = content_extractor.extract_text_file(storage_path)
        file_type = "text"

    quality_flag = result["quality_flag"]
    char_count = result["char_count"]

    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    doc_repo = DocumentRepository(db)
    doc = await doc_repo.create(
        session_id=uuid.UUID(session_id),
        user_id=uuid.UUID(user_id),
        filename=file.filename or "upload",
        file_type=file_type,
        file_size_bytes=len(file_bytes),
        storage_path=storage_path,
        quality_flag=quality_flag,
        expires_at=expires_at,
    )

    return DocumentUploadResponse(
        document_id=str(doc.id),
        quality_flag=quality_flag,
        extracted_char_count=char_count,
    )


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    doc_repo = DocumentRepository(db)
    doc = await doc_repo.get_by_id(uuid.UUID(document_id))
    if not doc or str(doc.user_id) != user_id:
        raise HTTPException(status_code=404, detail="Document not found.")

    content_extractor.delete_file(doc.storage_path)
    await doc_repo.delete(uuid.UUID(document_id))
    return {"deleted": True}
