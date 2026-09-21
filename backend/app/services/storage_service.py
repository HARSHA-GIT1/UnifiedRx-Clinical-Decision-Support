"""
Storage service — manages file uploads, path sanitization, size limits,
and local disk persistence.
"""

import os
import uuid
from pathlib import Path
from fastapi import HTTPException, UploadFile, status

# Default upload directory: backend/uploads
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", Path(__file__).resolve().parent.parent.parent / "uploads"))
MAX_UPLOAD_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB max

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",
}


def ensure_upload_dir() -> Path:
    """Ensure the upload directory exists and return its Path."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    return UPLOAD_DIR


async def save_uploaded_file(file: UploadFile) -> tuple[str, str, int]:
    """
    Validate, sanitize, and save an uploaded file to disk.

    Args:
        file: FastAPI UploadFile

    Returns:
        tuple of (original_filename, absolute_storage_path, file_size_bytes)

    Raises:
        HTTPException: 400 for disallowed file types, 413 for oversized files.
    """
    original_filename = file.filename or "uploaded_document"
    ext = Path(original_filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension '{ext}' is not supported. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # Validate content-type if provided
    if file.content_type and file.content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Content type '{file.content_type}' is not supported. Allowed: PDF and standard images (PNG, JPEG).",
        )

    ensure_upload_dir()
    unique_filename = f"{uuid.uuid4()}{ext}"
    destination = UPLOAD_DIR / unique_filename

    total_size = 0
    chunk_size = 1024 * 64  # 64 KB chunks

    try:
        with open(destination, "wb") as buffer:
            while chunk := await file.read(chunk_size):
                total_size += len(chunk)
                if total_size > MAX_UPLOAD_SIZE_BYTES:
                    # Remove partially written file
                    buffer.close()
                    if destination.exists():
                        destination.unlink()
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File exceeds maximum allowed size of {MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)}MB.",
                    )
                buffer.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        if destination.exists():
            destination.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to write uploaded file to disk: {str(e)}",
        )

    return original_filename, str(destination), total_size
