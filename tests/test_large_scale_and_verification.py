"""
AgriSmart AI - Automated Test Suite for 100,000+ Image Vision Pipeline,
10,000+ Q&A Knowledge Engine, and Live Internet Verification & Comparison Engine.
"""

import os
import sys
import unittest
import torch
from PIL import Image

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi.testclient import TestClient
from app.main import app
from app.modules.qa_engine import get_qa_engine
from app.modules.web_verifier import verify_disease_with_web, verify_and_answer_qa_with_web
from app.modules.farmer_assistant import ask_farmer_assistant
from model.predict import predict
from model.train_large_scale import AugmentedAgriculturalDataset, get_large_scale_augmentations, build_model


class TestLargeScaleAndVerification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.qa_engine = get_qa_engine()

    def test_qa_engine_exceeds_10000_nodes(self):
        """Verify knowledge base has over 10,000 indexed Q&A nodes."""
        self.assertGreaterEqual(
            self.qa_engine.total_nodes,
            10000,
            f"Knowledge engine has {self.qa_engine.total_nodes} nodes, expected >= 10,000."
        )

    def test_qa_engine_search_multi_crop(self):
        """Verify search retrieves accurate solutions across varied crops."""
        queries = [
            "cotton pink bollworm control",
            "wheat yellow rust treatment",
            "rice blast fungicide",
            "potato late blight mancozeb",
            "tomato bacterial spot treatment"
        ]
        for q in queries:
            results = self.qa_engine.search(q, top_k=3)
            self.assertTrue(len(results) > 0, f"Expected results for query: {q}")
            self.assertIn("answer_en", results[0])
            self.assertIn("topic", results[0])

    def test_web_verifier_disease_consensus(self):
        """Verify pathogen matrix and live internet comparison corroborates disease."""
        res = verify_disease_with_web(
            crop="Tomato",
            disease_display_name="Tomato Early Blight",
            class_label="Tomato___Early_blight"
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["consensus_status"], "VERIFIED_CONSENSUAL")
        self.assertGreaterEqual(res["agreement_score_pct"], 90.0)
        self.assertTrue(len(res["online_sources"]) >= 2)
        self.assertTrue(len(res["symptom_match_indicators"]) >= 2)
        self.assertEqual(res["scientific_taxa"], "Alternaria solani")

    def test_web_verifier_healthy_foliage(self):
        """Verify healthy foliage check passes with high consensus."""
        res = verify_disease_with_web(
            crop="Apple",
            disease_display_name="Apple Healthy",
            class_label="Apple___healthy"
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["consensus_status"], "CORROBORATED_HEALTHY")
        self.assertGreaterEqual(res["agreement_score_pct"], 95.0)

    def test_farmer_assistant_dual_verification(self):
        """Verify chatbot produces dual-verified response with online consensus."""
        res = ask_farmer_assistant("What is the treatment for Late Blight on potato?", language="en")
        self.assertEqual(res["intent"], "agronomy_answer")
        self.assertEqual(res["consensus_status"], "DUAL_VERIFIED_AGREEMENT")
        self.assertGreaterEqual(res["consensus_score_pct"], 90.0)
        self.assertTrue(res["verified_with_live_internet"])
        self.assertTrue(len(res["live_internet_citations"]) >= 1)
        self.assertIn("Potato", res["answer"])
        self.assertIn("Late Blight", res["topic"])

    def test_predict_disease_includes_web_consensus(self):
        """Verify core predict function attaches full web consensus data."""
        sample_path = os.path.join(PROJECT_ROOT, "model", "test_samples", "potato_early_blight.jpg")
        if os.path.exists(sample_path):
            result = predict(sample_path)
            self.assertIn("web_consensus", result)
            wc = result["web_consensus"]
            self.assertIsNotNone(wc)
            self.assertIn("consensus_status", wc)
            self.assertIn("agreement_score_pct", wc)

    def test_api_qa_search_endpoint(self):
        """Verify /api/qa/search returns matching nodes from the 10k+ corpus."""
        resp = self.client.get("/api/qa/search?q=blight&lang=en")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertGreater(data["total_matches"], 0)

    def test_large_scale_training_dataset_virtual_samples(self):
        """Verify large-scale dataset accurately configures 100,000+ virtual samples."""
        train_tf, _ = get_large_scale_augmentations()
        test_samples_dir = os.path.join(PROJECT_ROOT, "model", "test_samples")
        sample_files = [
            os.path.join(test_samples_dir, f) for f in os.listdir(test_samples_dir)
            if f.endswith((".jpg", ".png", ".jpeg"))
        ] if os.path.exists(test_samples_dir) else []

        dataset = AugmentedAgriculturalDataset(
            sample_paths=sample_files,
            target_samples=100000,
            transform=train_tf
        )
        self.assertEqual(len(dataset), 100000, "Dataset target length must be 100,000.")

        # Test index retrieval and tensor generation
        img_tensor, label = dataset[75420]
        self.assertIsInstance(img_tensor, torch.Tensor)
        self.assertEqual(img_tensor.shape, (3, 224, 224))
        self.assertIsInstance(label, int)


if __name__ == "__main__":
    unittest.main()
