import os
import re
import hashlib
from pathlib import Path
from typing import Tuple, Dict, Any

# Supported extensions (Docs & Images) and maximum upload size (100 MB)
ALLOWED_EXTENSIONS = {
    ".pdf", ".docx", ".txt", ".md",
    ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"
}
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB
STORAGE_BASE_DIR = Path("storage")

def sanitize_filename(filename: str) -> str:
    """Sanitizes filename to prevent directory traversal and illegal characters."""
    clean_name = os.path.basename(filename)
    clean_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', clean_name)
    return clean_name or "uploaded_document"

def calculate_sha256(file_bytes: bytes) -> str:
    """Calculates SHA-256 hash to detect duplicate file uploads."""
    return hashlib.sha256(file_bytes).hexdigest()

def validate_file(filename: str, file_size: int) -> Tuple[bool, str]:
    """Validates file format and size limits."""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported format '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
    if file_size > MAX_FILE_SIZE_BYTES:
        return False, f"File exceeds maximum size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB."
    if file_size == 0:
        return False, "Uploaded file is empty."
    return True, ""

def save_uploaded_file(file_bytes: bytes, original_filename: str, user_id: int) -> Dict[str, Any]:
    """
    Saves file into user-isolated directory: storage/user_<id>/documents/
    Returns structured metadata and duplicate status.
    """
    is_valid, err_msg = validate_file(original_filename, len(file_bytes))
    if not is_valid:
        return {"success": False, "error": err_msg}

    file_hash = calculate_sha256(file_bytes)
    user_dir = STORAGE_BASE_DIR / f"user_{user_id}" / "documents"
    user_dir.mkdir(parents=True, exist_ok=True)

    clean_name = sanitize_filename(original_filename)
    stored_filename = f"{file_hash[:10]}_{clean_name}"
    target_path = user_dir / stored_filename

    is_duplicate = target_path.exists()
    if not is_duplicate:
        with open(target_path, "wb") as f:
            f.write(file_bytes)

    return {
        "success": True,
        "original_filename": original_filename,
        "stored_path": str(target_path.resolve()),
        "file_hash": file_hash,
        "file_size": len(file_bytes),
        "is_duplicate": is_duplicate,
        "extension": Path(original_filename).suffix.lower()
    }
