"""
Automated Unit Tests for AgriSmart AI Bonus Modules (A through G)
Compliant with SIH-2026 Problem Statement 1 Section 3.2.
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from app.modules.crop_recommender import recommend_crops
from app.modules.smart_irrigation import calculate_smart_irrigation
from app.modules.weather_service import get_weather_intelligence
from app.modules.sustainability import calculate_sustainability_score
from app.modules.farmer_assistant import ask_farmer_assistant
from app.modules.iot_simulator import get_current_iot_telemetry, trigger_iot_scenario
from app.modules.agentic_advisor import run_agent_loop


class TestBonusModules(unittest.TestCase):

    def test_bonus_a_crop_recommender(self):
        """Test Bonus A: Crop recommendation returns top-3 ranked crops."""
        res = recommend_crops(soil_type="Loamy", ph=6.5, n=100, p=50, k=40, season="Kharif")
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["recommendations"]), 3)
        self.assertIn("validation_metric", res)
        self.assertIn("data_source", res)

    def test_bonus_b_smart_irrigation(self):
        """Test Bonus B: Irrigation logic predicts correct decisions."""
        # Drought condition
        drought = calculate_smart_irrigation(current_soil_moisture=12.0, crop_type="Tomato", forecast_rain_mm=0.0)
        self.assertTrue("IRRIGAT" in drought["decision"])
        self.assertGreater(drought["water_volume_liters_sqm"], 0.0)

        # Imminent rain condition
        rain = calculate_smart_irrigation(current_soil_moisture=18.0, crop_type="Tomato", forecast_rain_mm=15.0, rain_probability_pct=80.0)
        self.assertIn("DELAY", rain["decision"])

    def test_bonus_c_weather_intelligence(self):
        """Test Bonus C: Weather service returns current conditions and disease risk."""
        w = get_weather_intelligence()
        self.assertEqual(w["status"], "success")
        self.assertIn("disease_risk_index", w)
        self.assertIn("agronomic_actions", w)

    def test_bonus_d_sustainability_score(self):
        """Test Bonus D: Sustainability formula produces 0-100 score and quantified savings."""
        res = calculate_sustainability_score(irrigation_method="Drip Irrigation", solar_powered_pump=True)
        self.assertGreaterEqual(res["sustainability_score"], 80.0)
        self.assertIn("quantified_impact", res)
        self.assertGreater(res["quantified_impact"]["water_saved_liters_ha"], 0)
        self.assertGreater(res["quantified_impact"]["carbon_emissions_avoided_kg_co2e"], 0)

    def test_bonus_e_farmer_assistant(self):
        """Test Bonus E: Grounded assistant returns citations and translations."""
        en_res = ask_farmer_assistant("How to manage blight?", language="en")
        self.assertIn("ICAR", en_res["grounded_source"])
        hi_res = ask_farmer_assistant("ब्लाइट कैसे रोकें?", language="hi")
        self.assertEqual(hi_res["language"], "hi")

    def test_bonus_f_iot_telemetry(self):
        """Test Bonus F: IoT telemetry stream."""
        trigger_iot_scenario("normal")
        telemetry = get_current_iot_telemetry()
        self.assertIn("device_id", telemetry)
        self.assertIn("telemetry", telemetry)
        self.assertIn("soil_moisture_pct", telemetry["telemetry"])

    def test_bonus_g_agentic_advisor(self):
        """Test Bonus G: Autonomous decision loop executes all 4 stages."""
        cycle = run_agent_loop(crop="Tomato", stage="Mid-Season / Flowering", diagnosis="Tomato___Early_blight")
        self.assertIn("cycle_id", cycle)
        self.assertIn("perception", cycle)
        self.assertIn("reasoning_summary", cycle)
        self.assertIn("autonomous_actions", cycle)
        self.assertIn("farmer_alert_message", cycle)
        self.assertGreaterEqual(len(cycle["trace_log"]), 4)


if __name__ == "__main__":
    unittest.main()
