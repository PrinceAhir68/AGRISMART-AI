"""
AgriSmart AI - Automated Integration Tests for Settings, Farm Profile, and Data Export
SIH-2026 Problem Statement 1
"""

import os
import sys
import unittest
import time
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from app.main import app
from app.database import (
    register_user, update_user_profile, change_user_password, export_user_data,
    authenticate_user
)


class TestSettingsAndProfile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        # Create a dedicated test user for profile and settings tests
        cls.test_phone = f"91234{int(time.time()) % 100000:05d}"
        cls.test_password = "initialPassword123"
        res = register_user(
            name="Ramesh Patel",
            email_or_phone=cls.test_phone,
            password=cls.test_password,
            location="Ahmedabad, Gujarat",
            primary_crop="Tomato",
            language="gu"
        )
        assert res["success"] is True, f"Failed to register test user: {res}"
        cls.user_id = res["user"]["id"]

    def test_1_update_profile_api(self):
        """Tests POST /api/user/profile to update farm details and preferences."""
        payload = {
            "user_id": self.user_id,
            "name": "Rameshchandra Patel",
            "location": "Sanand, Gujarat",
            "village": "Nal Sarovar",
            "primary_crop": "Tomato, Cotton, Wheat",
            "farm_size": "12.5 Bigha",
            "soil_type": "Black Cotton",
            "water_source": "Canal",
            "language": "gu",
            "settings_json": '{"theme":"high-contrast","font_scale":"large","voice_rate":1.1}'
        }
        resp = self.client.post("/api/user/profile", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        user = data["user"]
        self.assertEqual(user["name"], "Rameshchandra Patel")
        self.assertEqual(user["location"], "Sanand, Gujarat")
        self.assertEqual(user["village"], "Nal Sarovar")
        self.assertEqual(user["primary_crop"], "Tomato, Cotton, Wheat")
        self.assertEqual(user["farm_size"], "12.5 Bigha")
        self.assertEqual(user["soil_type"], "Black Cotton")
        self.assertEqual(user["water_source"], "Canal")

    def test_2_change_password_api_success(self):
        """Tests POST /api/user/change-password with valid current password."""
        new_pwd = "newSecurePassword456"
        payload = {
            "user_id": self.user_id,
            "old_password": self.test_password,
            "new_password": new_pwd
        }
        resp = self.client.post("/api/user/change-password", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])

        # Verify authentication works with the new password
        auth_res = authenticate_user(self.test_phone, new_pwd)
        self.assertTrue(auth_res["success"])

        # Update test_password for subsequent tests
        self.__class__.test_password = new_pwd

    def test_3_change_password_api_incorrect_old(self):
        """Tests POST /api/user/change-password with wrong current password."""
        payload = {
            "user_id": self.user_id,
            "old_password": "WrongPassword999",
            "new_password": "someNewPassword123"
        }
        resp = self.client.post("/api/user/change-password", json=payload)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Current password is incorrect", resp.json()["detail"])

    def test_4_change_password_api_short_password(self):
        """Tests POST /api/user/change-password with short password."""
        payload = {
            "user_id": self.user_id,
            "old_password": self.test_password,
            "new_password": "123"
        }
        resp = self.client.post("/api/user/change-password", json=payload)
        self.assertEqual(resp.status_code, 400)

    def test_5_export_farm_data_api(self):
        """Tests GET /api/user/export-data for data backup and portability."""
        resp = self.client.get(f"/api/user/export-data?user_id={self.user_id}")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("user_profile", data)
        self.assertIn("diagnoses_history", data)
        self.assertIn("crop_recommendations", data)
        self.assertIn("feedback_history", data)
        self.assertEqual(data["user_profile"]["id"], self.user_id)

    def test_6_export_farm_data_guest_fallback(self):
        """Tests GET /api/user/export-data for guest farmers."""
        resp = self.client.get("/api/user/export-data")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("user_profile", data)
        self.assertIn("export_timestamp", data)


if __name__ == "__main__":
    unittest.main()
