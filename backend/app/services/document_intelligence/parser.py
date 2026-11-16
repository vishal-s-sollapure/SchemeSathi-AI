import hashlib
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import fitz  # PyMuPDF

from app.config import settings

logger = logging.getLogger("document_parser")


class DocumentParser:
    """Production PDF validator, text extractor, and page tracker with OCR fallback detection."""

    MAX_SIZE_BYTES = getattr(settings, "MAX_UPLOAD_SIZE_BYTES", 15 * 1024 * 1024)  # 15MB
    MAGIC_HEADER = b"%PDF-"

    @classmethod
    def validate_file(cls, file_bytes: bytes, filename: str) -> None:
        """Validates file size, file extension, magic header, and basic PDF integrity.
        
        Raises ValueError if invalid.
        """
        # 1. Size Limit Check
        if len(file_bytes) > cls.MAX_SIZE_BYTES:
            max_mb = cls.MAX_SIZE_BYTES / (1024 * 1024)
            actual_mb = len(file_bytes) / (1024 * 1024)
            raise ValueError(f"File size ({actual_mb:.2f} MB) exceeds maximum allowed limit of {max_mb:.0f} MB")

        # 2. Extension Check
        clean_ext = Path(filename).suffix.lower()
        if clean_ext != ".pdf":
            raise ValueError(f"Unsupported file format '{clean_ext}'. Only verified PDF documents are supported.")

        # 3. Magic Header Check
        if not file_bytes.startswith(cls.MAGIC_HEADER):
            raise ValueError("Corrupted or invalid PDF header. File does not appear to be a genuine PDF document.")

        # 4. PyMuPDF Structural Integrity Check
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            if len(doc) == 0:
                doc.close()
                raise ValueError("PDF document contains zero pages.")
            doc.close()
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Corrupted or encrypted PDF document cannot be parsed: {str(e)}")

    @classmethod
    def calculate_sha256(cls, file_bytes: bytes) -> str:
        """Computes deterministic SHA256 checksum."""
        return hashlib.sha256(file_bytes).hexdigest()

    @classmethod
    def extract_text_and_metadata(
        cls, file_bytes: bytes, filename: str
    ) -> Tuple[List[Dict[str, Any]], bool, int]:
        """Extracts text page-by-page from PDF with page tracking and OCR fallback detection.
        
        Returns:
            Tuple of (pages_text_list, ocr_applied, total_pages)
        """
        cls.validate_file(file_bytes, filename)

        pages_text: List[Dict[str, Any]] = []
        ocr_applied = False

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        total_pages = len(doc)

        for page_idx in range(total_pages):
            page_num = page_idx + 1
            page = doc[page_idx]

            # 1. Direct text extraction
            raw_text = page.get_text("text").strip()
            char_count = len(raw_text)

            # Check if this page is a scanned image with minimal/zero extractable text
            images = page.get_images()
            is_scanned = False

            if char_count < 25 and len(images) > 0:
                is_scanned = True
                ocr_applied = True
                # OCR Fallback: Try alternative PyMuPDF blocks or layout words
                blocks = page.get_text("blocks")
                block_texts = [b[4].strip() for b in blocks if len(b) > 4 and b[4].strip()]
                if block_texts:
                    raw_text = "\n".join(block_texts)
                    char_count = len(raw_text)
                else:
                    # Mark scanned page with structural notification for downstream candidate processing
                    raw_text = (
                        f"[SCANNED_DOCUMENT_PAGE_{page_num}] Scanned image-based document page detected "
                        f"({len(images)} image objects found). Document text requires optical verification."
                    )

            pages_text.append({
                "page_number": page_num,
                "text": raw_text,
                "char_count": char_count,
                "is_scanned": is_scanned,
            })

        doc.close()
        return pages_text, ocr_applied, total_pages

    @classmethod
    def save_file_securely(
        cls, file_bytes: bytes, original_filename: str, upload_dir: Optional[Path] = None
    ) -> Tuple[Path, str]:
        """Saves uploaded file securely to designated directory preventing path traversal.
        
        Returns:
            Tuple of (destination_path, safe_storage_filename)
        """
        # Determine upload directory
        base_dir = upload_dir or Path(getattr(settings, "UPLOAD_DIR", "app/uploads"))
        if not base_dir.is_absolute():
            base_dir = Path(__file__).resolve().parent.parent.parent / base_dir
        base_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize filename
        safe_base = os.path.basename(original_filename)
        # Strip path traversal characters
        safe_base = safe_base.replace("..", "").replace("/", "").replace("\\", "").strip()
        if not safe_base.lower().endswith(".pdf"):
            safe_base += ".pdf"

        sha256 = cls.calculate_sha256(file_bytes)
        unique_filename = f"{sha256[:12]}_{safe_base}"
        dest_path = base_dir / unique_filename

        with open(dest_path, "wb") as f:
            f.write(file_bytes)

        return dest_path, unique_filename
