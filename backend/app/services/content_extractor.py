"""
ContentExtractor service — extracts text from PDFs and text files.
"""
import os
import uuid
import aiofiles
from app.schemas.document import QualityAssessment
from app.core.config import settings


def _quality_flag(char_count: int) -> str:
    if char_count >= 50:
        return "ok"
    return "low_quality"


def extract_pdf(file_path: str) -> dict:
    """
    Extract text from a PDF file using PyMuPDF.

    Returns:
        dict with keys: text, char_count, quality_flag
    """
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(file_path)
        pages_text = []
        for page in doc:
            pages_text.append(page.get_text("text"))
        doc.close()

        text = "\n".join(pages_text)
        char_count = len(text)
        flag = _quality_flag(char_count)
        return {"text": text, "char_count": char_count, "quality_flag": flag}
    except Exception:
        return {"text": "", "char_count": 0, "quality_flag": "unreadable"}


def extract_text_file(file_path: str) -> dict:
    """
    Extract text from a plain text file (UTF-8).

    Returns:
        dict with keys: text, char_count, quality_flag
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        char_count = len(text)
        flag = _quality_flag(char_count)
        return {"text": text, "char_count": char_count, "quality_flag": flag}
    except Exception:
        return {"text": "", "char_count": 0, "quality_flag": "unreadable"}


def assess_quality(text: str) -> QualityAssessment:
    """
    Assess the quality of extracted text.
    """
    char_count = len(text)
    if char_count >= 50:
        flag = "ok"
        message = None
    else:
        flag = "low_quality"
        message = "Extracted text is too short (< 50 characters). The document may be low quality."
    return QualityAssessment(char_count=char_count, flag=flag, message=message)


async def save_file(
    file_bytes: bytes,
    filename: str,
    user_id: str,
    session_id: str,
) -> str:
    """
    Save uploaded file bytes to disk.

    Returns:
        storage_path (relative to UPLOAD_DIR)
    """
    dir_path = os.path.join(settings.UPLOAD_DIR, user_id, session_id)
    os.makedirs(dir_path, exist_ok=True)
    # Sanitize filename
    safe_name = os.path.basename(filename)
    file_path = os.path.join(dir_path, safe_name)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(file_bytes)
    return file_path


def delete_file(storage_path: str) -> None:
    """
    Delete a file from disk if it exists.
    """
    try:
        if os.path.exists(storage_path):
            os.remove(storage_path)
    except OSError:
        pass
