from .uploader import save_uploaded_file, ALLOWED_EXTENSIONS
from .extractor import extract_text
from .regex_cleaner import clean_text, extract_entities
from .ocr_extractor import extract_from_image
from .web_extractor import extract_from_url, extract_youtube_transcript, extract_web_article, extract_youtube_id

def process_document(file_bytes: bytes, filename: str, user_id: int):
    """
    Takes file bytes (Doc or Image), filename, and user_id.
    Saves file, extracts text (including OCR for images), cleans text, and identifies regex entities.
    """
    upload = save_uploaded_file(file_bytes, filename, user_id)
    if not upload.get("success"):
        return {"status": "error", "error_message": upload.get("error")}

    extracted = extract_text(file_bytes, upload["extension"], filename=filename)
    if "error" in extracted and not extracted.get("text"):
        return {"status": "error", "error_message": extracted["error"]}

    raw_text = extracted.get("text", "")
    cleaned = clean_text(raw_text)
    entities = extract_entities(cleaned)

    metadata = {
        "original_filename": upload["original_filename"],
        "stored_path": upload["stored_path"],
        "file_hash": upload["file_hash"],
        "file_size": upload["file_size"],
        "page_count": extracted.get("page_count", 1),
        "word_count": len(cleaned.split()) if cleaned else 0,
        "is_duplicate": upload["is_duplicate"],
        "is_scanned": extracted.get("is_scanned", False),
        "engine_used": extracted.get("engine_used"),
        "dimensions": extracted.get("dimensions"),
        "format": extracted.get("format")
    }

    return {
        "status": "success",
        "metadata": metadata,
        "cleaned_text": cleaned,
        "extracted_entities": entities
    }


def process_url(url: str, user_id: int):
    """
    Takes a Web article or YouTube URL, extracts clean text/transcript,
    cleans the text, and extracts entities.
    """
    res = extract_from_url(url)
    if res.get("status") == "error":
        return {"status": "error", "error_message": res.get("error", "Failed to process URL.")}

    raw_text = res.get("text", "")
    cleaned = clean_text(raw_text)
    entities = extract_entities(cleaned)

    metadata = {
        "type": res.get("type"),
        "title": res.get("title"),
        "author": res.get("author"),
        "source_url": res.get("source_url"),
        "thumbnail_url": res.get("thumbnail_url"),
        "video_id": res.get("video_id"),
        "word_count": len(cleaned.split()) if cleaned else 0
    }

    return {
        "status": "success",
        "metadata": metadata,
        "cleaned_text": cleaned,
        "extracted_entities": entities
    }
