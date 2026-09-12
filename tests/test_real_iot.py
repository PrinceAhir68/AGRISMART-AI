"""
AgriSmart AI - Automated Unit Tests for Real IoT Hardware Gateway
Validates:
1. Strict No-Fake-Data Guarantee: Disconnected hardware yields None/null for all sensors.
2. Selective Real Sensor Ingestion: Only provided sensors are populated; missing ones remain None.
3. COM Port Scanning: Lists system serial devices.
4. Safe Disconnect: Flushes telemetry buffers back to None.
5. Autonomous Agentic Loop Resilience: Operates cleanly without hardware.
"""

import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.modules.iot_manager import iot_manager
from app.modules.agentic_advisor import run_agent_loop


class TestRealIoTHardware(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Ensure clean disconnected state before each test
        iot_manager.disconnect()

    def tearDown(self):
        iot_manager.disconnect()

    def test_disconnected_by_default_has_no_fake_data(self):
        """Verify that disconnected IoT gateway strictly returns None/null with no fake values."""
        status_resp = self.client.get("/api/iot/status")
        self.assertEqual(status_resp.status_code, 200)
        status = status_resp.json()
        self.assertFalse(status["connected"])

        telem_resp = self.client.get("/api/iot/telemetry")
        self.assertEqual(telem_resp.status_code, 200)
        telem_frame = telem_resp.json()
        self.assertFalse(telem_frame["connected"])
        self.assertEqual(telem_frame["status_flag"], "NO_DEVICE_CONNECTED")

        # Crucial check: all sensor values MUST be None/null
        t = telem_frame["telemetry"]
        self.assertIsNone(t["soil_moisture_pct"])
        self.assertIsNone(t["ambient_temperature_c"])
        self.assertIsNone(t["relative_humidity_pct"])
        self.assertIsNone(t["soil_ph"])
        self.assertIsNone(t["soil_nitrogen_mg_kg"])

    def test_real_sensor_ingest_populates_only_provided_fields(self):
        """
        User Requirement: 'take real data from the device and show only real data
        other are make blank'.
        """
        # Microcontroller only has a soil moisture sensor attached
        payload = {
            "device_id": "ARDUINO-MOISTURE-ONLY",
            "soil_moisture_pct": 34.2
        }
        resp = self.client.post("/api/iot/ingest", json=payload)
        self.assertEqual(resp.status_code, 200)

        telem_resp = self.client.get("/api/iot/telemetry")
        telem = telem_resp.json()
        self.assertTrue(telem["connected"])
        self.assertEqual(telem["telemetry"]["soil_moisture_pct"], 34.2)

        # Other absent sensors MUST remain strictly None (blank)
        self.assertIsNone(telem["telemetry"]["ambient_temperature_c"])
        self.assertIsNone(telem["telemetry"]["relative_humidity_pct"])
        self.assertIsNone(telem["telemetry"]["soil_ph"])

    def test_ingest_with_sensor_aliases(self):
        """Verify that microcontrollers sending 'temp', 'moist', 'hum', 'ph' are mapped properly."""
        payload = {
            "moist": 28.5,
            "temp": 31.0,
            "rh": 58.0,
            "ph": 6.85
        }
        resp = self.client.post("/api/iot/ingest", json=payload)
        self.assertEqual(resp.status_code, 200)

        telem = self.client.get("/api/iot/telemetry").json()
        self.assertEqual(telem["telemetry"]["soil_moisture_pct"], 28.5)
        self.assertEqual(telem["telemetry"]["ambient_temperature_c"], 31.0)
        self.assertEqual(telem["telemetry"]["relative_humidity_pct"], 58.0)
        self.assertEqual(telem["telemetry"]["soil_ph"], 6.85)

    def test_disconnect_endpoint_clears_all_data(self):
        """Disconnect must reset status and wipe all sensors to None."""
        # First ingest some data
        self.client.post("/api/iot/ingest", json={"soil_moisture_pct": 45.0})
        self.assertTrue(self.client.get("/api/iot/status").json()["connected"])

        # Disconnect
        disc_resp = self.client.post("/api/iot/disconnect")
        self.assertEqual(disc_resp.status_code, 200)

        status = self.client.get("/api/iot/status").json()
        self.assertFalse(status["connected"])

        telem = self.client.get("/api/iot/telemetry").json()
        self.assertFalse(telem["connected"])
        self.assertIsNone(telem["telemetry"]["soil_moisture_pct"])

    def test_ports_scanning_endpoint(self):
        """Verify the COM port scanner endpoint."""
        resp = self.client.get("/api/iot/ports")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("ports", resp.json())
        self.assertIsInstance(resp.json()["ports"], list)

    def test_arduino_sketch_generator_endpoint(self):
        """Verify endpoint serving C++ firmware sketch."""
        resp = self.client.get("/api/iot/arduino-sketch")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("sketch", resp.json())
        sketch = resp.json()["sketch"]
        self.assertIn("analogRead", sketch)
        self.assertIn("soil_moisture_pct", sketch)

    def test_agentic_advisor_resilience_when_hardware_disconnected(self):
        """Verify that agent decision cycle executes without errors even when hardware is disconnected."""
        # Hardware is disconnected in setUp
        cycle = run_agent_loop(crop="Tomato", stage="Mid-Season / Flowering", diagnosis="Tomato___Early_blight")
        self.assertIn("cycle_id", cycle)
        self.assertIn("valve_state", cycle)
        # Verify that perception log mentions no hardware detected / baseline mode
        trace_str = " ".join(cycle["trace_log"])
        self.assertTrue(
            "NO PHYSICAL SENSOR DETECTED" in trace_str or "Sensor telemetry status" in trace_str or "baseline" in trace_str
        )


if __name__ == "__main__":
    unittest.main()
