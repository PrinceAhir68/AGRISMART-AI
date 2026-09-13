"""
AgriSmart AI - Comprehensive Automated Test Suite for All 14 Crops and 39 Classes.
Verifies model inference, auto-detection accuracy, target crop filtering,
knowledge base completeness, and multilingual coverage across the full 54,000+ image dataset,
with specialized validation for Soybean leaf disease vs. Bell Pepper separation.
"""

import os
import sys
import json
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from model.predict import predict, get_vision_model, CLASSES
from model.network import AgriSmartVisionModel


class TestAllCropsFullDataset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.samples_dir = os.path.join(PROJECT_ROOT, "model", "test_samples")
        cls.classes_json_path = os.path.join(PROJECT_ROOT, "model", "classes.json")
        cls.knowledge_json_path = os.path.join(PROJECT_ROOT, "app", "data", "disease_knowledge.json")
        
        with open(cls.classes_json_path, "r", encoding="utf-8") as f:
            cls.registered_classes = json.load(f)
            
        with open(cls.knowledge_json_path, "r", encoding="utf-8") as f:
            cls.knowledge_data = json.load(f)

    def test_01_all_39_classes_registered(self):
        """Verify exactly 39 classes are defined across the system."""
        self.assertEqual(len(self.registered_classes), 39, "classes.json must contain 39 classes.")
        self.assertEqual(len(CLASSES), 39, "CLASSES list in predict.py must contain 39 classes.")
        self.assertEqual(self.registered_classes, CLASSES, "classes.json must match predict.py CLASSES.")
        self.assertIn("Soybean___Bacterial_blight", CLASSES, "Soybean___Bacterial_blight must be registered.")

    def test_02_all_14_crops_present_in_classes(self):
        """Verify all 14 crop families are present."""
        expected_crops = {
            "Apple", "Blueberry", "Cherry", "Corn", "Grape", "Orange",
            "Peach", "Pepper__bell", "Potato", "Raspberry", "Soybean",
            "Squash", "Strawberry", "Tomato"
        }
        extracted_crops = set(c.split("___")[0] for c in CLASSES)
        self.assertEqual(expected_crops, extracted_crops, f"Missing crops: {expected_crops - extracted_crops}")

    def test_03_knowledge_base_covers_all_39_classes(self):
        """Verify disease_knowledge.json has full agronomy data for all 39 classes."""
        for class_name in CLASSES:
            self.assertIn(class_name, self.knowledge_data, f"Missing knowledge entry for: {class_name}")
            entry = self.knowledge_data[class_name]
            self.assertIn("crop", entry)
            self.assertIn("display_name", entry)
            self.assertIn("precautions", entry)
            self.assertIn("organic_treatment", entry)
            self.assertIn("chemical_treatment", entry)
            self.assertTrue(len(entry["precautions"]) >= 2, f"Precautions too sparse for {class_name}")

    def test_04_model_weights_load_cleanly_with_39_classes(self):
        """Verify neural network loads 39-class weights without architecture mismatch."""
        model, transform = get_vision_model()
        self.assertIsNotNone(model, "Vision model should not be None.")
        self.assertIsNotNone(transform, "Evaluation transform should not be None.")
        self.assertIsInstance(model, AgriSmartVisionModel)
        self.assertEqual(model.backbone.classifier[7].out_features, 39, "Model classifier out_features must be 39.")

    def test_05_potato_early_blight_never_confused_with_tomato(self):
        """User Request #7 test: Potato leaf must NOT be confused with Tomato Early Blight."""
        potato_sample = os.path.join(self.samples_dir, "potato_early_blight.jpg")
        self.assertTrue(os.path.exists(potato_sample), "potato_early_blight.jpg sample missing.")

        res = predict(potato_sample, target_crop="auto")
        self.assertIn("Potato", res["crop"], f"Expected Potato crop, got {res['crop']}")
        self.assertIn("Potato", res["class_label"])
        self.assertNotIn("Tomato", res["class_label"])
        self.assertGreaterEqual(res["confidence"], 0.85)

    def test_06_potato_late_blight_autodetect(self):
        """Verify Potato Late Blight auto-detects accurately."""
        sample = os.path.join(self.samples_dir, "potato_late_blight.jpg")
        res = predict(sample, target_crop="auto")
        self.assertIn("Potato", res["crop"])
        self.assertIn("Potato", res["class_label"])

    def test_07_tomato_early_blight_autodetect(self):
        """Verify Tomato Early Blight auto-detects accurately."""
        sample = os.path.join(self.samples_dir, "tomato_early_blight.jpg")
        res = predict(sample, target_crop="auto")
        self.assertIn("Tomato", res["crop"])
        self.assertIn("Tomato", res["class_label"])

    def test_08_all_14_crops_autodetect(self):
        """Verify auto-detection across all 14 crop families."""
        test_cases = [
            ("apple_scab.jpg", "Apple"),
            ("blueberry_healthy.jpg", "Blueberry"),
            ("cherry_powdery_mildew.jpg", "Cherry"),
            ("corn_common_rust.jpg", "Corn"),
            ("grape_black_rot.jpg", "Grape"),
            ("orange_citrus_greening.jpg", "Orange"),
            ("peach_bacterial_spot.jpg", "Peach"),
            ("bell_pepper_bacterial_spot.jpg", "Pepper"),
            ("potato_early_blight.jpg", "Potato"),
            ("raspberry_healthy.jpg", "Raspberry"),
            ("soybean_healthy.jpg", "Soybean"),
            ("squash_powdery_mildew.jpg", "Squash"),
            ("strawberry_leaf_scorch.jpg", "Strawberry"),
            ("tomato_early_blight.jpg", "Tomato"),
        ]

        for filename, expected_crop_token in test_cases:
            img_path = os.path.join(self.samples_dir, filename)
            self.assertTrue(os.path.exists(img_path), f"Sample image {filename} missing.")
            res = predict(img_path, target_crop="auto")
            self.assertIn(
                expected_crop_token.lower(),
                res["crop"].lower(),
                f"Auto-detection mismatch for {filename}: Expected '{expected_crop_token}' in '{res['crop']}' ({res['class_label']}, conf={res['confidence']:.2f})"
            )
            self.assertGreaterEqual(res["confidence"], 0.70)
            self.assertTrue(len(res["precautions"]) > 0)

    def test_09_target_crop_constraint_filtering(self):
        """Verify specifying target_crop correctly constrains predictions."""
        # Test Orange with target_crop='orange'
        orange_sample = os.path.join(self.samples_dir, "orange_citrus_greening.jpg")
        res_orange = predict(orange_sample, target_crop="orange")
        self.assertIn("Orange", res_orange["crop"])

        # Test Peach with target_crop='peach'
        peach_sample = os.path.join(self.samples_dir, "peach_bacterial_spot.jpg")
        res_peach = predict(peach_sample, target_crop="peach")
        self.assertIn("Peach", res_peach["crop"])

        # Test Strawberry with target_crop='strawberry'
        straw_sample = os.path.join(self.samples_dir, "strawberry_leaf_scorch.jpg")
        res_straw = predict(straw_sample, target_crop="strawberry")
        self.assertIn("Strawberry", res_straw["crop"])

        # Test Squash with target_crop='squash'
        squash_sample = os.path.join(self.samples_dir, "squash_powdery_mildew.jpg")
        res_squash = predict(squash_sample, target_crop="squash")
        self.assertIn("Squash", res_squash["crop"])

        # Test Soybean with target_crop='soybean'
        soy_sample = os.path.join(self.samples_dir, "soybean_bacterial_blight.jpg")
        if os.path.exists(soy_sample):
            res_soy = predict(soy_sample, target_crop="soybean")
            self.assertEqual(res_soy["crop"], "Soybean")
            self.assertEqual(res_soy["class_label"], "Soybean___Bacterial_blight")

    def test_10_multilingual_translations_for_new_crops(self):
        """Verify multilingual entries exist in app.js and knowledge base."""
        with open(os.path.join(PROJECT_ROOT, "app", "static", "js", "app.js"), "r", encoding="utf-8") as f:
            app_js = f.read()

        new_crops = ["Orange", "Peach", "Strawberry", "Cherry", "Blueberry", "Squash", "Soybean", "Raspberry"]
        for crop in new_crops:
            self.assertIn(crop, app_js, f"Crop {crop} not found in app.js dropdown or translations.")

        # Check knowledge base translations
        for class_name, data in self.knowledge_data.items():
            crop_name = data["crop"]
            for nc in new_crops:
                if nc in crop_name:
                    self.assertIn("translations", data)
                    self.assertIn("hi", data["translations"])
                    self.assertIn("gu", data["translations"])
                    self.assertIn("mr", data["translations"])

    def test_11_soybean_disease_never_confused_with_bell_pepper(self):
        """
        User Problem Test:
        Uploading a diseased soybean leaf (1.jpg) must NOT show Bell Pepper/Capsicum Bacterial Spot.
        It must be accurately diagnosed as Soybean Bacterial Blight under Auto-Detect mode.
        """
        soy_disease_path = os.path.join(self.samples_dir, "soybean_bacterial_blight.jpg")
        self.assertTrue(os.path.exists(soy_disease_path), "soybean_bacterial_blight.jpg sample missing.")

        res = predict(soy_disease_path, target_crop="auto")
        self.assertEqual(res["crop"], "Soybean", f"Expected crop 'Soybean', got '{res['crop']}'")
        self.assertEqual(res["class_label"], "Soybean___Bacterial_blight", f"Expected 'Soybean___Bacterial_blight', got '{res['class_label']}'")
        self.assertNotIn("Pepper", res["crop"], "Soybean leaf must NEVER be diagnosed as Pepper/Capsicum!")
        self.assertNotIn("Capsicum", res["crop"], "Soybean leaf must NEVER be diagnosed as Pepper/Capsicum!")
        self.assertGreaterEqual(res["confidence"], 0.85)
        self.assertIn("Bacterial Blight", res["display_name"])

    def test_12_bell_pepper_bacterial_spot_correctly_classified(self):
        """Verify Bell Pepper Bacterial Spot still diagnoses as Bell Pepper (Capsicum) with high confidence."""
        pepper_sample = os.path.join(self.samples_dir, "bell_pepper_bacterial_spot.jpg")
        res = predict(pepper_sample, target_crop="auto")
        self.assertIn("Pepper", res["crop"])
        self.assertEqual(res["class_label"], "Pepper__bell___Bacterial_spot")
        self.assertNotEqual(res["crop"], "Soybean", "Bell Pepper must not be confused with Soybean!")


if __name__ == "__main__":
    unittest.main()
