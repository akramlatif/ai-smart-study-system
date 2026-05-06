import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.document import Document


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        filename: str,
        file_type: str,
        file_size_bytes: int,
        storage_path: str,
        quality_flag: str,
        expires_at: datetime,
    ) -> Document:
        doc = Document(
            id=uuid.uuid4(),
            session_id=session_id,
            user_id=user_id,
            filename=filename,
            file_type=file_type,
            file_size_bytes=file_size_bytes,
            storage_path=storage_path,
            quality_flag=quality_flag,
            expires_at=expires_at,
        )
        self.db.add(doc)
        await self.db.flush()
        await self.db.refresh(doc)
        return doc

    async def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, document_id: uuid.UUID) -> bool:
        doc = await self.get_by_id(document_id)
        if doc:
            await self.db.delete(doc)
            await self.db.flush()
            return True
        return False

    async def get_expired(self) -> list[Document]:
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(Document).where(Document.expires_at <= now)
        )
        return list(result.scalars().all())
