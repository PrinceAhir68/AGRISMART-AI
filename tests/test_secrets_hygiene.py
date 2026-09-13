"""
AgriSmart AI - Automated Secrets and Credential Hygiene Test Suite
SIH-2026 Problem Statement 1

Validates:
1. Frontend static files (HTML, JS) contain zero hardcoded secrets, API keys, or tokens.
2. Backend codebase uses environment variables and contains no live secrets.
3. Git hygiene rules ignore all .env variants, database files, and certificates.
4. Information leakage prevention (/api/supabase/status never leaks keys).
5. Built-in zero-dependency .env loader functionality.
"""

import os
import re
import sys
import tempfile
import unittest
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from app.main import app, load_dotenv_file
from app.supabase_client import get_supabase_status


class TestSecretsHygiene(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.secret_patterns = [
            (re.compile(r"AIzaSy[0-9A-Za-z\-_]{33}"), "Google / Gemini API Key"),
            (re.compile(r"sbp_[a-zA-Z0-9]{40}"), "Supabase Service Token"),
            (re.compile(r"sk-[a-zA-Z0-9]{32,}"), "OpenAI API Key"),
            (re.compile(r"ghp_[a-zA-Z0-9]{36}"), "GitHub Personal Access Token"),
            (re.compile(r"(?i)(?:aws_secret_access_key|aws_access_key_id)\s*[:=]\s*['\"][A-Za-z0-9/+=]{20,}['\"]"), "AWS Credential"),
            (re.compile(r"(?i)(?:private_key|secret_key)\s*[:=]\s*['\"][A-Za-z0-9/+=]{30,}['\"]"), "Generic Private Key"),
        ]

    def test_frontend_has_no_hardcoded_secrets(self):
        """Guarantee that no API keys, tokens, or passwords are baked into frontend JavaScript or HTML."""
        frontend_files = [
            os.path.join(PROJECT_ROOT, "app", "static", "js", "app.js"),
            os.path.join(PROJECT_ROOT, "app", "static", "index.html"),
            os.path.join(PROJECT_ROOT, "app", "static", "css", "style.css")
        ]
        
        leaks = []
        for fpath in frontend_files:
            if not os.path.isfile(fpath):
                continue
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                for line_no, line in enumerate(f, 1):
                    for pat, desc in self.secret_patterns:
                        m = pat.search(line)
                        if m:
                            leaks.append(f"{os.path.basename(fpath)}:{line_no} [{desc}]: {m.group(0)[:25]}")

        self.assertEqual(len(leaks), 0, f"Found potential secrets exposed in frontend: {leaks}")

    def test_backend_has_no_hardcoded_api_keys(self):
        """Scan app/ and model/ Python files for known API key signatures."""
        leaks = []
        scan_dirs = [
            os.path.join(PROJECT_ROOT, "app"),
            os.path.join(PROJECT_ROOT, "model")
        ]

        for s_dir in scan_dirs:
            for root, dirs, files in os.walk(s_dir):
                if "__pycache__" in root:
                    continue
                for fname in files:
                    if fname.endswith(".py"):
                        fpath = os.path.join(root, fname)
                        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                            for line_no, line in enumerate(f, 1):
                                for pat, desc in self.secret_patterns:
                                    m = pat.search(line)
                                    if m:
                                        rel = os.path.relpath(fpath, PROJECT_ROOT)
                                        leaks.append(f"{rel}:{line_no} [{desc}]: {m.group(0)[:25]}")

        self.assertEqual(len(leaks), 0, f"Found potential secrets in backend code: {leaks}")

    def test_gitignore_protects_env_and_databases(self):
        """Verify that .gitignore properly excludes .env files, databases, and keys."""
        gitignore_path = os.path.join(PROJECT_ROOT, ".gitignore")
        self.assertTrue(os.path.isfile(gitignore_path), ".gitignore must exist")
        
        with open(gitignore_path, "r", encoding="utf-8") as f:
            content = f.read()

        required_rules = [".env", "*.db", "*.sqlite", "*.key", "*.pem"]
        for rule in required_rules:
            self.assertIn(rule, content, f"Expected rule '{rule}' missing from .gitignore")

    def test_supabase_status_endpoint_never_leaks_key(self):
        """Verify that /api/supabase/status never exposes SUPABASE_KEY in responses."""
        mock_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.sensitive_token_payload_xyz"
        old_url = os.environ.get("SUPABASE_URL")
        old_key = os.environ.get("SUPABASE_KEY")
        try:
            os.environ["SUPABASE_URL"] = "https://demofarm.supabase.co"
            os.environ["SUPABASE_KEY"] = mock_key
            
            resp = self.client.get("/api/supabase/status")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            
            # Key must never be in payload
            self.assertNotIn("key", data)
            self.assertNotIn("supabase_key", data)
            self.assertNotIn("apikey", data)
            resp_str = resp.text
            self.assertNotIn(mock_key, resp_str, "SUPABASE_KEY was leaked in HTTP response body!")
        finally:
            if old_url is not None:
                os.environ["SUPABASE_URL"] = old_url
            else:
                os.environ.pop("SUPABASE_URL", None)
            if old_key is not None:
                os.environ["SUPABASE_KEY"] = old_key
            else:
                os.environ.pop("SUPABASE_KEY", None)

    def test_load_dotenv_file_functionality(self):
        """Verify the built-in zero-dependency .env loader parses variables correctly."""
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".env") as tmp:
            tmp.write("# Comment line\n")
            tmp.write("TEST_SECRET_VAR=my_super_secret_value\n")
            tmp.write('TEST_QUOTED_VAR="quoted_secret"\n')
            tmp.write("\n")
            tmp.flush()
            tmp_path = tmp.name

        try:
            os.environ.pop("TEST_SECRET_VAR", None)
            os.environ.pop("TEST_QUOTED_VAR", None)

            loaded = load_dotenv_file(tmp_path)
            self.assertTrue(loaded)
            self.assertEqual(os.environ.get("TEST_SECRET_VAR"), "my_super_secret_value")
            self.assertEqual(os.environ.get("TEST_QUOTED_VAR"), "quoted_secret")
        finally:
            os.environ.pop("TEST_SECRET_VAR", None)
            os.environ.pop("TEST_QUOTED_VAR", None)
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()
