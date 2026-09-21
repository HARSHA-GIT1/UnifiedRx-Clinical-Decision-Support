"""
OCR Service - text extraction from medical documents (images and PDFs).

Architecture:
- CPU-bound text extraction designed to be run in a worker thread via asyncio.to_thread.
- PDF text extraction with pypdf for digital/text PDFs.
- Image OCR via EasyOCR (CPU-only) with graceful fallback when models are not available.
"""

import logging
from pathlib import Path
from pypdf import PdfReader

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy EasyOCR initialization
# ---------------------------------------------------------------------------
_EASY_OCR_INSTANCE = None
_EASY_OCR_AVAILABLE = None


def _get_easy_ocr():
    """Return a cached EasyOCR Reader, initializing it on first call.

    Construction is wrapped in its own try/except so that network or disk
    failures during the one-time model download are caught here rather than
    propagating up uncaught from a background task.
    """
    global _EASY_OCR_INSTANCE, _EASY_OCR_AVAILABLE
    if _EASY_OCR_AVAILABLE is False:
        return None
    if _EASY_OCR_INSTANCE is None:
        try:
            import easyocr
            logger.info("Initializing EasyOCR Reader (CPU-only, first call may download models)...")
            _EASY_OCR_INSTANCE = easyocr.Reader(["en"], gpu=False)
            _EASY_OCR_AVAILABLE = True
            logger.info("EasyOCR Reader initialized successfully.")
        except Exception as e:
            logger.error(
                "EasyOCR Reader initialization failed (%s). OCR will be unavailable; "
                "digital PDF extraction still works.",
                e,
            )
            _EASY_OCR_AVAILABLE = False
            return None
    return _EASY_OCR_INSTANCE


# ---------------------------------------------------------------------------
# Public extraction function
# ---------------------------------------------------------------------------

def extract_text_from_file(file_path: str | Path, mock_text: str | None = None) -> str:
    """
    Extract raw text from an image or PDF file on disk.

    Synchronous CPU-bound execution (call via asyncio.to_thread).

    Args:
        file_path: Path to the local file
        mock_text: If provided, immediately returns this text (used for deterministic testing).

    Returns:
        Extracted raw text string.
    """
    if mock_text is not None:
        return mock_text

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Document file not found at: {file_path}")

    ext = path.suffix.lower()

    # ------------------------------------------------------------------
    # 1. PDF handling - try digital text extraction first
    # ------------------------------------------------------------------
    if ext == ".pdf":
        try:
            reader = PdfReader(str(path))
            extracted_pages = []
            for page in reader.pages:
                text = page.extract_text() or ""
                if text.strip():
                    extracted_pages.append(text.strip())

            combined_pdf_text = "\n".join(extracted_pages)
            if combined_pdf_text.strip():
                return combined_pdf_text
        except Exception as e:
            logger.warning("Failed to extract digital text from PDF via pypdf: %s", e)

    # ------------------------------------------------------------------
    # 2. Image OCR via EasyOCR (also handles scanned/image-only PDFs)
    # ------------------------------------------------------------------
    ocr = _get_easy_ocr()
    if ocr is not None:
        try:
            results = ocr.readtext(str(path))
            text_lines = [item[1] for item in results if item and len(item) > 1]
            return "\n".join(text_lines)
        except Exception as e:
            logger.error("EasyOCR readtext failed for %s: %s", path.name, e)

    # ------------------------------------------------------------------
    # 3. Fallback: no OCR engine available or all attempts failed
    # ------------------------------------------------------------------
    logger.info("Using empty-text fallback for %s (no OCR engine available)", path.name)
    return ""
