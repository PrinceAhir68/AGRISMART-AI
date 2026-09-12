"""
Automated Unit Tests for AgriSmart AI Core Prediction Interface
Compliant with SIH-2026 Problem Statement 1 Section 3.1 & 4.1.
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from model.predict import predict, predict_class_label

class TestCorePredict(unittest.TestCase):
    def setUp(self):
        self.sample_img = os.path.join(PROJECT_ROOT, "model", "test_samples", "tomato_early_blight.jpg")
        self.assertTrue(os.path.exists(self.sample_img), f"Sample image {self.sample_img} does not exist.")

    def test_predict_function_structure(self):
        """Test that predict(path) returns required fields."""
        res = predict(self.sample_img)
        self.assertIsInstance(res, dict)
        self.assertIn("class_label", res)
        self.assertIn("confidence", res)
        self.assertIn("precautions", res)
        self.assertIn("is_disease", res)
        self.assertGreaterEqual(res["confidence"], 0.70)
        self.assertIsInstance(res["precautions"], list)

    def test_predict_class_label_contract(self):
        """Test Section 4.1 contract: predict(image_path) -> class_label."""
        label = predict_class_label(self.sample_img)
        self.assertIsInstance(label, str)
        self.assertIn("Tomato", label)

    def test_missing_image_raises_error(self):
        """Test that invalid file paths cleanly raise FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            predict("non_existent_leaf_photo.jpg")

if __name__ == "__main__":
    unittest.main()
