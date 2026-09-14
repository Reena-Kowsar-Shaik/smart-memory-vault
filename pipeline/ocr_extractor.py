import io
import os
from typing import Dict, Any

try:
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError:
    Image = None

try:
    import pytesseract
    # Check common Windows install paths for tesseract binary if not in PATH
    if os.name == 'nt':
        default_tesseract_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe")
        ]
        for t_path in default_tesseract_paths:
            if os.path.exists(t_path):
                pytesseract.pytesseract.tesseract_cmd = t_path
                break
except ImportError:
    pytesseract = None

try:
    import easyocr
    _easyocr_reader = None
except ImportError:
    easyocr = None
    _easyocr_reader = None


def preprocess_image_for_ocr(img: Any) -> Any:
    """Preprocesses an image with grayscale conversion and contrast boost for better OCR."""
    if img is None:
        return None
    try:
        # Convert to grayscale
        gray = img.convert("L")
        # Boost contrast
        enhancer = ImageEnhance.Contrast(gray)
        enhanced = enhancer.enhance(1.8)
        return enhanced
    except Exception:
        return img


def extract_from_image(file_bytes: bytes, filename: str = "") -> Dict[str, Any]:
    """
    Extracts text from images (whiteboards, scanned notes, receipts, certificates)
    using a multi-engine OCR fallback pipeline (pytesseract -> easyocr -> PIL metadata).
    """
    if Image is None:
        return {
            "text": "",
            "page_count": 1,
            "is_scanned": True,
            "error": "Pillow (PIL) is not installed."
        }

    try:
        img = Image.open(io.BytesIO(file_bytes))
        width, height = img.size
        img_format = img.format or "IMAGE"
        mode = img.mode
    except Exception as e:
        return {
            "text": "",
            "page_count": 1,
            "is_scanned": True,
            "error": f"Failed to decode image: {str(e)}"
        }

    extracted_text = ""
    engine_used = None

    # Method 1: PyTesseract OCR
    if pytesseract is not None:
        try:
            processed_img = preprocess_image_for_ocr(img)
            text = pytesseract.image_to_string(processed_img, timeout=10)
            if text and text.strip():
                extracted_text = text.strip()
                engine_used = "Tesseract OCR"
        except Exception:
            pass

    # Method 2: EasyOCR fallback
    if not extracted_text and easyocr is not None:
        try:
            global _easyocr_reader
            if _easyocr_reader is None:
                _easyocr_reader = easyocr.Reader(['en'], gpu=False)
            results = _easyocr_reader.readtext(file_bytes)
            if results:
                extracted_text = "\n".join([res[1] for res in results if len(res) > 1 and res[1].strip()])
                if extracted_text:
                    engine_used = "EasyOCR"
        except Exception:
            pass

    # Method 3: Fallback / Metadata extraction
    if not extracted_text:
        # If no OCR engine extracted text, provide image profile context
        extracted_text = f"[Image: {filename or 'Uploaded Image'}] (Format: {img_format}, Dimensions: {width}x{height}, Mode: {mode})"
        engine_used = "Image Metadata Parser"

    return {
        "text": extracted_text,
        "page_count": 1,
        "is_scanned": True,
        "engine_used": engine_used,
        "dimensions": f"{width}x{height}",
        "format": img_format
    }
