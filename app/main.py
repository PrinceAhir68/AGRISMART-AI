"""
AgriSmart AI - FastAPI Application Backend
SIH-2026 Problem Statement 1: Core Vision Detection, Bonus Modules (A - G),
Authentication, SQLite Database, and Supabase Integration.
"""

import os
import sys
import json
import shutil
import tempfile
import httpx
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

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware

# Import core and bonus modules
from model.predict import predict, InvalidPlantImageError
from app.modules.crop_recommender import recommend_crops, INDIAN_DISTRICTS
from app.modules.smart_irrigation import calculate_smart_irrigation
from app.modules.weather_service import get_weather_intelligence
from app.modules.sustainability import calculate_sustainability_score
from app.modules.farmer_assistant import ask_farmer_assistant
from app.modules.qa_engine import get_qa_engine
from app.modules.web_verifier import verify_disease_with_web, verify_and_answer_qa_with_web
from app.modules.iot_simulator import get_current_iot_telemetry, trigger_iot_scenario
from app.modules.agentic_advisor import run_agent_loop
from app.database import (
    register_user, authenticate_user, save_diagnosis_record, get_diagnosis_history,
    save_crop_recommendation, save_feedback, get_feedback_summary
)
from app.supabase_client import (
    get_supabase_status, sync_user_to_supabase, sync_diagnosis_to_supabase
)

app = FastAPI(
    title="AgriSmart AI API",
    description="SIH-2026 Internal Hackathon - Problem Statement 1 (AgriSmart AI)",
    version="2.0.0"
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
# USER AUTHENTICATION & DATABASE (Email/Phone + Password)
# -------------------------------------------------------------
class RegisterRequest(BaseModel):
    name: str
    email_or_phone: str
    password: str
    location: str = "Gujarat, India"
    primary_crop: str = "Tomato"
    language: str = "en"


@app.post("/api/auth/register")
def api_register(req: RegisterRequest):
    if len(req.password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters.")
    res = register_user(
        name=req.name,
        email_or_phone=req.email_or_phone,
        password=req.password,
        location=req.location,
        primary_crop=req.primary_crop,
        language=req.language
    )
    if not res["success"]:
        raise HTTPException(status_code=400, detail=res["error"])
    
    # Attempt background sync to Supabase
    sync_user_to_supabase(res["user"])
    return res


class LoginRequest(BaseModel):
    email_or_phone: str
    password: str


@app.post("/api/auth/login")
def api_login(req: LoginRequest):
    res = authenticate_user(email_or_phone=req.email_or_phone, password=req.password)
    if not res["success"]:
        raise HTTPException(status_code=401, detail=res["error"])
    return res


@app.get("/api/history")
def api_history(user_id: Optional[int] = None):
    return {"history": get_diagnosis_history(user_id=user_id)}


@app.get("/api/supabase/status")
def api_supabase_status():
    return get_supabase_status()


# -------------------------------------------------------------
# CORE TASK: Leaf Disease Detection (Computer Vision)
# -------------------------------------------------------------
@app.post("/api/predict")
async def predict_disease(
    file: UploadFile = File(...),
    user_id: Optional[int] = Form(None),
    target_crop: Optional[str] = Form(None),
    current_weather: Optional[str] = Form(None)
):
    """
    Mandatory Core Task Endpoint:
    Accepts an uploaded plant leaf image and outputs predicted class, confidence,
    symptoms, immediate cultural precautions, organic remedies, and chemical controls.
    Performs Live Internet Cross-Verification & Comparison against ICAR/FAO databases.
    Automatically saves record to SQLite database and syncs to Supabase.
    """
    tmp_path = None
    try:
        suffix = os.path.splitext(file.filename)[1] or ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        weather_dict = None
        if current_weather:
            try:
                weather_dict = json.loads(current_weather) if isinstance(current_weather, str) else current_weather
            except Exception:
                pass

        result = predict(tmp_path, target_crop=target_crop, current_weather=weather_dict)

        # Save to SQLite database
        rec_id = save_diagnosis_record(
            crop=result["crop"],
            disease=result["display_name"],
            class_label=result["class_label"],
            confidence=result["confidence"],
            is_disease=result["is_disease"],
            precautions=result["precautions"],
            treatment=result["chemical_treatment"] or result["organic_treatment"],
            user_id=user_id,
            image_name=file.filename
        )
        result["record_id"] = rec_id

        # Sync to Supabase if configured
        sync_diagnosis_to_supabase({
            "user_id": user_id,
            "crop": result["crop"],
            "disease": result["display_name"],
            "class_label": result["class_label"],
            "confidence": result["confidence"],
            "is_disease": result["is_disease"],
            "symptoms": result["symptoms"],
            "treatment": result["chemical_treatment"],
            "image_url": file.filename
        })

        return result
    except InvalidPlantImageError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "NOT_A_PLANT_IMAGE",
                "message": str(e),
                "user_guidance": "The uploaded photo is not recognized as a plant leaf, crop, tree, fruit, or vegetable. Please upload a clear photo of an agricultural crop, leaf, or plant part."
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


# -------------------------------------------------------------
# MULTILINGUAL TTS AUDIO PROXY (Hindi, Gujarati, Marathi, English)
# -------------------------------------------------------------
_TTS_CACHE: Dict[str, bytes] = {}

@app.get("/api/tts")
async def api_text_to_speech(text: str = Query(...), lang: str = Query("en")):
    """
    Multilingual audio streaming proxy for Indian languages (Hindi, Gujarati, Marathi)
    and English, solving lack of local Indian voice packs on Windows OS.
    """
    clean_text = text.strip()[:250]
    if not clean_text:
        raise HTTPException(status_code=400, detail="Text parameter cannot be empty.")

    cache_key = f"{lang}:{clean_text}"
    if cache_key in _TTS_CACHE:
        return Response(content=_TTS_CACHE[cache_key], media_type="audio/mpeg")

    url = "https://translate.google.com/translate_tts"
    params = {
        "ie": "UTF-8",
        "tl": lang,
        "client": "tw-ob",
        "q": clean_text
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(url, params=params, headers=headers)
            if resp.status_code == 200 and len(resp.content) > 100:
                if len(_TTS_CACHE) > 300:
                    _TTS_CACHE.clear()
                _TTS_CACHE[cache_key] = resp.content
                return Response(content=resp.content, media_type="audio/mpeg")
    except Exception as e:
        print(f"TTS Streaming warning: {e}")

    raise HTTPException(status_code=502, detail="Audio voice generation temporarily unavailable.")


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
# CROP RECOMMENDATION & SOIL HEALTH
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
    state: Optional[str] = "Gujarat"
    district: Optional[str] = "Ahmedabad"
    user_id: Optional[int] = None


@app.post("/api/crop-recommendation")
def api_crop_recommendation(req: CropRecRequest):
    loc = f"{req.district}, {req.state}" if req.district and req.state else req.location
    res = recommend_crops(
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
        location=loc
    )
    # Save recommendation to database for learning
    rec_id = save_crop_recommendation(
        user_id=req.user_id,
        state=req.state or "Gujarat",
        district=req.district or "Ahmedabad",
        soil_type=req.soil_type,
        ph=req.ph,
        n=req.n,
        p=req.p,
        k=req.k,
        season=req.season,
        rainfall=req.rainfall,
        temperature=req.temperature,
        top_crops=res.get("recommendations", [])
    )
    res["record_id"] = rec_id
    return res


@app.get("/api/districts")
def api_districts():
    """Returns directory of supported agricultural states and districts."""
    return {"districts": INDIAN_DISTRICTS}


# -------------------------------------------------------------
# FARMER FEEDBACK LOOP (Continuous Model Improvement)
# -------------------------------------------------------------
class FeedbackRequest(BaseModel):
    item_type: str  # 'diagnosis' or 'crop_recommendation'
    item_id: Optional[int] = None
    helpful: bool
    comments: Optional[str] = ""
    user_id: Optional[int] = None


@app.post("/api/feedback")
def api_feedback(req: FeedbackRequest):
    fb_id = save_feedback(
        item_type=req.item_type,
        item_id=req.item_id,
        helpful=req.helpful,
        comments=req.comments or "",
        user_id=req.user_id
    )
    return {
        "status": "success",
        "feedback_id": fb_id,
        "message": "Thank you for your feedback! This data helps continuously improve AgriSmart AI models.",
        "summary": get_feedback_summary()
    }


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
# BONUS MODULE C: Weather-Based Intelligence (Real-Time GPS Location)
# -------------------------------------------------------------
@app.get("/api/weather")
def api_weather(
    lat: float = Query(23.0225, description="Latitude from GPS"),
    lon: float = Query(72.5714, description="Longitude from GPS"),
    name: str = Query("Ahmedabad, Gujarat", description="Location name or city")
):
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
    language: str = "en"


@app.post("/api/assistant")
def api_assistant(req: AssistantRequest):
    return ask_farmer_assistant(query=req.query, language=req.language)


@app.get("/api/qa/search")
def api_qa_search(q: str = Query(..., min_length=2), lang: str = Query("en")):
    """
    10,000+ Agricultural Q&A Knowledge Engine Search Endpoint.
    Searches 10,800 agronomy knowledge nodes across 50 crops and 12 agronomic domains.
    """
    engine = get_qa_engine()
    results = engine.search(q, top_k=5)
    return {
        "status": "success",
        "query": q,
        "language": lang,
        "total_matches": len(results),
        "results": results
    }


# -------------------------------------------------------------
# BONUS MODULE F: IoT Telemetry Feed & Scenarios
# -------------------------------------------------------------
@app.get("/api/iot/telemetry")
def api_iot_telemetry():
    return get_current_iot_telemetry()


class ScenarioRequest(BaseModel):
    scenario: str


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
