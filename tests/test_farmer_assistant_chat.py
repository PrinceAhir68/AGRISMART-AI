"""
AgriSmart AI - Automated Integration Tests for Agronomy AI Chatbot
SIH-2026 Problem Statement 1 (Bonus Module E)
"""

import os
import sys
import unittest
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from app.main import app
from app.modules.farmer_assistant import ask_farmer_assistant


class TestFarmerAssistantChat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_greetings_intent(self):
        """Verify natural greetings in English, Hindi, Gujarati, Marathi."""
        cases = [
            ("Hello", "en", "Welcome & Greetings"),
            ("नमस्ते", "hi", "Welcome & Greetings"),
            ("કેમ છો", "gu", "Welcome & Greetings"),
            ("नमस्कार", "mr", "Welcome & Greetings"),
        ]
        for query, lang, expected_topic in cases:
            res = ask_farmer_assistant(query, lang)
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["intent"], "greeting")
            self.assertTrue(len(res["answer"]) > 20)

    def test_help_and_guide_intent(self):
        """Verify help and capability guide intent."""
        cases = [
            ("help", "en"),
            ("what can you do", "en"),
            ("how does this work", "en"),
            ("मदद", "hi"),
            ("કેવી રીતે વાપરવું", "gu"),
        ]
        for query, lang in cases:
            res = ask_farmer_assistant(query, lang)
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["intent"], "help_guide")
            self.assertTrue(len(res["answer"]) > 50)

    def test_agronomy_qa_crop_questions(self):
        """Verify domain crop questions return verified ICAR answers."""
        queries = [
            ("How do I treat Early Blight on tomatoes?", "en"),
            ("टमाटर में झुलसा रोग का उपचार", "hi"),
            ("ઘઉંમાં ખાતર કેટલું નાખવું", "gu"),
            ("What is the organic treatment for corn rust?", "en"),
        ]
        for q, lang in queries:
            res = ask_farmer_assistant(q, lang)
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["intent"], "agronomy_answer")
            self.assertTrue(bool(res["answer"]))
            self.assertTrue(bool(res["topic"]))
            self.assertIn("consensus_score_pct", res)
            self.assertTrue(res["consensus_score_pct"] >= 70.0)

    def test_out_of_domain_guardrail(self):
        """Verify non-agricultural queries are cleanly rejected by guardrail."""
        queries = [
            "who won the cricket match yesterday?",
            "write a poem about space exploration",
            "what is the capital of France?",
        ]
        for q in queries:
            res = ask_farmer_assistant(q, "en")
            self.assertEqual(res["status"], "out_of_domain")
            self.assertEqual(res["intent"], "guardrail_rejection")
            self.assertIn("agricultural specialist", res["answer"])

    def test_api_assistant_endpoint(self):
        """Verify POST /api/assistant API endpoint returns JSON with expected schema."""
        payload = {
            "query": "How do I treat Early Blight on tomatoes?",
            "language": "en"
        }
        resp = self.client.post("/api/assistant", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("status", data)
        self.assertIn("topic", data)
        self.assertIn("answer", data)
        self.assertIn("grounded_source", data)
        self.assertIn("consensus_score_pct", data)
        self.assertTrue(data["status"] == "success")


if __name__ == "__main__":
    unittest.main()
