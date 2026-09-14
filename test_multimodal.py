import unittest
import io
from PIL import Image, ImageDraw
from pipeline.uploader import validate_file, save_uploaded_file, ALLOWED_EXTENSIONS
from pipeline.ocr_extractor import extract_from_image
from pipeline.extractor import extract_text
from pipeline.web_extractor import extract_youtube_id, extract_from_url
from pipeline import process_document, process_url


class TestMultimodalIngestion(unittest.TestCase):

    def setUp(self):
        # Create a test synthetic PNG image with text
        self.img = Image.new('RGB', (300, 100), color=(255, 255, 255))
        d = ImageDraw.Draw(self.img)
        d.text((10, 10), "Smart Memory Vault OCR Test 2026", fill=(0, 0, 0))
        d.text((10, 40), "Email: test@example.com Phone: 555-123-4567", fill=(0, 0, 0))
        
        buffer = io.BytesIO()
        self.img.save(buffer, format="PNG")
        self.img_bytes = buffer.getvalue()

    def test_image_extensions_allowed(self):
        """Verify image file formats are allowed in uploader."""
        for ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp"]:
            self.assertIn(ext, ALLOWED_EXTENSIONS)
            valid, msg = validate_file(f"test_file{ext}", 1024)
            self.assertTrue(valid, f"Extension {ext} should be valid: {msg}")

    def test_ocr_extractor_basic(self):
        """Verify image extractor processes raw bytes and returns metadata."""
        result = extract_from_image(self.img_bytes, filename="sample_test.png")
        self.assertIn("text", result)
        self.assertEqual(result.get("format"), "PNG")
        self.assertEqual(result.get("dimensions"), "300x100")
        self.assertTrue(result.get("is_scanned"))

    def test_extractor_routing_for_images(self):
        """Verify extract_text correctly routes .png and .jpg to OCR."""
        result = extract_text(self.img_bytes, ".png", filename="test.png")
        self.assertIn("text", result)
        self.assertEqual(result.get("format"), "PNG")

    def test_process_document_image_pipeline(self):
        """Verify end-to-end document processing for images."""
        res = process_document(self.img_bytes, "ocr_note.png", user_id=999)
        self.assertEqual(res.get("status"), "success")
        self.assertIn("metadata", res)
        self.assertEqual(res["metadata"]["dimensions"], "300x100")
        self.assertIn("extracted_entities", res)

    def test_youtube_id_extractor(self):
        """Test extraction of YouTube IDs from various URL patterns."""
        urls = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtube.com/watch?v=dQw4w9WgXcQ&t=42s", "dQw4w9WgXcQ")
        ]
        for url, expected_id in urls:
            vid_id = extract_youtube_id(url)
            self.assertEqual(vid_id, expected_id, f"Failed for {url}")

    def test_process_url_validation(self):
        """Test process_url handles empty and invalid inputs gracefully."""
        res_empty = process_url("", user_id=1)
        self.assertEqual(res_empty.get("status"), "error")

        res_invalid = process_url("not-a-valid-domain-xyz12345.nonexistent", user_id=1)
        self.assertEqual(res_invalid.get("status"), "error")


if __name__ == "__main__":
    unittest.main()
