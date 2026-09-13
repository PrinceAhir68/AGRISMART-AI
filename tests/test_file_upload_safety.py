"""
AgriSmart AI - Automated File Upload Security Test Suite
Validates that:
1. Disallowed file extensions (.py, .exe, .sh, .php, .svg, .bat, .html) are strictly rejected with HTTP 400.
2. Extension spoofing (non-image payload disguised with .jpg extension) is caught by magic bytes and rejected.
3. Empty and sub-minimum files (<100 bytes) are rejected with HTTP 400.
4. Oversized files (>10 MB) are rejected with HTTP 413 without memory or disk exhaustion.
5. Path traversal attempts in filenames (../../test_leaf.jpg) are sanitized to base names.
6. Uploaded files are stored strictly outside the web root (app/static) in isolated storage.
7. Temporary upload files are guaranteed to be unlinked/cleaned up after processing.
8. Valid agricultural leaf image uploads process normally with HTTP 200.
"""

import os
import io
import sys
import unittest
from PIL import Image
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.main import app
from app.modules.file_security import (
    ISOLATED_UPLOAD_DIR, verify_storage_is_isolated,
    validate_extension, verify_magic_bytes, sanitize_filename,
    FileValidationError, validate_image_content
)


class TestFileUploadSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app, raise_server_exceptions=False)
        cls.static_dir = os.path.join(PROJECT_ROOT, "app", "static")
        cls.sample_dir = os.path.join(PROJECT_ROOT, "model", "test_samples")

    def test_1_isolated_storage_is_outside_web_root(self):
        """Verify upload storage directory is strictly outside app/static (the web root)."""
        is_isolated = verify_storage_is_isolated(self.static_dir)
        self.assertTrue(is_isolated, "Isolated upload dir must NEVER be inside the static web root!")
        
        abs_upload = os.path.abspath(ISOLATED_UPLOAD_DIR)
        abs_static = os.path.abspath(self.static_dir)
        self.assertFalse(abs_upload.startswith(abs_static))

    def test_2_reject_disallowed_extensions(self):
        """Verify uploads with dangerous executable or script extensions are rejected immediately."""
        dangerous_extensions = [
            ("exploit.py", b"# benign python script\n", "text/x-python"),
            ("payload.exe", b"BENIGN_TEST_BINARY_DATA", "application/octet-stream"),
            ("script.sh", b"# benign shell script\n", "application/x-sh"),
            ("shell.php", b"<?php echo 'test'; ?>", "application/x-php"),
            ("vector.svg", b"<svg xmlns='http://www.w3.org/2000/svg'><circle cx='10' cy='10' r='5'/></svg>", "image/svg+xml"),
            ("batch.bat", b"@echo off\necho test", "application/x-bat"),
            ("webpage.html", b"<html><body>Test HTML</body></html>", "text/html"),
        ]

        for fname, content, ctype in dangerous_extensions:
            resp = self.client.post(
                "/api/predict",
                files={"file": (fname, content, ctype)}
            )
            self.assertEqual(
                resp.status_code, 400,
                f"File '{fname}' with extension should have been rejected with 400 Bad Request, got {resp.status_code}"
            )
            data = resp.json()
            err_msg = str(data.get("detail", ""))
            self.assertIn("Unsupported file extension", err_msg)

    def test_3_reject_extension_spoofing(self):
        """Verify that disguising plain text as .jpg is caught by magic bytes inspection."""
        fake_jpg_content = b"This is plain text data not an image.\n" * 10
        resp = self.client.post(
            "/api/predict",
            files={"file": ("fake_leaf.jpg", fake_jpg_content, "image/jpeg")}
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        err_msg = str(data.get("detail", ""))
        self.assertIn("Invalid file signature", err_msg)

    def test_4_reject_empty_and_sub_minimum_files(self):
        """Verify empty and tiny files (<100 bytes) are rejected."""
        # 0 bytes
        resp_empty = self.client.post(
            "/api/predict",
            files={"file": ("empty.jpg", b"", "image/jpeg")}
        )
        self.assertEqual(resp_empty.status_code, 400)

        # Sub-minimum bytes (e.g., 20 bytes of dummy JPEG header)
        tiny_bytes = b"\xFF\xD8\xFF\xE0" + b"\x00" * 16
        resp_tiny = self.client.post(
            "/api/predict",
            files={"file": ("tiny.jpg", tiny_bytes, "image/jpeg")}
        )
        self.assertEqual(resp_tiny.status_code, 400)
        data = resp_tiny.json()
        self.assertIn("minimum file size", str(data.get("detail", "")))

    def test_5_reject_oversized_file(self):
        """Verify files exceeding 10 MB are rejected with HTTP 413 Payload Too Large."""
        oversized_len = 10 * 1024 * 1024 + 1024 * 100
        header = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00"
        oversized_data = header + (b"\x00" * (oversized_len - len(header)))

        resp = self.client.post(
            "/api/predict",
            files={"file": ("large_leaf.jpg", oversized_data, "image/jpeg")}
        )
        self.assertEqual(
            resp.status_code, 413,
            f"Expected HTTP 413 for oversized file, got {resp.status_code}"
        )
        data = resp.json()
        err_msg = str(data.get("detail", ""))
        self.assertIn("exceeds maximum allowable limit", err_msg)

    def test_6_path_traversal_in_filename_sanitization(self):
        """Verify filenames with path traversal (../../test_leaf.jpg) are sanitized to simple base names."""
        raw_traversal = "../../test_leaf.jpg"
        clean = sanitize_filename(raw_traversal)
        self.assertEqual(clean, "test_leaf.jpg")
        self.assertNotIn("..", clean)
        self.assertNotIn("/", clean)
        self.assertNotIn("\\", clean)

        # Null byte injection attempt
        null_traversal = "leaf.jpg" + chr(0) + ".exe"
        clean_null = sanitize_filename(null_traversal)
        self.assertEqual(clean_null, "leaf.jpg.exe")
        with self.assertRaises(FileValidationError):
            validate_extension(clean_null)

    def test_7_decompression_bomb_dimension_threshold(self):
        """Verify image with excessive dimensions (>8000px) is rejected to prevent Decompression Bomb attacks."""
        img_buffer = io.BytesIO()
        huge_img = Image.new("RGB", (8500, 50), color="green")
        huge_img.save(img_buffer, format="JPEG")
        huge_bytes = img_buffer.getvalue()

        resp = self.client.post(
            "/api/predict",
            files={"file": ("huge_aspect.jpg", huge_bytes, "image/jpeg")}
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertIn("exceeds maximum allowable dimension", str(data.get("detail", "")))

    def test_8_valid_image_upload_success_and_cleanup(self):
        """Verify a valid leaf photo processes successfully and leaves no temporary files behind."""
        sample_path = os.path.join(self.sample_dir, "tomato_early_blight.jpg")
        self.assertTrue(os.path.isfile(sample_path), "Sample tomato leaf must exist for test")

        files_before = set(os.listdir(ISOLATED_UPLOAD_DIR))

        with open(sample_path, "rb") as f:
            file_bytes = f.read()

        resp = self.client.post(
            "/api/predict",
            files={"file": ("tomato_early_blight.jpg", file_bytes, "image/jpeg")},
            data={"target_crop": "Tomato"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("crop"), "Tomato")
        self.assertIn("class_label", data)
        self.assertTrue(data.get("confidence", 0) > 0.5)

        # Verify 100% temporary file cleanup in isolated storage
        files_after = set(os.listdir(ISOLATED_UPLOAD_DIR))
        new_files = files_after - files_before
        self.assertEqual(len(new_files), 0, f"Temporary upload files were leaked in isolated storage: {new_files}")


if __name__ == "__main__":
    unittest.main()
