"""
Automated Integration Tests for AgriSmart AI FastAPI Endpoints (Updated)
SIH-2026 Problem Statement 1
"""

import os
import sys
import unittest
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from app.main import app

class TestApiEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.sample_img_path = os.path.join(PROJECT_ROOT, "model", "test_samples", "tomato_early_blight.jpg")

    def test_root_index(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)

    def test_auth_registration_and_login(self):
        # Unique test phone number
        test_phone = f"998877{os.getpid() % 10000:04d}"
        reg_payload = {
            "name": "Test Farmer",
            "email_or_phone": test_phone,
            "password": "securepassword123",
            "location": "Ahmedabad, Gujarat",
            "primary_crop": "Tomato",
            "language": "gu"
        }
        reg_resp = self.client.post("/api/auth/register", json=reg_payload)
        self.assertEqual(reg_resp.status_code, 200)
        self.assertTrue(reg_resp.json()["success"])

        # Login test
        login_payload = {
            "email_or_phone": test_phone,
            "password": "securepassword123"
        }
        login_resp = self.client.post("/api/auth/login", json=login_payload)
        self.assertEqual(login_resp.status_code, 200)
        self.assertTrue(login_resp.json()["success"])

    def test_supabase_status(self):
        resp = self.client.get("/api/supabase/status")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("status", resp.json())

    def test_predict_endpoint(self):
        with open(self.sample_img_path, "rb") as f:
            resp = self.client.post("/api/predict", files={"file": ("leaf.jpg", f, "image/jpeg")})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("class_label", data)
        self.assertIn("confidence", data)
        self.assertIn("record_id", data)

    def test_history_endpoint(self):
        resp = self.client.get("/api/history")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("history", resp.json())

    def test_crop_rec_endpoint(self):
        payload = {"soil_type": "Loamy", "ph": 6.5, "n": 90, "p": 50, "k": 40, "season": "Kharif"}
        resp = self.client.post("/api/crop-recommendation", json=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()["recommendations"]), 3)

    def test_irrigation_endpoint(self):
        payload = {"current_soil_moisture": 18.0, "crop_type": "Tomato", "forecast_rain_mm": 0.0}
        resp = self.client.post("/api/smart-irrigation", json=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("decision", resp.json())

    def test_weather_endpoint_with_gps(self):
        resp = self.client.get("/api/weather?lat=23.0225&lon=72.5714&name=Ahmedabad")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("disease_risk_index", resp.json())

    def test_sustainability_endpoint(self):
        payload = {"irrigation_method": "Drip Irrigation", "solar_powered_pump": True}
        resp = self.client.post("/api/sustainability", json=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("sustainability_score", resp.json())

    def test_assistant_endpoint(self):
        payload = {"query": "How to manage rust?", "language": "hi"}
        resp = self.client.post("/api/assistant", json=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("answer", resp.json())

    def test_iot_endpoints(self):
        resp = self.client.get("/api/iot/telemetry")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("telemetry", resp.json())

    def test_health_and_security_headers(self):
        for path in ("/health", "/api/health"):
            resp = self.client.get(path)
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertEqual(data["status"], "healthy")
            self.assertEqual(data["database"], "ok")
            self.assertEqual(data["classes_count"], 39)
            self.assertEqual(data["model_status"], "ready")
            self.assertTrue(data["model_loaded"])
            self.assertIn("dependencies", data)
            self.assertEqual(data["dependencies"]["vision_model"], "ready")
            self.assertTrue(data["storage_isolated"])
            # Security headers
            self.assertEqual(resp.headers.get("x-content-type-options"), "nosniff")
            self.assertEqual(resp.headers.get("x-frame-options"), "SAMEORIGIN")
            self.assertEqual(resp.headers.get("referrer-policy"), "strict-origin-when-cross-origin")

    def test_blueprint_api_aliases_and_research(self):
        # 1. Test /api/diagnosis
        with open(self.sample_img_path, "rb") as f:
            resp = self.client.post("/api/diagnosis", files={"file": ("leaf.jpg", f, "image/jpeg")})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("class_label", resp.json())
        self.assertIn("confidence", resp.json())

        # 2. Test /api/diagnosis/feedback
        fb_resp = self.client.post("/api/diagnosis/feedback", json={"item_type": "diagnosis", "item_id": "1", "helpful": True})
        self.assertEqual(fb_resp.status_code, 200)
        self.assertEqual(fb_resp.json()["status"], "success")

        # 3. Test /api/irrigation
        irrig_resp = self.client.post("/api/irrigation", json={"current_soil_moisture": 18.0, "crop_type": "Tomato"})
        self.assertEqual(irrig_resp.status_code, 200)
        self.assertIn("decision", irrig_resp.json())

        # 4. Test /api/research/metrics
        res_resp = self.client.get("/api/research/metrics")
        self.assertEqual(res_resp.status_code, 200)
        m_data = res_resp.json()
        self.assertEqual(m_data["model_version"], "MobileNetV3-Small-v2")
        self.assertEqual(m_data["held_out_test_metrics"]["top1_accuracy_pct"], 95.05)
        self.assertEqual(m_data["held_out_test_metrics"]["top3_accuracy_pct"], 99.38)


if __name__ == "__main__":
    unittest.main()
