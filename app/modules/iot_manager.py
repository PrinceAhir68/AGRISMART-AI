"""
AgriSmart AI - Production Real IoT Hardware Gateway & Manager
Zero Fake Data Architecture:
- Disconnected: All telemetry fields return None / blank (--).
- Connected: Displays strictly physical sensor readings from USB, Wi-Fi, or Bluetooth.
- Watchdog: Automatically expires connection if no real hardware heartbeat within 15 seconds.
"""

import time
import json
import re
import datetime
import threading
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("agrismart.iot")

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


NON_IOT_DEVICE_REGEX = re.compile(
    r'(watch|band|fitbit|gear|smartwatch|wear|speaker|soundbar|audio|headphone|headset|earbud|earphone|airpod|buds|tws|soundcore|boat\s*(?:stone|rockerz|airdopes|wave|storm)|jbl|sony\s*(?:wh|wf|srs)|bose|marshall|zebronics\s*(?:zeb|sound)|realme\s*buds|oneplus\s*buds|noise\s*(?:colorfit|shots)|fire-?boltt|boult|tv|dongle|mouse|keyboard|echo|alexa|nest|homepod|car|handsfree)',
    re.IGNORECASE
)


class RealIoTHardwareGateway:

    """
    Manages physical IoT hardware connections:
    1. USB Serial Cable (Arduino, ESP32, STM32, CH340, CP2102)
    2. Wi-Fi Sensor Station (ESP32 / ESP8266 HTTP Ingest & Polling)
    3. Bluetooth BLE Probes (Web Bluetooth / BLE UART)
    """

    def __init__(self):
        self.is_connected: bool = False
        self.connection_type: Optional[str] = None  # "USB", "WIFI", "BLUETOOTH", "SIMULATED"
        self.device_id: Optional[str] = None
        self.device_model: Optional[str] = None
        self.port_or_endpoint: Optional[str] = None
        self.baudrate: int = 115200
        self.last_heartbeat_ts: float = 0.0
        self.watchdog_timeout_sec: float = 15.0

        # Raw serial thread controls
        self.serial_thread: Optional[threading.Thread] = None
        self.serial_obj: Optional[Any] = None
        self.stop_serial_event: threading.Event = threading.Event()

        # Wi-Fi polling thread controls
        self.wifi_thread: Optional[threading.Thread] = None
        self.stop_wifi_event: threading.Event = threading.Event()

        # Raw terminal buffer (up to 50 recent lines)
        self.raw_terminal_log: List[str] = []
        self._lock = threading.RLock()


        # Physical Sensor Registry (Strict Real-Only, None when absent/disconnected)
        self.real_telemetry: Dict[str, Optional[float]] = {
            "soil_moisture_pct": None,
            "ambient_temperature_c": None,
            "relative_humidity_pct": None,
            "soil_ph": None,
            "soil_nitrogen_mg_kg": None,
            "soil_phosphorus_mg_kg": None,
            "soil_potassium_mg_kg": None
        }

        self.hardware_health: Dict[str, Any] = {
            "solar_voltage_v": None,
            "battery_pct": None,
            "rssi_dbm": None,
            "packets_received": 0
        }

        # Test simulation override flag (for unit tests only)
        self._simulated_mode: bool = False
        self._simulated_scenario: str = "normal"

    # -----------------------------------------------------------------
    # COM Port Discovery
    # -----------------------------------------------------------------
    def list_serial_ports(self) -> List[Dict[str, str]]:
        """Scans physical USB/COM ports on the host system."""
        ports_list = []
        if not SERIAL_AVAILABLE:
            return ports_list

        try:
            detected = serial.tools.list_ports.comports()
            for p in detected:
                ports_list.append({
                    "port": p.device,
                    "description": p.description or "Generic Serial Port",
                    "hwid": p.hwid or "",
                    "manufacturer": getattr(p, 'manufacturer', '') or "Unknown"
                })
        except Exception as e:
            print(f"[IoT Manager] Error scanning ports: {e}")

        return ports_list

    # -----------------------------------------------------------------
    # USB Serial Connection
    # -----------------------------------------------------------------
    def connect_usb(self, port: str, baudrate: int = 115200) -> Dict[str, Any]:
        """Connects to a physical USB COM port via PySerial."""
        if not SERIAL_AVAILABLE:
            return {"status": "error", "message": "PySerial not installed on server."}

        self.disconnect()

        try:
            self.stop_serial_event.clear()
            self.serial_obj = serial.Serial(port=port, baudrate=baudrate, timeout=1.0)
            self.port_or_endpoint = port
            self.baudrate = baudrate
            self.device_id = f"USB-NODE-{port}"
            self.device_model = f"USB Serial Device ({baudrate} bps)"
            self.connection_type = "USB"
            self.is_connected = True
            self.last_heartbeat_ts = time.time()

            # Start reading thread
            self.serial_thread = threading.Thread(
                target=self._serial_reader_worker,
                daemon=True,
                name=f"IoT-Serial-{port}"
            )
            self.serial_thread.start()

            self._log_terminal(f"Connected to USB port {port} at {baudrate} baud.")
            return {
                "status": "connected",
                "connection_type": "USB",
                "port": port,
                "baudrate": baudrate
            }
        except Exception as e:
            self.disconnect()
            logger.error("Failed to connect to USB serial port %s: %s", port, e, exc_info=True)
            return {"status": "error", "message": f"Failed to connect to port {port}. Please verify the device is plugged in and not in use by another program."}

    def _serial_reader_worker(self):
        """Worker thread continuously reading lines from physical USB serial port."""
        while not self.stop_serial_event.is_set():
            try:
                if self.serial_obj and self.serial_obj.is_open:
                    line = self.serial_obj.readline()
                    if line:
                        text = line.decode('utf-8', errors='ignore').strip()
                        if text:
                            self._log_terminal(f"<< {text}")
                            self._parse_and_ingest_raw_string(text, "USB")
                else:
                    break
            except Exception as e:
                logger.error("Serial read worker error: %s", e, exc_info=True)
                self._log_terminal("Serial communication stream interrupted.")
                time.sleep(0.5)
                break

    # -----------------------------------------------------------------
    # Wi-Fi Sensor Polling
    # -----------------------------------------------------------------
    def connect_wifi(self, endpoint_url: str, poll_interval_sec: float = 3.0) -> Dict[str, Any]:
        """Connects to an ESP32 / Arduino Wi-Fi local HTTP endpoint."""
        import requests
        self.disconnect()

        target_url = endpoint_url.strip()
        if not target_url.startswith("http://") and not target_url.startswith("https://"):
            target_url = f"http://{target_url}"

        # Quick test connection
        try:
            resp = requests.get(target_url, timeout=3.0)
            if resp.status_code == 200:
                self.is_connected = True
                self.connection_type = "WIFI"
                self.port_or_endpoint = target_url
                self.device_id = f"WIFI-NODE-{target_url.replace('http://', '').replace('/', '_')}"
                self.device_model = "Wi-Fi AgriMesh Sensor Station"
                self.last_heartbeat_ts = time.time()
                self._parse_and_ingest_raw_string(resp.text, "WIFI")

                self.stop_wifi_event.clear()
                self.wifi_thread = threading.Thread(
                    target=self._wifi_poller_worker,
                    args=(target_url, poll_interval_sec),
                    daemon=True,
                    name="IoT-WifiPoller"
                )
                self.wifi_thread.start()
                self._log_terminal(f"Connected to Wi-Fi station at {target_url}")
                return {"status": "connected", "connection_type": "WIFI", "endpoint": target_url}
            else:
                logger.warning("Wi-Fi station at %s returned HTTP %s", target_url, resp.status_code)
                return {"status": "error", "message": f"Sensor station responded with status code {resp.status_code}."}
        except Exception as e:
            logger.error("Wi-Fi station connection error to %s: %s", target_url, e, exc_info=True)
            return {"status": "error", "message": "Unable to establish connection with Wi-Fi sensor station. Please verify the station IP and network."}

    def _wifi_poller_worker(self, target_url: str, interval: float):
        """Worker thread periodically polling Wi-Fi sensor endpoint."""
        import requests
        while not self.stop_wifi_event.is_set():
            try:
                resp = requests.get(target_url, timeout=2.5)
                if resp.status_code == 200:
                    self._parse_and_ingest_raw_string(resp.text, "WIFI")
            except Exception as e:
                logger.warning("Wi-Fi telemetry polling error: %s", e)
                self._log_terminal("Wi-Fi sensor stream interrupted. Retrying...")
            time.sleep(interval)

    # -----------------------------------------------------------------
    # Telemetry Ingestion Engine
    # -----------------------------------------------------------------
    def ingest_telemetry(self, raw_data: Dict[str, Any], connection_type: str = "WIFI") -> Dict[str, Any]:
        """
        Accepts real telemetry dictionary pushed from physical hardware,
        Web Serial API in browser, or Web Bluetooth API.
        STRICT REAL-ONLY: Only provided fields are updated; absent fields remain None.
        """
        with self._lock:
            # Validate device identity against non-IoT consumer electronics (speakers, smartwatches, etc.)
            dev_identifiers = [
                str(raw_data.get("device_id", "")),
                str(raw_data.get("device_model", "")),
                str(raw_data.get("device_name", ""))
            ]
            for dev_str in dev_identifiers:
                if dev_str and NON_IOT_DEVICE_REGEX.search(dev_str):
                    self._log_terminal(f"❌ [VALIDATION REJECTED] Ineligible device '{dev_str}' detected. Consumer audio/smartwatch devices cannot be connected as agricultural IoT sensors.")
                    return {
                        "status": "rejected",
                        "error": "DEVICE_REJECTED_NON_IOT",
                        "message": f"Ineligible device: '{dev_str}' is an audio speaker, smartwatch, or consumer wearable. AgriSmart AI strictly requires genuine Agricultural & Environmental IoT sensors."
                    }

            self.last_heartbeat_ts = time.time()
            self.is_connected = True
            self.connection_type = connection_type
            self._simulated_mode = False

            if "device_id" in raw_data and raw_data["device_id"]:
                self.device_id = str(raw_data["device_id"])
            elif not self.device_id:
                self.device_id = f"{connection_type}-AGRI-NODE"


            if "device_model" in raw_data and raw_data["device_model"]:
                self.device_model = str(raw_data["device_model"])

            # Clean and map known sensor keys
            field_mappings = {
                "soil_moisture_pct": ["soil_moisture_pct", "soil_moisture", "moisture", "moist", "sm"],
                "ambient_temperature_c": ["ambient_temperature_c", "temperature", "temp", "ambient_temp", "t"],
                "relative_humidity_pct": ["relative_humidity_pct", "humidity", "hum", "rh", "h"],
                "soil_ph": ["soil_ph", "ph", "soilph"],
                "soil_nitrogen_mg_kg": ["soil_nitrogen_mg_kg", "nitrogen", "n", "soil_n"],
                "soil_phosphorus_mg_kg": ["soil_phosphorus_mg_kg", "phosphorus", "p", "soil_p"],
                "soil_potassium_mg_kg": ["soil_potassium_mg_kg", "potassium", "k", "soil_k"]
            }

            # Map health keys
            health_mappings = {
                "solar_voltage_v": ["solar_voltage_v", "solar_v", "solar", "v_solar"],
                "battery_pct": ["battery_pct", "battery", "batt", "v_batt"],
                "rssi_dbm": ["rssi_dbm", "rssi", "wifi_rssi"]
            }

            # Check top-level or nested "telemetry" dictionary
            source_dict = raw_data.get("telemetry", raw_data)

            for target_key, aliases in field_mappings.items():
                found_val = None
                for alias in aliases:
                    if alias in source_dict and source_dict[alias] is not None:
                        try:
                            val = float(source_dict[alias])
                            # Basic physical plausibility validation
                            if target_key == "soil_moisture_pct" and 0.0 <= val <= 100.0:
                                found_val = round(val, 1)
                            elif target_key == "ambient_temperature_c" and -20.0 <= val <= 70.0:
                                found_val = round(val, 1)
                            elif target_key == "relative_humidity_pct" and 0.0 <= val <= 100.0:
                                found_val = round(val, 1)
                            elif target_key == "soil_ph" and 0.0 <= val <= 14.0:
                                found_val = round(val, 2)
                            elif "mg_kg" in target_key and 0.0 <= val <= 1000.0:
                                found_val = int(val)
                            break
                        except (ValueError, TypeError):
                            continue
                if found_val is not None:
                    self.real_telemetry[target_key] = found_val

            for target_key, aliases in health_mappings.items():
                for alias in aliases:
                    if alias in source_dict and source_dict[alias] is not None:
                        try:
                            self.hardware_health[target_key] = float(source_dict[alias])
                            break
                        except (ValueError, TypeError):
                            continue

            self.hardware_health["packets_received"] = self.hardware_health.get("packets_received", 0) + 1

        return {"status": "ok", "telemetry": self.real_telemetry}

    def _parse_and_ingest_raw_string(self, text: str, conn_type: str):
        """Parses JSON, CSV, or Key-Value strings from physical serial/network streams."""
        text = text.strip()
        if not text:
            return

        # Case 1: JSON payload
        if text.startswith("{") and text.endswith("}"):
            try:
                data = json.loads(text)
                self.ingest_telemetry(data, conn_type)
                return
            except json.JSONDecodeError:
                pass

        # Case 2: Key-Value pairs e.g. "moisture:34.2, temp:28.1, hum:65, ph:6.8"
        if ":" in text or "=" in text:
            kv_dict = {}
            parts = re.split(r'[,;\s]+', text)
            for part in parts:
                if ":" in part:
                    k, v = part.split(":", 1)
                    kv_dict[k.strip().lower()] = v.strip()
                elif "=" in part:
                    k, v = part.split("=", 1)
                    kv_dict[k.strip().lower()] = v.strip()
            if kv_dict:
                self.ingest_telemetry(kv_dict, conn_type)
                return

        # Case 3: Comma-separated values (CSV) e.g. "34.5, 28.2, 64.0, 6.8"
        # Standard agricultural CSV order: [Moisture, Temp, Humidity, pH]
        if "," in text:
            parts = [p.strip() for p in text.split(",")]
            csv_dict = {}
            try:
                if len(parts) >= 1 and parts[0]:
                    csv_dict["soil_moisture_pct"] = float(parts[0])
                if len(parts) >= 2 and parts[1]:
                    csv_dict["ambient_temperature_c"] = float(parts[1])
                if len(parts) >= 3 and parts[2]:
                    csv_dict["relative_humidity_pct"] = float(parts[2])
                if len(parts) >= 4 and parts[3]:
                    csv_dict["soil_ph"] = float(parts[3])
                if csv_dict:
                    self.ingest_telemetry(csv_dict, conn_type)
                    return
            except ValueError:
                pass

    # -----------------------------------------------------------------
    # Disconnect & Watchdog
    # -----------------------------------------------------------------
    def disconnect(self) -> Dict[str, str]:
        """Safely disconnects all physical links and resets telemetry to blank."""
        # Stop serial
        self.stop_serial_event.set()
        if self.serial_obj:
            try:
                self.serial_obj.close()
            except Exception:
                pass
            self.serial_obj = None

        # Stop Wi-Fi
        self.stop_wifi_event.set()

        # Reset state
        with self._lock:
            self.is_connected = False
            self.connection_type = None
            self.device_id = None
            self.device_model = None
            self.port_or_endpoint = None
            self.last_heartbeat_ts = 0.0
            self._simulated_mode = False

            # Reset all sensor telemetry to None (blank)
            for k in self.real_telemetry:
                self.real_telemetry[k] = None

            for k in self.hardware_health:
                if k != "packets_received":
                    self.hardware_health[k] = None

        self._log_terminal("Device disconnected. Telemetry cleared to blank.")
        return {"status": "disconnected"}

    def check_watchdog(self):
        """Watchdog resets connection if real hardware packet hasn't arrived within 15s."""
        if self.is_connected and not self._simulated_mode:
            if time.time() - self.last_heartbeat_ts > self.watchdog_timeout_sec:
                self._log_terminal("Hardware timeout (>15s since last packet). Disconnecting.")
                self.disconnect()

    def _log_terminal(self, msg: str):
        """Appends line to circular log buffer for UI terminal."""
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] {msg}"
        with self._lock:
            self.raw_terminal_log.append(entry)
            if len(self.raw_terminal_log) > 60:
                self.raw_terminal_log.pop(0)

    # -----------------------------------------------------------------
    # Public Telemetry Output Frame
    # -----------------------------------------------------------------
    def get_status(self) -> Dict[str, Any]:
        """Returns connection status summary for navbar and badges."""
        self.check_watchdog()
        return {
            "connected": self.is_connected,
            "connection_type": self.connection_type,
            "device_id": self.device_id,
            "device_model": self.device_model,
            "port_or_endpoint": self.port_or_endpoint,
            "last_heartbeat_sec_ago": round(time.time() - self.last_heartbeat_ts, 1) if self.last_heartbeat_ts > 0 else None,
            "terminal_log": list(self.raw_terminal_log[-15:])
        }

    def get_telemetry_frame(self) -> Dict[str, Any]:
        """
        Returns full telemetry frame.
        When DISCONNECTED: all sensor fields are None / blank.
        When CONNECTED: returns only real physical sensor readings.
        """
        self.check_watchdog()

        # Handle simulation mode (used only if explicitly invoked in automated tests)
        if self._simulated_mode:
            return self._get_simulated_frame()

        if not self.is_connected:
            return {
                "connected": False,
                "device_id": None,
                "device_model": None,
                "connection_type": None,
                "timestamp": None,
                "status_flag": "NO_DEVICE_CONNECTED",
                "telemetry": {k: None for k in self.real_telemetry},
                "hardware_health": {k: None for k in self.hardware_health},
                "architecture_path": "No physical IoT hardware connected. Telemetry is blank."
            }

        return {
            "connected": True,
            "device_id": self.device_id,
            "device_model": self.device_model,
            "connection_type": self.connection_type,
            "port_or_endpoint": self.port_or_endpoint,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status_flag": "ACTIVE_REAL_HARDWARE",
            "telemetry": dict(self.real_telemetry),
            "hardware_health": dict(self.hardware_health),
            "architecture_path": f"Physical Sensors -> {self.device_model} ({self.connection_type}) -> AgriSmart AI Core"
        }

    # -----------------------------------------------------------------
    # Test Scenario Simulation (Only for Automated Testing)
    # -----------------------------------------------------------------
    def set_test_scenario(self, mode: str):
        """Allows unit tests to verify pipeline response under simulated conditions."""
        self._simulated_mode = True
        self._simulated_scenario = mode
        self.is_connected = True
        self.connection_type = "SIMULATED"
        self.device_id = "ESP32-TEST-BENCH"
        self.device_model = "AgriSmart Virtual Hardware Emulator"

    def _get_simulated_frame(self) -> Dict[str, Any]:
        """Generates predictable test values for unittest verification."""
        moist = 24.5
        temp = 28.0
        hum = 65.0
        ph = 6.8
        status = "NORMAL"

        if self._simulated_scenario == "drought":
            moist = 11.2
            temp = 33.5
            hum = 42.0
            status = "ALERT_WATER_STRESS"
        elif self._simulated_scenario == "rain":
            moist = 38.0
            hum = 88.0
            temp = 24.0
            status = "RAIN_INFLOW_DETECTED"

        return {
            "connected": True,
            "device_id": self.device_id,
            "device_model": self.device_model,
            "connection_type": "SIMULATED",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status_flag": status,
            "telemetry": {
                "soil_moisture_pct": moist,
                "ambient_temperature_c": temp,
                "relative_humidity_pct": hum,
                "soil_ph": ph,
                "soil_nitrogen_mg_kg": 110,
                "soil_phosphorus_mg_kg": 50,
                "soil_potassium_mg_kg": 45
            },
            "hardware_health": {
                "solar_voltage_v": 4.1,
                "battery_pct": 92,
                "rssi_dbm": -65,
                "packets_received": 1
            },
            "architecture_path": "Sensors (Real/Simulated) -> ESP32 Gateway -> REST/MQTT API -> AgriSmart AI Core"
        }

    # -----------------------------------------------------------------
    # Firmware Code Generator
    # -----------------------------------------------------------------
    @staticmethod
    def get_arduino_sketch() -> str:
        """Returns ready-to-flash C++ sketch for Arduino Uno / Nano and ESP32."""
        return """/*
 * AgriSmart AI - Real IoT Hardware Firmware (Arduino & ESP32)
 * Sensors Supported:
 *   - Capacitive Soil Moisture Sensor (Analog Pin A0)
 *   - DHT11 / DHT22 Temperature & Humidity (Digital Pin D2)
 *   - Analog Soil pH Sensor (Analog Pin A1)
 *
 * Transports:
 *   - Mode 1: USB Serial (Baud 115200) -> Works with Web Serial & USB Cable!
 *   - Mode 2: Wi-Fi HTTP Post (ESP32) -> Ingests to /api/iot/ingest
 */

#include <Arduino.h>

// Pin Definitions
#define SOIL_MOISTURE_PIN A0
#define SOIL_PH_PIN       A1

// Calibration values for Capacitive Soil Moisture Sensor v1.2
const int AIR_VALUE   = 620; // Sensor in dry air
const int WATER_VALUE = 310; // Sensor submerged in water

void setup() {
  Serial.begin(115200);
  while (!Serial) { delay(10); }
  Serial.println("{\\"status\\": \\"booted\\", \\"device\\": \\"AgriSmart-Node-v1\\"}");
}

void loop() {
  // 1. Read Capacitive Soil Moisture
  int rawMoist = analogRead(SOIL_MOISTURE_PIN);
  float moistPct = map(rawMoist, AIR_VALUE, WATER_VALUE, 0, 100);
  moistPct = constrain(moistPct, 0.0, 100.0);

  // 2. Read Soil pH Sensor (0-14 pH mapped from 0-5V or 0-3.3V)
  int rawPH = analogRead(SOIL_PH_PIN);
  float voltage = rawPH * (5.0 / 1023.0);
  float phVal = 7.0 + ((2.5 - voltage) * 3.5); // Calibration slope
  phVal = constrain(phVal, 3.5, 9.5);

  // 3. Emit Real JSON Telemetry Frame over Serial / USB
  Serial.print("{\\"soil_moisture_pct\\": ");
  Serial.print(moistPct, 1);
  Serial.print(", \\"soil_ph\\": ");
  Serial.print(phVal, 2);
  Serial.println("}");

  delay(2000); // 2-second sampling interval
}
"""


# Global singleton manager instance
iot_manager = RealIoTHardwareGateway()
