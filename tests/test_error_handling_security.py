"""
AgriSmart AI - Automated Security & Error Handling Test Suite
Validates that:
1. Internal stack traces, raw tracebacks, and internal file paths are NEVER exposed to clients.
2. Raw database errors and SQL schemas are masked behind clean, user-friendly responses.
3. Global exception handlers catch unhandled Exceptions and SQLite errors gracefully.
4. HTTPExceptions with accidental path disclosures have paths actively redacted.
5. Server-side loggers capture full exception details and tracebacks (exc_info=True) for developer debugging.
"""

import os
import sys
import unittest
import logging
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import sqlite3

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.main import app
from app.database import (
    register_user, authenticate_user, update_user_profile,
    change_user_password, reset_user_password, save_diagnosis_record
)


class LogCaptureHandler(logging.Handler):
    """Custom in-memory log capturing handler to verify server-side logging."""
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(record)


class TestErrorHandlingSecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app, raise_server_exceptions=False)
        cls.api_logger = logging.getLogger("agrismart.api")
        cls.db_logger = logging.getLogger("agrismart.database")

    def setUp(self):
        self.log_handler = LogCaptureHandler()
        self.api_logger.addHandler(self.log_handler)
        self.db_logger.addHandler(self.log_handler)

    def tearDown(self):
        self.api_logger.removeHandler(self.log_handler)
        self.db_logger.removeHandler(self.log_handler)

    def test_unhandled_exception_returns_clean_500_and_logs_server_traceback(self):
        """Verify that an unexpected crash returns generic 500 JSON without leaking traceback to client."""
        with patch("app.main.get_weather_intelligence", side_effect=RuntimeError("Secret internal fault: C:\\Secrets\\key.txt")):
            resp = self.client.get("/api/weather?lat=23.0&lon=72.0")
            self.assertEqual(resp.status_code, 500)
            
            body_text = resp.text
            # Client must NEVER see the internal exception string, paths, or tracebacks
            self.assertNotIn("Traceback (most recent call last)", body_text)
            self.assertNotIn("C:\\Secrets", body_text)
            self.assertNotIn("RuntimeError", body_text)
            
            # Response must be structured generic JSON
            data = resp.json()
            self.assertEqual(data.get("error"), "internal_server_error")
            self.assertIn("unexpected error occurred", data.get("message", ""))

            # Verify server-side logger received the error with full traceback
            error_records = [r for r in self.log_handler.records if r.levelno >= logging.ERROR]
            self.assertTrue(len(error_records) > 0, "Server-side logger did not record the 500 error!")
            found_logged_traceback = any(r.exc_info is not None for r in error_records)
            self.assertTrue(found_logged_traceback, "Server-side log record is missing traceback exc_info!")

    def test_database_error_does_not_leak_raw_sql_or_schema(self):
        """Verify that database errors log tracebacks server-side and return generic safe messages."""
        with patch("sqlite3.connect", side_effect=sqlite3.OperationalError("near 'SYNTAX_ERR': syntax error in table users")):
            res = register_user(
                name="Security Test",
                email_or_phone="9999900000",
                password="TestPassword123"
            )
            # Must return clean failure dictionary
            self.assertFalse(res["success"])
            # Client message must not leak SQLite internal error or table schema
            err_msg = res.get("error", "")
            self.assertNotIn("syntax error", err_msg)
            self.assertNotIn("near 'SYNTAX_ERR'", err_msg)
            self.assertIn("temporarily unavailable", err_msg)

            # Verify server log captured the operational error with traceback
            db_error_records = [r for r in self.log_handler.records if r.levelno >= logging.ERROR]
            self.assertTrue(len(db_error_records) > 0)
            logged_messages = [r.getMessage() for r in db_error_records]
            self.assertTrue(any("Database error" in m for m in logged_messages))

    def test_http_exception_path_redaction_sanitizer(self):
        """Verify that if an HTTPException contains an internal file path, it gets redacted before sending."""
        with patch("app.main.calculate_smart_irrigation", side_effect=HTTPException(
            status_code=400,
            detail="Failed to read calibration file at C:\\Users\\prins\\AGRISMART_AI\\secret_config.yaml"
        )):
            resp = self.client.post("/api/smart-irrigation", json={
                "soil_moisture": 30, "crop": "Tomato"
            })
            self.assertEqual(resp.status_code, 400)
            
            body_text = resp.text
            # Path must be redacted and sanitized to generic safe message
            self.assertNotIn("C:\\Users\\prins", body_text)
            self.assertNotIn("secret_config.yaml", body_text)
            self.assertIn("An internal processing error occurred", body_text)

    def test_sample_image_path_traversal_prevention(self):
        """Verify directory traversal attacks on /samples/{filename} are safely rejected without path disclosure."""
        traversal_attempts = [
            "../../app/database.py",
            "..\\..\\app\\main.py",
            "....//....//Windows//win.ini",
            "/etc/passwd"
        ]
        for attempt in traversal_attempts:
            resp = self.client.get(f"/samples/{attempt}")
            self.assertIn(resp.status_code, [404, 400], f"Failed traversal block for: {attempt}")
            # Internal server paths must never be disclosed
            self.assertNotIn("C:\\Users", resp.text)
            self.assertNotIn("Traceback", resp.text)

    def test_predict_endpoint_corrupt_file_handling(self):
        """Verify uploading corrupt or malformed file to /api/predict produces clean 400/500 without stack trace."""
        fake_corrupt_bytes = b"NOT_A_REAL_IMAGE_DATA_CORRUPT"
        resp = self.client.post(
            "/api/predict",
            files={"file": ("corrupted.jpg", fake_corrupt_bytes, "image/jpeg")}
        )
        self.assertIn(resp.status_code, [400, 500])
        body_text = resp.text
        self.assertNotIn("Traceback (most recent call last)", body_text)
        self.assertNotIn("C:\\", body_text)
        self.assertNotIn(".py\", line", body_text)

    def test_tts_error_handling_sanitized(self):
        """Verify that TTS failures return clean user message rather than internal exception traces."""
        with patch("gtts.gTTS.write_to_fp", side_effect=Exception("Internal gTTS socket connection reset: 192.168.1.1")):
            resp = self.client.get("/api/tts?text=Test%20speech&lang=en")
            self.assertEqual(resp.status_code, 503)
            self.assertNotIn("Internal gTTS socket", resp.text)
            self.assertNotIn("Traceback", resp.text)
            data = resp.json()
            self.assertIn("temporarily unavailable", data.get("detail", ""))

    def test_reset_password_sanitized_errors(self):
        """Verify /api/auth/reset-password returns generic safe message on database failure."""
        with patch("sqlite3.connect", side_effect=sqlite3.DatabaseError("Disk I/O error on database.sqlite")):
            resp = self.client.post(
                "/api/auth/reset-password",
                json={"email_or_phone": "farmer@example.com", "new_password": "NewSecretPassword123!"}
            )
            self.assertEqual(resp.status_code, 500)
            self.assertNotIn("Disk I/O error", resp.text)
            self.assertNotIn("database.sqlite", resp.text)
            data = resp.json()
            self.assertIn("temporarily unavailable", data.get("detail", ""))


if __name__ == "__main__":
    unittest.main()
