"""
Automated Integration Tests for AgriSmart AI FastAPI Endpoints
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

    def test_predict_endpoint(self):
        with open(self.sample_img_path, "rb") as f:
            resp = self.client.post("/api/predict", files={"file": ("leaf.jpg", f, "image/jpeg")})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("class_label", data)
        self.assertIn("confidence", data)
        self.assertIn("precautions", data)

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

    def test_weather_endpoint(self):
        resp = self.client.get("/api/weather")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("disease_risk_index", resp.json())

    def test_sustainability_endpoint(self):
        payload = {"irrigation_method": "Drip Irrigation", "solar_powered_pump": True}
        resp = self.client.post("/api/sustainability", json=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("sustainability_score", resp.json())

    def test_assistant_endpoint(self):
        payload = {"query": "How to treat late blight?", "language": "hi"}
        resp = self.client.post("/api/assistant", json=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("answer", resp.json())

    def test_iot_endpoints(self):
        resp = self.client.get("/api/iot/telemetry")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("telemetry", resp.json())

        scen_resp = self.client.post("/api/iot/scenario", json={"scenario": "rain"})
        self.assertEqual(scen_resp.status_code, 200)

    def test_agent_endpoint(self):
        payload = {"crop": "Tomato", "stage": "Mid-Season / Flowering", "diagnosis": "Tomato___Early_blight"}
        resp = self.client.post("/api/agent/cycle", json=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("cycle_id", resp.json())
        self.assertIn("farmer_alert_message", resp.json())

    def test_report_endpoint(self):
        resp = self.client.get("/api/model/report")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("primary_metric", resp.json())


if __name__ == "__main__":
    unittest.main()
