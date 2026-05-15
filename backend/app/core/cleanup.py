"""
Document expiry cleanup job.
Deletes uploaded documents when their session ends or after 24 hours.
"""
import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.document import Document
from app.services.content_extractor import delete_file

logger = logging.getLogger(__name__)


async def cleanup_expired_documents(db: AsyncSession) -> int:
    """
    Delete all documents that have passed their expires_at timestamp.
    Returns the number of documents deleted.
    """
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Document).where(Document.expires_at <= now)
    )
    expired_docs = result.scalars().all()

    deleted_count = 0
    for doc in expired_docs:
        try:
            delete_file(doc.storage_path)
            await db.delete(doc)
            deleted_count += 1
        except Exception as e:
            logger.error(f"Failed to delete document {doc.id}: {e}")

    if deleted_count > 0:
        await db.commit()
        logger.info(f"Cleaned up {deleted_count} expired documents.")

    return deleted_count


async def run_cleanup_loop(get_db_func, interval_seconds: int = 3600) -> None:
    """
    Background task that runs document cleanup every interval_seconds.
    Default: every hour.
    """
    while True:
        try:
            async for db in get_db_func():
                await cleanup_expired_documents(db)
        except Exception as e:
            logger.error(f"Cleanup job error: {e}")
        await asyncio.sleep(interval_seconds)
