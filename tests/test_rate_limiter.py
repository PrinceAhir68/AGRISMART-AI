"""
AgriSmart AI - Automated Unit & Integration Tests for Tiered Rate Limiting
SIH-2026 Problem Statement 1

Validates:
1. Stricter authentication rate limits (login, signup, change password, reset password)
2. Per-IP and per-account limits with exponential backoff progression rather than hard lockout
3. Successful login clearing consecutive failure penalties
4. Moderate rate limits on public unauthenticated endpoints
5. Looser rate limits on authenticated user actions
6. Dynamic runtime configurability of all thresholds without hardcoded values
"""

import os
import sys
import time
import unittest
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from app.main import app
from app.modules.rate_limiter import get_rate_limiter, RateLimitConfig


class TestTieredRateLimiter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.limiter = get_rate_limiter()

    def setUp(self):
        # Reset limiter before each test to guarantee fresh state
        self.limiter.reset_all()
        # Ensure default test config
        self.limiter.update_config({
            "enabled": True,
            "auth_ip_max": 10,
            "auth_ip_window": 60,
            "auth_account_threshold": 3,
            "auth_backoff_base": 2.0,
            "auth_backoff_factor": 2.0,
            "auth_backoff_max": 300.0,
            "public_ip_max": 30,
            "public_ip_window": 60,
            "authed_user_max": 120,
            "authed_user_window": 60
        })

    def tearDown(self):
        self.limiter.reset_all()
        # Restore default config
        self.limiter.config = RateLimitConfig.from_env()

    def test_auth_exponential_backoff_progression(self):
        """Verify that repeated failed login attempts escalate with exponential backoff delay."""
        account = "test_backoff_farmer@example.com"
        headers = {"X-Forwarded-For": "192.168.10.1"}

        # Attempts 1 to 3 should fail with 401 (not rate limited yet)
        for i in range(1, 4):
            resp = self.client.post(
                "/api/auth/login",
                json={"email_or_phone": account, "password": "wrong_password"},
                headers=headers
            )
            self.assertEqual(resp.status_code, 401, f"Attempt {i} should be 401")

        # Attempt 4: Exceeds threshold (3), should trigger exponential backoff (2^0 * 2 = 2s)
        resp4 = self.client.post(
            "/api/auth/login",
            json={"email_or_phone": account, "password": "wrong_password"},
            headers=headers
        )
        self.assertEqual(resp4.status_code, 429)
        self.assertIn("Retry-After", resp4.headers)
        retry_after4 = int(resp4.headers["Retry-After"])
        self.assertTrue(1 <= retry_after4 <= 3, f"Expected ~2s backoff, got {retry_after4}")
        self.assertIn("Exponential backoff", resp4.json()["detail"])

        # Advance account backoff manually to simulate next failure
        self.limiter.account_backoff._blocked_until[account.lower()] = time.time() - 1  # unblock
        self.limiter.record_auth_result(account, "192.168.10.1", success=False)  # 5th failure

        # Attempt 5: Exponential backoff increases to 2^1 * 2 = 4s
        resp5 = self.client.post(
            "/api/auth/login",
            json={"email_or_phone": account, "password": "wrong_password"},
            headers=headers
        )
        self.assertEqual(resp5.status_code, 429)
        retry_after5 = int(resp5.headers["Retry-After"])
        self.assertTrue(3 <= retry_after5 <= 5, f"Expected ~4s backoff, got {retry_after5}")

    def test_successful_auth_resets_backoff(self):
        """Verify that a successful login resets the failure counter and clears any backoff."""
        account = f"farmer_reset_{int(time.time())}@example.com"
        password = "valid_password_123"
        headers = {"X-Forwarded-For": "192.168.10.2"}

        # Register the user
        reg_resp = self.client.post(
            "/api/auth/register",
            json={"name": "Test Farmer", "email_or_phone": account, "password": password},
            headers=headers
        )
        self.assertEqual(reg_resp.status_code, 200)

        # 2 failed attempts
        for _ in range(2):
            self.client.post(
                "/api/auth/login",
                json={"email_or_phone": account, "password": "wrong"},
                headers=headers
            )
        self.assertEqual(self.limiter.account_backoff._failures.get(account.lower()), 2)

        # Successful login
        login_resp = self.client.post(
            "/api/auth/login",
            json={"email_or_phone": account, "password": password},
            headers=headers
        )
        self.assertEqual(login_resp.status_code, 200)

        # Failure count must be reset to 0
        self.assertNotIn(account.lower(), self.limiter.account_backoff._failures)
        self.assertNotIn(account.lower(), self.limiter.account_backoff._blocked_until)

    def test_auth_per_ip_sliding_window_limit(self):
        """Verify that high-volume attempts from a single IP are capped by IP sliding window."""
        self.limiter.update_config({"auth_ip_max": 4, "auth_ip_window": 60})
        ip = "192.168.10.99"
        headers = {"X-Forwarded-For": ip}

        # Send 4 requests from this IP with different accounts
        for i in range(4):
            resp = self.client.post(
                "/api/auth/login",
                json={"email_or_phone": f"account_{i}@example.com", "password": "wrong"},
                headers=headers
            )
            self.assertEqual(resp.status_code, 401)

        # 5th request from same IP should be blocked by IP sliding window
        resp5 = self.client.post(
            "/api/auth/login",
            json={"email_or_phone": "account_other@example.com", "password": "wrong"},
            headers=headers
        )
        self.assertEqual(resp5.status_code, 429)
        self.assertIn("Authentication rate limit exceeded for IP", resp5.json()["detail"])
        self.assertEqual(resp5.headers.get("X-RateLimit-Limit"), "4")

    def test_public_endpoint_moderate_rate_limiting(self):
        """Verify that public endpoints enforce moderate rate limits per IP."""
        self.limiter.update_config({"public_ip_max": 5, "public_ip_window": 60})
        headers = {"X-Forwarded-For": "10.0.0.50"}

        # 5 requests allowed
        for i in range(5):
            resp = self.client.get("/api/districts", headers=headers)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.headers.get("X-RateLimit-Limit"), "5")

        # 6th request blocked with 429
        resp6 = self.client.get("/api/districts", headers=headers)
        self.assertEqual(resp6.status_code, 429)
        self.assertIn("Public API rate limit exceeded", resp6.json()["detail"])
        self.assertIn("Retry-After", resp6.headers)

    def test_authenticated_user_looser_rate_limiting(self):
        """Verify that authenticated user actions have a looser rate limit threshold."""
        self.limiter.update_config({
            "public_ip_max": 2,
            "authed_user_max": 8,
            "authed_user_window": 60
        })
        ip = "10.0.0.88"

        # As an unauthenticated public IP, 2 requests max
        for _ in range(2):
            resp = self.client.get("/api/districts", headers={"X-Forwarded-For": ip})
            self.assertEqual(resp.status_code, 200)
        resp3 = self.client.get("/api/districts", headers={"X-Forwarded-For": ip})
        self.assertEqual(resp3.status_code, 429)

        # But with an authenticated user context (user_id=101), limit is looser (8 requests)
        user_headers = {"X-Forwarded-For": ip, "X-User-Id": "101"}
        for i in range(6):
            resp = self.client.get("/api/history?user_id=101", headers=user_headers)
            self.assertEqual(resp.status_code, 200, f"Authed request {i+1} should succeed")
            self.assertEqual(resp.headers.get("X-RateLimit-Limit"), "8")

    def test_configurable_thresholds_at_runtime(self):
        """Verify that all rate limit thresholds can be queried and modified dynamically via API."""
        # 1. Query current config
        get_resp = self.client.get("/api/system/rate-limit-config")
        self.assertEqual(get_resp.status_code, 200)
        data = get_resp.json()
        self.assertTrue(data["status"] == "success")
        self.assertIn("auth_ip_max", data["config"])
        self.assertIn("auth_backoff_factor", data["config"])

        # 2. Update config via API
        update_payload = {
            "auth_ip_max": 25,
            "auth_backoff_base": 3.5,
            "public_ip_max": 50,
            "authed_user_max": 200
        }
        post_resp = self.client.post("/api/system/rate-limit-config", json=update_payload)
        self.assertEqual(post_resp.status_code, 200)
        updated = post_resp.json()["config"]
        self.assertEqual(updated["auth_ip_max"], 25)
        self.assertEqual(updated["auth_backoff_base"], 3.5)
        self.assertEqual(updated["public_ip_max"], 50)
        self.assertEqual(updated["authed_user_max"], 200)

        # Confirm internal singleton updated
        self.assertEqual(self.limiter.config.auth_ip_max, 25)
        self.assertEqual(self.limiter.config.auth_backoff_base, 3.5)

    def test_password_reset_rate_limiting(self):
        """Verify that password reset endpoint enforces strict auth rate limits."""
        headers = {"X-Forwarded-For": "192.168.10.44"}
        account = "farmer_reset_test@example.com"
        
        # 3 failed reset attempts (account not found)
        for _ in range(3):
            resp = self.client.post(
                "/api/auth/reset-password",
                json={"email_or_phone": account, "new_password": "newpassword123"},
                headers=headers
            )
            self.assertEqual(resp.status_code, 404)

        # 4th attempt blocked with 429
        resp4 = self.client.post(
            "/api/auth/reset-password",
            json={"email_or_phone": account, "new_password": "newpassword123"},
            headers=headers
        )
        self.assertEqual(resp4.status_code, 429)
        self.assertIn("Retry-After", resp4.headers)

    def test_disabled_rate_limiting_bypasses_all(self):
        """Verify that setting enabled=False bypasses all rate limits immediately."""
        self.limiter.update_config({"enabled": False, "public_ip_max": 2})
        headers = {"X-Forwarded-For": "10.0.0.99"}

        # Even with public_ip_max=2, 10 requests succeed without 429
        for _ in range(10):
            resp = self.client.get("/api/districts", headers=headers)
            self.assertEqual(resp.status_code, 200)

    def test_different_accounts_isolation(self):
        """Verify that backoff on account A does not affect legitimate user on account B."""
        headers_a = {"X-Forwarded-For": "192.168.10.101"}
        headers_b = {"X-Forwarded-For": "192.168.10.102"}
        account_a = "victim_account@example.com"
        account_b = "innocent_account@example.com"

        # Account A receives 3 failures -> triggers backoff
        for _ in range(3):
            self.client.post("/api/auth/login", json={"email_or_phone": account_a, "password": "wrong"}, headers=headers_a)
        
        # Account A is now rate-limited
        resp_a = self.client.post("/api/auth/login", json={"email_or_phone": account_a, "password": "wrong"}, headers=headers_a)
        self.assertEqual(resp_a.status_code, 429)

        # Account B from another IP is NOT rate-limited
        resp_b = self.client.post("/api/auth/login", json={"email_or_phone": account_b, "password": "wrong"}, headers=headers_b)
        self.assertEqual(resp_b.status_code, 401)


if __name__ == "__main__":
    unittest.main()
