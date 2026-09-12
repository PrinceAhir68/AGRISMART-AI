"""
AgriSmart AI - FastAPI Application Backend
SIH-2026 Problem Statement 1: Core Vision Detection & All 7 Bonus Modules (A - G)
"""

import os
import sys
import shutil
import tempfile
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

# Ensure project root is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
sys.path.insert(0, PROJECT_ROOT)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Import core and bonus modules
from model.predict import predict
from app.modules.crop_recommender import recommend_crops
from app.modules.smart_irrigation import calculate_smart_irrigation
from app.modules.weather_service import get_weather_intelligence
from app.modules.sustainability import calculate_sustainability_score
from app.modules.farmer_assistant import ask_farmer_assistant
from app.modules.iot_simulator import get_current_iot_telemetry, trigger_iot_scenario
from app.modules.agentic_advisor import run_agent_loop

app = FastAPI(
    title="AgriSmart AI API",
    description="SIH-2026 Internal Hackathon - Problem Statement 1 (AgriSmart AI)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files mount
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
REPORT_DIR = os.path.join(PROJECT_ROOT, "report")
if os.path.exists(REPORT_DIR):
    app.mount("/report-assets", StaticFiles(directory=REPORT_DIR), name="report-assets")


@app.get("/")
def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "AgriSmart AI API is active. UI file loading."}


# -------------------------------------------------------------
# CORE TASK: Leaf Disease Detection (Computer Vision)
# -------------------------------------------------------------
@app.post("/api/predict")
async def predict_disease(file: UploadFile = File(...)):
    """
    Mandatory Core Task Endpoint:
    Accepts an uploaded plant leaf image and outputs predicted class, confidence,
    symptoms, immediate cultural precautions, organic remedies, and chemical controls.
    """
    try:
        suffix = os.path.splitext(file.filename)[1] or ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        result = predict(tmp_path)
        os.remove(tmp_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


@app.get("/api/samples")
def list_sample_images():
    """Returns available demonstration sample images."""
    samples_dir = os.path.join(PROJECT_ROOT, "model", "test_samples")
    if not os.path.exists(samples_dir):
        return {"samples": []}
    files = [f for f in os.listdir(samples_dir) if f.endswith((".jpg", ".png", ".jpeg"))]
    return {
        "samples": [
            {"filename": f, "path": f"/samples/{f}", "label": f.replace(".jpg", "").replace("_", " ").title()}
            for f in files
        ]
    }


@app.get("/samples/{filename}")
def serve_sample_image(filename: str):
    sample_file = os.path.join(PROJECT_ROOT, "model", "test_samples", filename)
    if os.path.exists(sample_file):
        return FileResponse(sample_file)
    raise HTTPException(status_code=404, detail="Sample image not found")


# -------------------------------------------------------------
# BONUS MODULE A: Crop Recommendation
# -------------------------------------------------------------
class CropRecRequest(BaseModel):
    soil_type: str = "Loamy"
    ph: float = 6.5
    n: float = 90.0
    p: float = 50.0
    k: float = 40.0
    temperature: float = 26.0
    humidity: float = 65.0
    rainfall: float = 80.0
    water_availability: str = "Moderate"
    season: str = "Kharif"
    previous_crop: str = "Wheat"
    location: str = "Western India"


@app.post("/api/crop-recommendation")
def api_crop_recommendation(req: CropRecRequest):
    return recommend_crops(
        soil_type=req.soil_type,
        ph=req.ph,
        n=req.n,
        p=req.p,
        k=req.k,
        temperature=req.temperature,
        humidity=req.humidity,
        rainfall=req.rainfall,
        water_availability=req.water_availability,
        season=req.season,
        previous_crop=req.previous_crop,
        location=req.location
    )


# -------------------------------------------------------------
# BONUS MODULE B: Smart Irrigation
# -------------------------------------------------------------
class IrrigationRequest(BaseModel):
    current_soil_moisture: float = 20.0
    soil_type: str = "Loamy"
    crop_type: str = "Tomato"
    growth_stage: str = "Mid-Season / Flowering"
    forecast_rain_mm: float = 0.0
    rain_probability_pct: float = 10.0
    ambient_temp_c: float = 30.0


@app.post("/api/smart-irrigation")
def api_smart_irrigation(req: IrrigationRequest):
    return calculate_smart_irrigation(
        current_soil_moisture=req.current_soil_moisture,
        soil_type=req.soil_type,
        crop_type=req.crop_type,
        growth_stage=req.growth_stage,
        forecast_rain_mm=req.forecast_rain_mm,
        rain_probability_pct=req.rain_probability_pct,
        ambient_temp_c=req.ambient_temp_c
    )


# -------------------------------------------------------------
# BONUS MODULE C: Weather-Based Intelligence
# -------------------------------------------------------------
@app.get("/api/weather")
def api_weather(lat: float = 23.0225, lon: float = 72.5714, name: str = "Ahmedabad, Gujarat"):
    return get_weather_intelligence(latitude=lat, longitude=lon, location_name=name)


# -------------------------------------------------------------
# BONUS MODULE D: Sustainability & Carbon Score
# -------------------------------------------------------------
class SustainabilityRequest(BaseModel):
    irrigation_method: str = "Drip Irrigation"
    water_applied_liters_sqm: float = 4.5
    optimal_water_liters_sqm: float = 4.0
    fertilizer_type: str = "Integrated Organic + NPK"
    solar_powered_pump: bool = True
    organic_mulching: bool = True
    crop_rotation_with_legumes: bool = True
    disease_severity_pct: float = 5.0


@app.post("/api/sustainability")
def api_sustainability(req: SustainabilityRequest):
    return calculate_sustainability_score(
        irrigation_method=req.irrigation_method,
        water_applied_liters_sqm=req.water_applied_liters_sqm,
        optimal_water_liters_sqm=req.optimal_water_liters_sqm,
        fertilizer_type=req.fertilizer_type,
        solar_powered_pump=req.solar_powered_pump,
        organic_mulching=req.organic_mulching,
        crop_rotation_with_legumes=req.crop_rotation_with_legumes,
        disease_severity_pct=req.disease_severity_pct
    )


# -------------------------------------------------------------
# BONUS MODULE E: Grounded Farmer Assistant (GenAI)
# -------------------------------------------------------------
class AssistantRequest(BaseModel):
    query: str
    language: str = "en"  # "en", "hi", "gu", "mr"


@app.post("/api/assistant")
def api_assistant(req: AssistantRequest):
    return ask_farmer_assistant(query=req.query, language=req.language)


# -------------------------------------------------------------
# BONUS MODULE F: IoT Telemetry Feed & Scenarios
# -------------------------------------------------------------
@app.get("/api/iot/telemetry")
def api_iot_telemetry():
    return get_current_iot_telemetry()


class ScenarioRequest(BaseModel):
    scenario: str  # "normal", "drought", "rain", "acid_surge"


@app.post("/api/iot/scenario")
def api_iot_scenario(req: ScenarioRequest):
    return trigger_iot_scenario(req.scenario)


# -------------------------------------------------------------
# BONUS MODULE G: Autonomous Agentic Advisor
# -------------------------------------------------------------
class AgentCycleRequest(BaseModel):
    crop: str = "Tomato"
    stage: str = "Mid-Season / Flowering"
    diagnosis: str = "Tomato___Early_blight"


@app.post("/api/agent/cycle")
def api_agent_cycle(req: AgentCycleRequest):
    return run_agent_loop(crop=req.crop, stage=req.stage, diagnosis=req.diagnosis)


# -------------------------------------------------------------
# Model Report & Metrics Endpoint (Section 7.3)
# -------------------------------------------------------------
@app.get("/api/model/report")
def api_model_report():
    metrics_file = os.path.join(REPORT_DIR, "metrics.json")
    if os.path.exists(metrics_file):
        import json
        with open(metrics_file, "r") as f:
            return json.load(f)
    return {"message": "Run python model/evaluate.py to compile report metrics."}


if __name__ == "__main__":
    import uvicorn
    print("Starting AgriSmart AI Server on http://127.0.0.1:8000 ...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
