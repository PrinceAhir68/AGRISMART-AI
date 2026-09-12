"""
AgriSmart AI - Bonus Module G: Autonomous Agentic Agricultural Advisor
Compliant with SIH-2026 Problem Statement 1 Section 3.2 Bonus Module G.

Autonomous Loop:
  [1. PERCEPTION] -> [2. MULTI-MODAL REASONING] -> [3. DECISION ENGINE] -> [4. ACTUATION & FARMER ALERT]

Demonstrates end-to-end autonomous reasoning:
  Monitors sensor telemetry + weather forecasts + leaf vision status,
  reasons about water stress and pathogen pressure, and executes automated actuation
  (smart solenoid valve trigger) and farmer advisory notifications.
"""

import time
import os
import sys
import datetime
from typing import Dict, Any, List

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.modules.iot_simulator import get_current_iot_telemetry
from app.modules.weather_service import get_weather_intelligence
from app.modules.smart_irrigation import calculate_smart_irrigation


class AgriSmartAgenticAdvisor:
    """
    Autonomous agricultural agent executing continuous observe-reason-decide-act loops.
    """
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
        self.smart_valve_state = "CLOSED"  # CLOSED or OPEN
        self.valve_open_since = None

    def run_decision_cycle(
        self,
        crop_type: str = "Tomato",
        growth_stage: str = "Mid-Season / Flowering",
        latest_leaf_diagnosis: str = "Tomato___Early_blight"
    ) -> Dict[str, Any]:
        """
        Executes one complete autonomous reasoning cycle.
        """
        cycle_id = f"CYCLE-{int(time.time())}"
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        logs = []

        # ----------------------------------------------------
        # STAGE 1: PERCEPTION (Observe world state)
        # ----------------------------------------------------
        logs.append(f"[{timestamp}] STAGE 1: PERCEPTION initiated.")
        
        # 1.1 Ingest IoT sensor stream
        sensor_data = get_current_iot_telemetry()
        raw_moist = sensor_data["telemetry"].get("soil_moisture_pct")
        raw_temp = sensor_data["telemetry"].get("ambient_temperature_c")
        raw_hum = sensor_data["telemetry"].get("relative_humidity_pct")
        raw_ph = sensor_data["telemetry"].get("soil_ph")

        is_hw_connected = sensor_data.get("connected", False)
        conn_type = sensor_data.get("connection_type", "None")

        if is_hw_connected and raw_moist is not None:
            moisture = float(raw_moist)
            temp_in = float(raw_temp) if raw_temp is not None else 28.0
            hum_in = float(raw_hum) if raw_hum is not None else 65.0
            ph_in = float(raw_ph) if raw_ph is not None else 6.8
            logs.append(f"  * Sensor telemetry ingested [REAL HARDWARE via {conn_type}]: Moisture={moisture}%, Temp={temp_in}°C, RH={hum_in}%, pH={ph_in}")
        else:
            moisture = 24.0  # Agronomic baseline for loamy soil capacity
            temp_in = float(raw_temp) if raw_temp is not None else 28.0
            hum_in = float(raw_hum) if raw_hum is not None else 65.0
            ph_in = float(raw_ph) if raw_ph is not None else 6.8
            logs.append(f"  * Sensor telemetry status: [NO PHYSICAL SENSOR DETECTED] Operating on soil moisture baseline ({moisture}%) and satellite meteorological feeds.")


        # 1.2 Ingest Live/Forecast Weather
        weather = get_weather_intelligence()
        rain_prob = weather["current_weather"]["rain_24h_prob_pct"]
        rain_sum = weather["current_weather"]["rain_24h_sum_mm"]
        fungal_risk = weather["disease_risk_index"]
        logs.append(f"  * Weather intelligence synced: 24h Rain Prob={rain_prob}%, Predicted Rain={rain_sum}mm, Pathogen Risk Index={fungal_risk}/100")

        # 1.3 Ingest Leaf Computer Vision Diagnostic
        logs.append(f"  * Leaf vision status: Last classified diagnosis='{latest_leaf_diagnosis}'")

        # ----------------------------------------------------
        # STAGE 2: MULTI-MODAL REASONING
        # ----------------------------------------------------
        logs.append(f"[{timestamp}] STAGE 2: REASONING & CROSS-MODAL SYNTHESIS.")
        
        irrigation_assessment = calculate_smart_irrigation(
            current_soil_moisture=moisture,
            soil_type="Loamy",
            crop_type=crop_type,
            growth_stage=growth_stage,
            forecast_rain_mm=rain_sum,
            rain_probability_pct=rain_prob,
            ambient_temp_c=temp_in
        )
        
        reasons = []
        is_water_critical = moisture < irrigation_assessment["stress_threshold_pct"]
        rain_likely = rain_sum >= 8.0 and rain_prob >= 60

        if is_water_critical and not rain_likely:
            reasons.append(f"Soil moisture ({moisture}%) is BELOW critical {growth_stage} threshold ({irrigation_assessment['stress_threshold_pct']}%). Transpiration deficit active.")
        elif is_water_critical and rain_likely:
            reasons.append(f"Soil moisture ({moisture}%) is low, BUT forecasted rainfall ({rain_sum}mm @ {rain_prob}%) will replenish root zone naturally.")
        else:
            reasons.append(f"Soil moisture ({moisture}%) is stable. No water stress detected.")

        pathogen_alert = False
        if "blight" in latest_leaf_diagnosis.lower() or fungal_risk >= 70:
            pathogen_alert = True
            reasons.append(f"Elevated fungal proliferation probability: Disease detection confirms presence of {latest_leaf_diagnosis}, amplified by atmospheric humidity ({hum_in}%).")

        for r in reasons:
            logs.append(f"  * {r}")

        # ----------------------------------------------------
        # STAGE 3: DECISION ENGINE
        # ----------------------------------------------------
        logs.append(f"[{timestamp}] STAGE 3: DECISION SELECTION.")
        
        autonomous_actions = []
        valve_action = "MAINTAIN_CLOSED"
        
        if is_water_critical and not rain_likely:
            valve_action = "TRIGGER_OPEN"
            self.smart_valve_state = "OPEN"
            self.valve_open_since = timestamp
            runtime = irrigation_assessment["estimated_drip_runtime_minutes"]
            autonomous_actions.append(f"ACTUATION: Smart Solenoid Valve #1 OPENED for {runtime} min (delivering {irrigation_assessment['water_volume_liters_sqm']} L/m²).")
        elif rain_likely:
            valve_action = "KEEP_CLOSED_RAIN_AHEAD"
            self.smart_valve_state = "CLOSED"
            autonomous_actions.append(f"CONSERVATION: Solenoid Valve LOCKED CLOSED. Estimated {irrigation_assessment['water_volume_liters_sqm'] * 1000:.0f} L water and pumping kWh saved.")
        else:
            valve_action = "MAINTAIN_CLOSED"
            self.smart_valve_state = "CLOSED"
            autonomous_actions.append("STANDBY: Solenoid Valve kept CLOSED. Moisture levels optimal.")

        if pathogen_alert:
            autonomous_actions.append("ADVISORY: Autonomous prescription dispatched to farmer: Apply preventative bio-fungicide (Trichoderma viride 5g/L) before next rainfall.")

        for a in autonomous_actions:
            logs.append(f"  * {a}")

        # ----------------------------------------------------
        # STAGE 4: NOTIFICATION & ACTUATION DISPATCH
        # ----------------------------------------------------
        logs.append(f"[{timestamp}] STAGE 4: FARMER NOTIFICATION & HARDWARE TELEMETRY DISPATCH.")
        
        farmer_sms = (
            f"[AgriSmart AI Alert] {crop_type} ({growth_stage}): "
            f"Moisture={moisture}%. Valve is {self.smart_valve_state}. "
            f"{'Rain expected soon - irrigation delayed to save water.' if rain_likely else ('Emergency watering active.' if valve_action == 'TRIGGER_OPEN' else 'Field conditions normal.')} "
            f"{'Warning: Fungal risk high, inspect lower leaves.' if pathogen_alert else ''}"
        )
        logs.append(f"  * Push/SMS Alert Generated: \"{farmer_sms}\"")

        cycle_summary = {
            "cycle_id": cycle_id,
            "timestamp": timestamp,
            "crop": crop_type,
            "growth_stage": growth_stage,
            "valve_state": self.smart_valve_state,
            "perception": {
                "soil_moisture": moisture,
                "soil_ph": ph_in,
                "temperature": temp_in,
                "humidity": hum_in,
                "rain_forecast_mm": rain_sum,
                "rain_probability_pct": rain_prob,
                "leaf_diagnosis": latest_leaf_diagnosis
            },
            "reasoning_summary": reasons,
            "autonomous_actions": autonomous_actions,
            "farmer_alert_message": farmer_sms,
            "trace_log": logs
        }

        self.history.append(cycle_summary)
        if len(self.history) > 20:
            self.history.pop(0)

        return cycle_summary


# Singleton advisor agent
agentic_advisor = AgriSmartAgenticAdvisor()


def run_agent_loop(crop: str = "Tomato", stage: str = "Mid-Season / Flowering", diagnosis: str = "Tomato___Early_blight") -> Dict[str, Any]:
    """Exposes agent run cycle."""
    return agentic_advisor.run_decision_cycle(crop_type=crop, growth_stage=stage, latest_leaf_diagnosis=diagnosis)


if __name__ == "__main__":
    result = run_agent_loop()
    print("Bonus Module G: Agentic Advisor Cycle Execution:")
    print("Cycle ID:", result["cycle_id"])
    print("Valve State:", result["valve_state"])
    print("Farmer Alert:", result["farmer_alert_message"])
    print("\nTrace Log:")
    for l in result["trace_log"]:
        print(l)
