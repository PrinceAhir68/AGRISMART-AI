"""
AgriSmart AI - Comprehensive Enhancements Test Suite
Verifies:
1. Disease detection constraint with target_crop & non-plant validation
2. Agronomy Assistant greetings & out-of-domain rejection guardrails
3. Soil Health Diagnostician & ICAR remediation recommendations
4. State/District lookup and persistence in crop recommendations
5. Farmer Feedback loop (/api/feedback) persistence
6. Multilingual TTS streaming
"""
import io
import json
import unittest
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient

from app.main import app
from model.predict import predict, is_valid_plant_image
from app.modules.farmer_assistant import ask_farmer_assistant
from app.modules.crop_recommender import diagnose_soil_health, INDIAN_DISTRICTS
from app.database import get_feedback_summary

client = TestClient(app)

class TestEnhancements(unittest.TestCase):
    
    # -------------------------------------------------------------
    # 1. Disease Detection Bias Elimination & Crop Constraint
    # -------------------------------------------------------------
    def test_target_crop_constraint_potato(self):
        """When Potato is selected as target_crop, prediction must be a Potato pathology, never Tomato Early Blight."""
        res = predict("model/test_samples/potato_late_blight.jpg", target_crop="Potato")
        self.assertEqual(res["crop"], "Potato")
        self.assertIn("Potato", res["class_label"])
        self.assertNotEqual(res["class_label"], "Tomato___Early_blight")

    def test_target_crop_constraint_corn(self):
        """When Corn is selected as target_crop, prediction must be a Corn pathology, never Tomato Early Blight."""
        res = predict("model/test_samples/corn_common_rust.jpg", target_crop="Corn")
        self.assertTrue(res["crop"].startswith("Corn"))
        self.assertIn("Corn", res["class_label"])
        self.assertNotEqual(res["class_label"], "Tomato___Early_blight")

    def test_target_crop_via_api(self):
        """Test /api/predict accepts target_crop in multipart form."""
        with open("model/test_samples/potato_late_blight.jpg", "rb") as img_file:
            resp = client.post(
                "/api/predict",
                files={"file": ("potato.jpg", img_file, "image/jpeg")},
                data={"target_crop": "Potato"}
            )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["crop"], "Potato")

    def test_non_plant_image_rejection(self):
        """Non-plant synthetic image must be rejected with 400 NOT_A_PLANT_IMAGE."""
        img_blue = Image.fromarray(np.full((120, 120, 3), [10, 30, 240], dtype=np.uint8))
        buf = io.BytesIO()
        img_blue.save(buf, format="JPEG")
        buf.seek(0)
        resp = client.post("/api/predict", files={"file": ("blue_screen.jpg", buf, "image/jpeg")})
        self.assertEqual(resp.status_code, 400)
        detail = resp.json().get("detail", {})
        self.assertEqual(detail.get("error"), "NOT_A_PLANT_IMAGE")

    # -------------------------------------------------------------
    # 2. Chatbot: Culturally Grounded Greetings & Strict Guardrails
    # -------------------------------------------------------------
    def test_chatbot_greetings_all_languages(self):
        """Verify conversational greetings across English, Hindi, Gujarati, Marathi."""
        # English
        ans_en = ask_farmer_assistant("Hello, good morning!", "en")
        self.assertEqual(ans_en["intent"], "greeting")
        self.assertIn("AgriSmart", ans_en["answer"])

        # Hindi (native Devanagari script)
        ans_hi = ask_farmer_assistant("नमस्ते", "hi")
        self.assertEqual(ans_hi["intent"], "greeting")
        self.assertIn("नमस्ते", ans_hi["answer"])

        # Gujarati (native script)
        ans_gu = ask_farmer_assistant("કેમ છો", "gu")
        self.assertEqual(ans_gu["intent"], "greeting")
        self.assertIn("નમસ્તે", ans_gu["answer"])

        # Marathi (native script)
        ans_mr = ask_farmer_assistant("नमस्कार", "mr")
        self.assertEqual(ans_mr["intent"], "greeting")
        self.assertIn("नमस्कार", ans_mr["answer"])

    def test_chatbot_out_of_domain_guardrail(self):
        """Verify that non-agricultural queries (movies, cricket, coding, etc.) are strictly rejected."""
        queries = [
            "Who is the best Bollywood actor?",
            "What was the cricket score yesterday?",
            "Write a Python script for a calculator",
            "What is the capital of France?"
        ]
        for q in queries:
            ans = ask_farmer_assistant(q, "en")
            self.assertEqual(ans["intent"], "guardrail_rejection")
            self.assertIn("agricultural", ans["answer"].lower())

    def test_chatbot_agronomy_queries(self):
        """Verify valid farming inquiries return ICAR grounded advice."""
        ans = ask_farmer_assistant("How to manage Early Blight in tomato?", "en")
        self.assertEqual(ans["intent"], "agronomy_answer")
        self.assertIn("Blight", ans["topic"])
        self.assertIn("ICAR", ans["grounded_source"])

    # -------------------------------------------------------------
    # 3. Soil Health Diagnostician & ICAR Remediation
    # -------------------------------------------------------------
    def test_soil_health_acidic(self):
        """Acidic soil (pH < 6.0) should trigger Agricultural Lime remedy."""
        alerts = diagnose_soil_health(ph=5.2, n=100, p=50, k=50)
        ph_alert = next(a for a in alerts if a["param"] == "pH")
        self.assertEqual(ph_alert["severity"], "HIGH")
        self.assertIn("Lime", ph_alert["remedy"])

    def test_soil_health_alkaline(self):
        """Alkaline soil (pH > 7.8) should trigger Agricultural Gypsum remedy."""
        alerts = diagnose_soil_health(ph=8.4, n=100, p=50, k=50)
        ph_alert = next(a for a in alerts if a["param"] == "pH")
        self.assertEqual(ph_alert["severity"], "HIGH")
        self.assertIn("Gypsum", ph_alert["remedy"])

    def test_soil_health_nutrient_deficiencies(self):
        """Low N, low P, low K should trigger specific fertilizer remedies."""
        alerts = diagnose_soil_health(ph=6.5, n=40, p=15, k=25)
        n_alert = next(a for a in alerts if a["param"] == "Nitrogen")
        self.assertIn("Urea", n_alert["remedy"])
        p_alert = next(a for a in alerts if a["param"] == "Phosphorus")
        self.assertIn("SSP", p_alert["remedy"])
        k_alert = next(a for a in alerts if a["param"] == "Potassium")
        self.assertIn("MOP", k_alert["remedy"])

    # -------------------------------------------------------------
    # 4. District Directory & Dual Location Persistence
    # -------------------------------------------------------------
    def test_districts_endpoint(self):
        """Verify /api/districts returns supported Indian agricultural districts."""
        resp = client.get("/api/districts")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("Gujarat", data["districts"])
        self.assertIn("Maharashtra", data["districts"])
        self.assertIn("Punjab", data["districts"])
        self.assertIn("Ahmedabad", data["districts"]["Gujarat"])

    def test_crop_recommendation_with_district_persistence(self):
        """Verify crop recommendation handles state/district and persists to SQLite."""
        payload = {
            "soil_type": "Black Cotton",
            "ph": 7.2,
            "n": 100,
            "p": 50,
            "k": 45,
            "temperature": 28.0,
            "rainfall": 600.0,
            "season": "Kharif",
            "previous_crop": "Wheat",
            "state": "Gujarat",
            "district": "Rajkot"
        }
        resp = client.post("/api/crop-recommendation", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertGreater(len(data["recommendations"]), 0)
        self.assertIn("soil_health_diagnosis", data)
        self.assertIsNotNone(data.get("record_id"))

    # -------------------------------------------------------------
    # 5. Farmer Feedback Loop (/api/feedback)
    # -------------------------------------------------------------
    def test_farmer_feedback_submission(self):
        """Verify feedback is recorded in SQLite and summary is updated."""
        payload = {
            "item_type": "diagnosis",
            "helpful": True,
            "comments": "Very accurate detection of blight."
        }
        resp = client.post("/api/feedback", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("summary", data)
        self.assertGreater(data["summary"]["total_feedback"], 0)

    # -------------------------------------------------------------
    # 6. Resilient TTS Streaming
    # -------------------------------------------------------------
    def test_tts_streaming_languages(self):
        """Verify TTS endpoint streams audio for all 4 languages."""
        for lang, phrase in [("hi", "नमस्ते किसान भाई"), ("gu", "નમસ્તે ખેડૂત મિત્ર"), ("mr", "नमस्कार शेतकरी मित्र"), ("en", "Hello farmer")]:
            resp = client.get(f"/api/tts?text={phrase}&lang={lang}")
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.headers.get("content-type"), "audio/mpeg")
            self.assertGreater(len(resp.content), 200)


if __name__ == "__main__":
    unittest.main()
