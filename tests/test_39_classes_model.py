"""
AgriSmart AI - 39-Class Vision Model & 14-Crop Architecture Test Suite
SIH-2026 Problem Statement 1

Validates:
1. 39-Class catalog completeness in classes.json and model/network.py
2. Full ICAR agronomic advisory coverage across all 39 classes in disease_knowledge.json
3. Multilingual translations (Hindi, Gujarati, Marathi, English) for all 39 classes
4. MobileNetV3 neural network forward pass produces 39 output logits
5. Saved weights (agrismart_mobilenetv3.pth) and metrics (metrics.json) validity
6. Accurate prediction on representative leaves across newly supported crops
7. Rejection of Background_without_leaves with InvalidPlantImageError
8. Target crop filtering behavior
"""

import os
import sys
import json
import unittest
import torch
from PIL import Image

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from model.network import AgriSmartVisionModel, get_eval_transforms
from model.predict import predict, predict_class_label, InvalidPlantImageError, _normalize_crop_name


class Test39ClassesVisionSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.classes_path = os.path.join(PROJECT_ROOT, "model", "classes.json")
        cls.knowledge_path = os.path.join(PROJECT_ROOT, "app", "data", "disease_knowledge.json")
        cls.weights_path = os.path.join(PROJECT_ROOT, "model", "weights", "agrismart_mobilenetv3.pth")
        cls.metrics_path = os.path.join(PROJECT_ROOT, "model", "metrics.json")
        cls.samples_dir = os.path.join(PROJECT_ROOT, "model", "test_samples")

        with open(cls.classes_path, "r", encoding="utf-8") as f:
            cls.classes = json.load(f)

        with open(cls.knowledge_path, "r", encoding="utf-8") as f:
            cls.knowledge = json.load(f)

    def test_01_classes_count_is_39(self):
        """Verify that classes.json contains exactly 39 standard classes."""
        self.assertEqual(len(self.classes), 39, f"Expected 39 classes, found {len(self.classes)}")
        self.assertIn("Background_without_leaves", self.classes)
        self.assertIn("Orange___Haunglongbing_(Citrus_greening)", self.classes)
        self.assertIn("Blueberry___healthy", self.classes)
        self.assertIn("Soybean___healthy", self.classes)
        self.assertIn("Squash___Powdery_mildew", self.classes)

    def test_02_knowledge_base_covers_all_39_classes(self):
        """Verify that disease_knowledge.json covers every class in classes.json."""
        missing = [cls for cls in self.classes if cls not in self.knowledge]
        self.assertEqual(len(missing), 0, f"Classes missing from disease_knowledge.json: {missing}")

        for cls_name in self.classes:
            entry = self.knowledge[cls_name]
            self.assertIn("display_name", entry)
            self.assertIn("crop", entry)
            self.assertIn("is_disease", entry)
            self.assertIn("symptoms", entry)
            self.assertIn("precautions", entry)
            self.assertIsInstance(entry["precautions"], list)
            self.assertGreaterEqual(len(entry["precautions"]), 1)
            self.assertIn("organic_treatment", entry)
            self.assertIn("chemical_treatment", entry)
            self.assertIn("prevention", entry)
            self.assertIn("translations", entry)
            
            # Check translations
            trans = entry["translations"]
            for lang in ["hi", "gu", "mr"]:
                self.assertIn(lang, trans, f"Missing {lang} translation for {cls_name}")
                self.assertIn("title", trans[lang])
                self.assertIn("action", trans[lang])

    def test_03_mobilenetv3_produces_39_logits(self):
        """Verify that AgriSmartVisionModel forward pass outputs exactly 39 logits."""
        model = AgriSmartVisionModel(num_classes=39)
        model.eval()
        dummy_input = torch.randn(2, 3, 224, 224)
        with torch.no_grad():
            output = model(dummy_input)
        self.assertEqual(output.shape, (2, 39), f"Expected shape (2, 39), got {output.shape}")

    def test_04_weights_and_metrics_files_exist(self):
        """Verify that trained model weights and metrics.json are present."""
        self.assertTrue(os.path.exists(self.weights_path), f"Weights file missing: {self.weights_path}")
        self.assertGreater(os.path.getsize(self.weights_path), 1_000_000, "Weights file is suspiciously small")
        
        self.assertTrue(os.path.exists(self.metrics_path), f"Metrics file missing: {self.metrics_path}")
        with open(self.metrics_path, "r", encoding="utf-8") as f:
            metrics = json.load(f)
        self.assertEqual(metrics["num_classes"], 39)
        self.assertEqual(len(metrics["crops_supported"]), 14)
        self.assertGreaterEqual(metrics["total_dataset_images"], 55000)

    def test_05_predict_on_multiple_crops(self):
        """Test inference on representative sample leaves across diverse crops."""
        test_cases = [
            ("tomato_early_blight.jpg", "Tomato"),
            ("apple_apple_scab.jpg", "Apple"),
            ("orange_haunglongbing_citrus_greening.jpg", "Orange"),
            ("blueberry_healthy.jpg", "Blueberry"),
            ("corn_common_rust.jpg", "Corn"),
            ("grape_black_rot.jpg", "Grape"),
            ("strawberry_leaf_scorch.jpg", "Strawberry"),
            ("peach_bacterial_spot.jpg", "Peach"),
            ("squash_powdery_mildew.jpg", "Squash"),
        ]
        for filename, expected_crop_keyword in test_cases:
            img_path = os.path.join(self.samples_dir, filename)
            if os.path.exists(img_path):
                res = predict(img_path)
                self.assertIsInstance(res, dict)
                self.assertIn("class_label", res)
                self.assertGreater(res["confidence"], 0.0)
                self.assertLessEqual(res["confidence"], 1.0)
                self.assertIn("precautions", res)
                self.assertIn("translations", res)
                self.assertIn(expected_crop_keyword.lower(), res["crop"].lower(), f"Expected crop {expected_crop_keyword}, got {res['crop']}")

    def test_06_background_without_leaves_rejection(self):
        """Verify that non-leaf background images raise InvalidPlantImageError."""
        bg_path = os.path.join(self.samples_dir, "background_without_leaves.jpg")
        if os.path.exists(bg_path):
            with self.assertRaises(InvalidPlantImageError):
                predict(bg_path)

    def test_07_target_crop_normalization_14_crops(self):
        """Verify that all 14 crops normalize to valid prefixes."""
        self.assertEqual(_normalize_crop_name("Tomato"), "Tomato")
        self.assertEqual(_normalize_crop_name("tamatar"), "Tomato")
        self.assertEqual(_normalize_crop_name("Potato"), "Potato")
        self.assertEqual(_normalize_crop_name("Corn"), "Corn")
        self.assertEqual(_normalize_crop_name("Apple"), "Apple")
        self.assertEqual(_normalize_crop_name("Grape"), "Grape")
        self.assertIn("Pepper", _normalize_crop_name("Bell Pepper"))
        self.assertEqual(_normalize_crop_name("Blueberry"), "Blueberry")
        self.assertEqual(_normalize_crop_name("Cherry"), "Cherry")
        self.assertEqual(_normalize_crop_name("Orange"), "Orange")
        self.assertEqual(_normalize_crop_name("Peach"), "Peach")
        self.assertEqual(_normalize_crop_name("Raspberry"), "Raspberry")
        self.assertEqual(_normalize_crop_name("Soybean"), "Soybean")
        self.assertEqual(_normalize_crop_name("Squash"), "Squash")
        self.assertEqual(_normalize_crop_name("Strawberry"), "Strawberry")


if __name__ == "__main__":
    unittest.main()
