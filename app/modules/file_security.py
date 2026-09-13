"""
AgriSmart AI - File Security & Isolated Storage Subsystem
Provides rigorous validation for all file uploads:
1. File extension whitelist (.jpg, .jpeg, .png, .webp, .bmp)
2. Magic bytes inspection (JPEG, PNG, WEBP, BMP signatures)
3. Chunked file size enforcement (Default max 10MB, min 100 bytes)
4. Decompression bomb prevention & dimension threshold checks (Pillow)
5. Isolated storage outside the web root with non-executable permissions
6. Guaranteed cleanup via context manager
"""

import os
import sys
import secrets
import logging
import tempfile
import contextlib
from typing import Tuple, Optional
from PIL import Image
from fastapi import UploadFile

logger = logging.getLogger("agrismart.file_security")

# Configuration Constants
MAX_UPLOAD_SIZE_BYTES = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", 10 * 1024 * 1024))  # 10 MB
MIN_UPLOAD_SIZE_BYTES = int(os.getenv("MIN_UPLOAD_SIZE_BYTES", 100))               # 100 Bytes
MAX_IMAGE_DIMENSION = int(os.getenv("MAX_IMAGE_DIMENSION", 8000))                  # 8000 px
MAX_IMAGE_PIXELS = int(os.getenv("MAX_IMAGE_PIXELS", 25_000_000))                  # 25 MP

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
ALLOWED_MIME_TYPES = {
    "image/jpeg", "image/pjpeg", "image/png", "image/x-png",
    "image/webp", "image/bmp", "image/x-ms-bmp"
}

# Dedicated isolated directory outside the web root
ISOLATED_UPLOAD_DIR = os.getenv(
    "AGRISMART_UPLOAD_DIR",
    os.path.join(tempfile.gettempdir(), "agrismart_isolated_uploads")
)
os.makedirs(ISOLATED_UPLOAD_DIR, exist_ok=True)


class FileValidationError(Exception):
    """Raised when an uploaded file violates security or validation policies."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def sanitize_filename(raw_filename: Optional[str]) -> str:
    """
    Sanitizes raw client-supplied filenames.
    Strips directory traversal sequences, null bytes, and path delimiters.
    """
    if not raw_filename:
        return "unnamed_upload.jpg"
    base = os.path.basename(raw_filename)
    # Strip null bytes and non-printable control characters
    cleaned = "".join(c for c in base if c.isprintable() and c not in ['\0', '/', '\\', ':', '*', '?', '"', '<', '>', '|'])
    return cleaned.strip() or "unnamed_upload.jpg"


def validate_extension(filename: str) -> str:
    """
    Validates file extension against allowed whitelist.
    Returns normalized lowercase extension (e.g., '.jpg').
    """
    _, ext = os.path.splitext(filename)
    ext_lower = ext.lower().strip()
    if not ext_lower or ext_lower not in ALLOWED_EXTENSIONS:
        raise FileValidationError(
            f"Unsupported file extension '{ext_lower or 'none'}'. "
            f"Only valid image formats (JPG, PNG, WEBP, BMP) are accepted.",
            status_code=400
        )
    return ext_lower


def verify_magic_bytes(header: bytes) -> str:
    """
    Inspects initial file bytes to verify authentic image file signatures.
    Rejects disguised executables, scripts, or non-image payloads.
    """
    if len(header) < 4:
        raise FileValidationError("Uploaded file is too small or incomplete to verify format.", status_code=400)

    # 1. JPEG: starts with FF D8 FF
    if header.startswith(b"\xFF\xD8\xFF"):
        return "JPEG"

    # 2. PNG: starts with 89 50 4E 47 0D 0A 1A 0A
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "PNG"

    # 3. WEBP: starts with RIFF and contains WEBP at index 8..12
    if header.startswith(b"RIFF") and len(header) >= 12 and header[8:12] == b"WEBP":
        return "WEBP"

    # 4. BMP: starts with BM (42 4D)
    if header.startswith(b"BM"):
        return "BMP"

    raise FileValidationError(
        "Invalid file signature. The file content does not match an authentic image format.",
        status_code=400
    )


def save_upload_to_isolated_storage(upload_file: UploadFile) -> Tuple[str, str]:
    """
    Safely streams uploaded file to isolated storage with size and signature enforcement.
    Returns tuple: (isolated_file_path, sanitized_client_filename).
    """
    clean_name = sanitize_filename(upload_file.filename)
    ext = validate_extension(clean_name)

    # Optional MIME type check if provided by client
    if upload_file.content_type:
        mime = upload_file.content_type.lower().split(";")[0].strip()
        # Permit image/* or explicitly allowed MIME types
        if mime not in ALLOWED_MIME_TYPES and not mime.startswith("image/"):
            raise FileValidationError(
                f"Invalid MIME content type '{upload_file.content_type}'. Please upload an image.",
                status_code=400
            )

    # Cryptographically random destination filename in isolated directory
    token = secrets.token_hex(16)
    dest_filename = f"leaf_{token}{ext}"
    dest_path = os.path.join(ISOLATED_UPLOAD_DIR, dest_filename)

    chunk_size = 64 * 1024  # 64 KB chunks
    total_bytes = 0
    first_chunk = True

    try:
        with open(dest_path, "wb") as out_f:
            while True:
                chunk = upload_file.file.read(chunk_size)
                if not chunk:
                    break

                # Validate magic bytes on initial chunk
                if first_chunk:
                    verify_magic_bytes(chunk[:32])
                    first_chunk = False

                total_bytes += len(chunk)
                if total_bytes > MAX_UPLOAD_SIZE_BYTES:
                    max_mb = MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)
                    raise FileValidationError(
                        f"File size exceeds maximum allowable limit of {max_mb} MB.",
                        status_code=413
                    )

                out_f.write(chunk)

        # Minimum size check
        if total_bytes < MIN_UPLOAD_SIZE_BYTES:
            raise FileValidationError(
                "Uploaded file is empty or corrupted (under minimum file size).",
                status_code=400
            )

        # Restrict permissions (read/write only by current owner, no execute)
        try:
            os.chmod(dest_path, 0o600)
        except Exception:
            pass

        return dest_path, clean_name

    except Exception:
        # Guarantee partial file deletion on error
        if os.path.exists(dest_path):
            try:
                os.remove(dest_path)
            except Exception:
                pass
        raise


def validate_image_content(file_path: str) -> None:
    """
    Deep content validation using Pillow.
    Catches decompression bombs, corrupted streams, and invalid geometries.
    """
    # Configure decompression bomb limit
    Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS

    # 1. Structural integrity verification
    try:
        with Image.open(file_path) as img:
            img.verify()
    except Image.DecompressionBombError:
        raise FileValidationError(
            "Image exceeds safe pixel density thresholds (potential decompression bomb).",
            status_code=400
        )
    except Exception as e:
        logger.warning("Pillow verify() failed on uploaded file: %s", e)
        raise FileValidationError(
            "Uploaded image file is corrupted or contains an invalid structure.",
            status_code=400
        )

    # 2. Re-open to inspect dimensions and format (verify() closes file handle in PIL)
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
                raise FileValidationError(
                    f"Image resolution ({width}x{height}) exceeds maximum allowable dimension of {MAX_IMAGE_DIMENSION}px.",
                    status_code=400
                )
            if img.format not in ["JPEG", "PNG", "WEBP", "BMP"]:
                raise FileValidationError(
                    f"Unsupported image encoding format '{img.format}'.",
                    status_code=400
                )
    except FileValidationError:
        raise
    except Exception as e:
        logger.warning("Failed reading image dimensions: %s", e)
        raise FileValidationError("Unable to parse image dimensions or geometry.", status_code=400)


@contextlib.contextmanager
def secure_isolated_upload(upload_file: UploadFile):
    """
    Context manager that streams, validates, and stores an upload in isolated storage,
    then guarantees file removal upon exit.
    Yields tuple: (isolated_file_path, sanitized_filename)
    """
    dest_path = None
    try:
        dest_path, clean_name = save_upload_to_isolated_storage(upload_file)
        validate_image_content(dest_path)
        yield dest_path, clean_name
    finally:
        if dest_path and os.path.exists(dest_path):
            try:
                os.remove(dest_path)
            except Exception as e:
                logger.warning("Could not unlink temporary upload file %s: %s", dest_path, e)


def verify_storage_is_isolated(static_dir: str) -> bool:
    """Verifies that the upload storage directory is completely outside the static web root."""
    abs_upload = os.path.abspath(ISOLATED_UPLOAD_DIR)
    abs_static = os.path.abspath(static_dir)
    return not abs_upload.startswith(abs_static)
