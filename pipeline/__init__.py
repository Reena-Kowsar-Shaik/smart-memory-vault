from .uploader import save_uploaded_file
from .extractor import extract_text
from .regex_cleaner import clean_text, extract_entities

def process_document(file_bytes: bytes, filename: str, user_id: int):
    """
    Main function for Member 4 & Member 1 to call:
    Takes file bytes, filename, and user_id.
    Returns validated, saved, extracted, and cleaned data with regex entities.
    """
    upload = save_uploaded_file(file_bytes, filename, user_id)
    if not upload.get("success"):
        return {"status": "error", "error_message": upload.get("error")}

    extracted = extract_text(file_bytes, upload["extension"])
    if "error" in extracted:
        return {"status": "error", "error_message": extracted["error"]}

    cleaned = clean_text(extracted.get("text", ""))
    entities = extract_entities(cleaned)

    metadata = {
        "original_filename": upload["original_filename"],
        "stored_path": upload["stored_path"],
        "file_hash": upload["file_hash"],
        "file_size": upload["file_size"],
        "page_count": extracted.get("page_count", 1),
        "word_count": len(cleaned.split()) if cleaned else 0,
        "is_duplicate": upload["is_duplicate"],
        "is_scanned": extracted.get("is_scanned", False)
    }

    return {
        "status": "success",
        "metadata": metadata,
        "cleaned_text": cleaned,
        "extracted_entities": entities
    }
