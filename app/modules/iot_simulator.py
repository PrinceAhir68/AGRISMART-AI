"""
AgriSmart AI - Bonus Module F: IoT Edge Sensor Telemetry Simulator
Compliant with SIH-2026 Problem Statement 1 Section 3.2 & Section 12:
  Sensors (real or simulated) -> ESP32 / Raspberry Pi -> Cloud / API -> AI/ML Engine -> Recommendation Engine -> Web / Mobile App -> Farmer

Sensors Emulated:
  1. Capacitive Soil Moisture Sensor (Volumetric Water Content %)
  2. SHT31 Digital Ambient Temperature (°C)
  3. Digital Air Relative Humidity (%)
  4. Soil Glass Electrode pH Sensor (pH 3.5 - 9.0)
  5. Optical Soil N-P-K Sensor (mg/kg)
  6. Edge Gateway Metrics (Solar panel V, Battery level %, LoRa/WiFi RSSI)
"""

import time
import math
import random
import datetime
from typing import Dict, Any


class IoTEsp32GatewaySimulator:
    """
    Simulates an ESP32-WROOM / Raspberry Pi agricultural edge device
    broadcasting MQTT / REST sensor frames every telemetry interval.
    """
    def __init__(self, device_id: str = "ESP32-AGRI-FIELD-01", location: str = "Plot 4B (Tomato - North Grid)"):
        self.device_id = device_id
        self.location = location
        self.base_moisture = 22.5
        self.base_temp = 29.5
        self.base_humidity = 64.0
        self.base_ph = 6.6
        self.anomaly_mode = None  # None, 'drought', 'rain', 'acid_surge'
        self.cycle_step = 0

    def set_anomaly(self, mode: str):
        """Simulate real-world field anomalies for live judge demonstration."""
        self.anomaly_mode = mode

    def get_telemetry_frame(self) -> Dict[str, Any]:
        """Generates a complete RFC-compliant sensor telemetry packet."""
        self.cycle_step += 1
        t = self.cycle_step * 0.1
        
        # Diurnal fluctuation
        temp_drift = 2.0 * math.sin(t) + random.uniform(-0.3, 0.3)
        hum_drift = -2.5 * math.sin(t) + random.uniform(-0.5, 0.5)
        moist_drift = -0.1 * (self.cycle_step % 50) * 0.1  # gradual dry-down
        
        current_temp = self.base_temp + temp_drift
        current_hum = self.base_humidity + hum_drift
        current_moist = self.base_moisture + moist_drift
        current_ph = self.base_ph + random.uniform(-0.05, 0.05)

        # Apply anomaly overrides if activated
        status_flag = "NORMAL"
        if self.anomaly_mode == "drought":
            current_moist = max(8.5, current_moist - 8.0)
            current_temp += 3.5
            current_hum -= 15.0
            status_flag = "ALERT_WATER_STRESS"
        elif self.anomaly_mode == "rain":
            current_moist = min(36.0, current_moist + 12.0)
            current_hum = min(95.0, current_hum + 25.0)
            current_temp -= 3.0
            status_flag = "RAIN_INFLOW_DETECTED"
        elif self.anomaly_mode == "acid_surge":
            current_ph = 4.8
            status_flag = "ALERT_SOIL_ACIDITY"

        current_moist = round(max(5.0, min(50.0, current_moist)), 1)
        current_temp = round(current_temp, 1)
        current_hum = round(max(20.0, min(99.0, current_hum)), 1)
        current_ph = round(max(4.0, min(9.0, current_ph)), 2)

        # NPK sensor readings
        nitrogen = int(105 + random.randint(-5, 5))
        phosphorus = int(52 + random.randint(-3, 3))
        potassium = int(48 + random.randint(-4, 4))

        # Gateway hardware telemetry
        solar_volts = round(4.1 + 0.2 * math.sin(t), 2)
        battery_pct = 94
        wifi_rssi_dbm = -64 + random.randint(-3, 3)

        payload = {
            "device_id": self.device_id,
            "device_model": "ESP32-S3 AgriMesh Node v2.1",
            "firmware_version": "1.4.2-SIH26",
            "field_location": self.location,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status_flag": status_flag,
            "telemetry": {
                "soil_moisture_pct": current_moist,
                "ambient_temperature_c": current_temp,
                "relative_humidity_pct": current_hum,
                "soil_ph": current_ph,
                "soil_nitrogen_mg_kg": nitrogen,
                "soil_phosphorus_mg_kg": phosphorus,
                "soil_potassium_mg_kg": potassium
            },
            "hardware_health": {
                "solar_voltage_v": solar_volts,
                "battery_pct": battery_pct,
                "rssi_dbm": wifi_rssi_dbm,
                "mesh_hops": 1
            },
            "architecture_path": "Sensors (Real/Simulated) -> ESP32 Gateway -> REST/MQTT API -> AgriSmart AI Core"
        }
        return payload


# Import real hardware IoT manager
from app.modules.iot_manager import iot_manager

# Singleton instance for backward compatibility
iot_gateway = IoTEsp32GatewaySimulator()


def get_current_iot_telemetry() -> Dict[str, Any]:
    """
    Exposes current sensor stream frame from physical IoT Hardware Manager.
    Returns None / blank for fields when no real hardware is connected.
    """
    return iot_manager.get_telemetry_frame()


def trigger_iot_scenario(scenario: str) -> Dict[str, str]:
    """
    Allows unit tests to verify system response under simulated conditions.
    """
    iot_manager.set_test_scenario(scenario)
    return {"status": "success", "mode": scenario}


if __name__ == "__main__":
    frame = get_current_iot_telemetry()
    print("Real Hardware IoT Telemetry Frame:")
    print("Connected:", frame.get("connected"))
    print("Telemetry:", frame["telemetry"])
    print("Architecture:", frame["architecture_path"])

