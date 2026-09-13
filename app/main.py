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

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from app.modules.rate_limiter import get_rate_limiter, extract_client_ip, RateLimitResult

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
from app.modules.iot_manager import iot_manager

from app.modules.agentic_advisor import run_agent_loop
from app.database import (
    register_user, authenticate_user, save_diagnosis_record, get_diagnosis_history,
    save_crop_recommendation, save_feedback, get_feedback_summary,
    update_user_profile, change_user_password, export_user_data
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


# -------------------------------------------------------------
# TIERED RATE LIMITING MIDDLEWARE (Public & Authenticated)
# -------------------------------------------------------------
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    limiter = get_rate_limiter()
    path = request.url.path
    
    # Exclude non-API paths, static files, openapi documentation
    # Also exclude authentication routes (they are rate-limited with per-account exponential backoff inside route handlers)
    auth_paths = (
        "/api/auth/login",
        "/api/auth/register",
        "/api/user/change-password",
        "/api/auth/reset-password"
    )
    if (
        not path.startswith("/api/")
        or path.startswith("/static")
        or path.startswith("/report-assets")
        or path in auth_paths
        or path.startswith("/docs")
        or path.startswith("/openapi.json")
    ):
        return await call_next(request)
    
    client_ip = extract_client_ip(request.headers, request.client.host if request.client else None)
    
    # Check if request has authenticated user context
    user_id = request.query_params.get("user_id") or request.headers.get("X-User-Id") or request.headers.get("x-user-id")
    
    if user_id:
        res = limiter.check_authenticated_rate_limit(user_id=user_id, ip=client_ip, endpoint=path)
    else:
        res = limiter.check_public_rate_limit(ip=client_ip, endpoint=path)
        
    if not res.allowed:
        return JSONResponse(
            status_code=429,
            content={
                "error": "rate_limit_exceeded",
                "detail": res.detail,
                "retry_after": res.retry_after,
                "limit": res.limit,
                "limit_type": res.limit_type
            },
            headers=res.to_headers()
        )
        
    response = await call_next(request)
    
    # Attach standard rate limit headers
    for k, v in res.to_headers().items():
        response.headers[k] = v
        
    return response

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
def api_register(req: RegisterRequest, request: Request):
    limiter = get_rate_limiter()
    client_ip = extract_client_ip(request.headers, request.client.host if request.client else None)
    
    rate_check = limiter.check_auth_rate_limit(account=req.email_or_phone, ip=client_ip)
    if not rate_check.allowed:
        raise HTTPException(
            status_code=429,
            detail=rate_check.detail,
            headers=rate_check.to_headers()
        )
    
    if len(req.password) < 4:
        limiter.record_auth_result(account=req.email_or_phone, ip=client_ip, success=False)
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
        limiter.record_auth_result(account=req.email_or_phone, ip=client_ip, success=False)
        raise HTTPException(status_code=400, detail=res["error"])
    
    limiter.record_auth_result(account=req.email_or_phone, ip=client_ip, success=True)
    # Attempt background sync to Supabase
    sync_user_to_supabase(res["user"])
    return res


class LoginRequest(BaseModel):
    email_or_phone: str
    password: str


@app.post("/api/auth/login")
def api_login(req: LoginRequest, request: Request):
    limiter = get_rate_limiter()
    client_ip = extract_client_ip(request.headers, request.client.host if request.client else None)
    
    rate_check = limiter.check_auth_rate_limit(account=req.email_or_phone, ip=client_ip)
    if not rate_check.allowed:
        raise HTTPException(
            status_code=429,
            detail=rate_check.detail,
            headers=rate_check.to_headers()
        )
        
    res = authenticate_user(email_or_phone=req.email_or_phone, password=req.password)
    if not res["success"]:
        limiter.record_auth_result(account=req.email_or_phone, ip=client_ip, success=False)
        raise HTTPException(status_code=401, detail=res["error"])
        
    # Reset backoff counters on successful login
    limiter.record_auth_result(account=req.email_or_phone, ip=client_ip, success=True)
    return res


class ResetPasswordRequest(BaseModel):
    email_or_phone: str
    new_password: str


@app.post("/api/auth/reset-password")
def api_reset_password(req: ResetPasswordRequest, request: Request):
    limiter = get_rate_limiter()
    client_ip = extract_client_ip(request.headers, request.client.host if request.client else None)
    
    rate_check = limiter.check_auth_rate_limit(account=req.email_or_phone, ip=client_ip)
    if not rate_check.allowed:
        raise HTTPException(
            status_code=429,
            detail=rate_check.detail,
            headers=rate_check.to_headers()
        )
    
    if len(req.new_password) < 4:
        limiter.record_auth_result(account=req.email_or_phone, ip=client_ip, success=False)
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters.")
        
    from app.database import get_db_connection, hash_password
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email_or_phone = ?", (req.email_or_phone.strip().lower(),))
    user_row = cursor.fetchone()
    if not user_row:
        conn.close()
        limiter.record_auth_result(account=req.email_or_phone, ip=client_ip, success=False)
        raise HTTPException(status_code=404, detail="User account not found.")
        
    user_id = user_row["id"]
    pwd_hash, salt = hash_password(req.new_password)
    cursor.execute("UPDATE users SET password_hash = ?, password_salt = ? WHERE id = ?", (pwd_hash, salt, user_id))
    conn.commit()
    conn.close()
    
    limiter.record_auth_result(account=req.email_or_phone, ip=client_ip, success=True)
    return {"success": True, "message": "Password reset successfully. You may now log in with your new password."}


@app.get("/api/history")
def api_history(user_id: Optional[int] = None):
    return {"history": get_diagnosis_history(user_id=user_id)}


class UpdateProfileRequest(BaseModel):
    user_id: int
    name: str
    location: str = "Gujarat, India"
    village: str = ""
    primary_crop: str = "Tomato"
    farm_size: str = ""
    soil_type: str = "Loamy"
    water_source: str = "Borewell"
    language: str = "en"
    settings_json: str = "{}"


@app.post("/api/user/profile")
def api_update_profile(req: UpdateProfileRequest):
    res = update_user_profile(
        user_id=req.user_id,
        name=req.name,
        location=req.location,
        village=req.village,
        primary_crop=req.primary_crop,
        farm_size=req.farm_size,
        soil_type=req.soil_type,
        water_source=req.water_source,
        language=req.language,
        settings_json=req.settings_json
    )
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Failed to update profile"))
    return res


class ChangePasswordRequest(BaseModel):
    user_id: int
    old_password: str
    new_password: str


@app.post("/api/user/change-password")
def api_change_password(req: ChangePasswordRequest, request: Request):
    limiter = get_rate_limiter()
    client_ip = extract_client_ip(request.headers, request.client.host if request.client else None)
    account_key = f"user_id:{req.user_id}"
    
    rate_check = limiter.check_auth_rate_limit(account=account_key, ip=client_ip)
    if not rate_check.allowed:
        raise HTTPException(
            status_code=429,
            detail=rate_check.detail,
            headers=rate_check.to_headers()
        )
        
    res = change_user_password(
        user_id=req.user_id,
        old_password=req.old_password,
        new_password=req.new_password
    )
    if not res.get("success"):
        limiter.record_auth_result(account=account_key, ip=client_ip, success=False)
        raise HTTPException(status_code=400, detail=res.get("error", "Failed to change password"))
        
    limiter.record_auth_result(account=account_key, ip=client_ip, success=True)
    return res


# -------------------------------------------------------------
# DYNAMIC RATE LIMIT CONFIGURATION (Runtime Configurable)
# -------------------------------------------------------------
class UpdateRateLimitConfigRequest(BaseModel):
    enabled: Optional[bool] = None
    auth_ip_max: Optional[int] = None
    auth_ip_window: Optional[int] = None
    auth_account_threshold: Optional[int] = None
    auth_backoff_base: Optional[float] = None
    auth_backoff_factor: Optional[float] = None
    auth_backoff_max: Optional[float] = None
    public_ip_max: Optional[int] = None
    public_ip_window: Optional[int] = None
    authed_user_max: Optional[int] = None
    authed_user_window: Optional[int] = None


@app.get("/api/system/rate-limit-config")
def api_get_rate_limit_config():
    limiter = get_rate_limiter()
    return {"status": "success", "config": limiter.get_config()}


@app.post("/api/system/rate-limit-config")
def api_update_rate_limit_config(req: UpdateRateLimitConfigRequest):
    limiter = get_rate_limiter()
    data = req.model_dump() if hasattr(req, "model_dump") else req.dict()
    updates = {k: v for k, v in data.items() if v is not None}
    updated = limiter.update_config(updates)
    return {"status": "success", "config": updated}


@app.get("/api/user/export-data")
def api_export_data(user_id: Optional[int] = None):
    return export_user_data(user_id=user_id)


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
# BONUS MODULE F: Real IoT Hardware Telemetry & Actuation
# -------------------------------------------------------------
@app.get("/api/iot/status")
def api_iot_status():
    """Returns real hardware connection status and serial logs."""
    return iot_manager.get_status()


@app.get("/api/iot/telemetry")
def api_iot_telemetry():
    """
    Returns real hardware telemetry frame.
    All sensor values are None / blank when no hardware is connected.
    """
    return iot_manager.get_telemetry_frame()


@app.get("/api/iot/ports")
def api_iot_list_ports():
    """Lists physical USB/Serial COM ports on the system."""
    return {"ports": iot_manager.list_serial_ports()}


class UsbConnectRequest(BaseModel):
    port: str
    baudrate: int = 115200


@app.post("/api/iot/connect-usb")
def api_iot_connect_usb(req: UsbConnectRequest):
    """Connects server to physical USB serial port."""
    return iot_manager.connect_usb(port=req.port, baudrate=req.baudrate)


class WifiConnectRequest(BaseModel):
    endpoint_url: str
    poll_interval: float = 3.0


@app.post("/api/iot/connect-wifi")
def api_iot_connect_wifi(req: WifiConnectRequest):
    """Initiates periodic polling of a Wi-Fi sensor station."""
    return iot_manager.connect_wifi(endpoint_url=req.endpoint_url, poll_interval_sec=req.poll_interval)


@app.post("/api/iot/disconnect")
def api_iot_disconnect():
    """Safely disconnects any active physical link and resets telemetry to blank."""
    return iot_manager.disconnect()


@app.post("/api/iot/ingest")
def api_iot_ingest(payload: Dict[str, Any], connection_type: str = "WIFI"):
    """
    Accepts real sensor telemetry pushed from ESP32/Arduino,
    Web Serial API in browser, or Web Bluetooth.
    """
    return iot_manager.ingest_telemetry(raw_data=payload, connection_type=connection_type)


@app.get("/api/iot/arduino-sketch")
def api_iot_arduino_sketch():
    """Returns ready-to-flash C++ sketch for Arduino Uno and ESP32."""
    return {"sketch": iot_manager.get_arduino_sketch()}


@app.get("/api/system/network-ip")
def api_system_network_ip():
    """
    Return local network IP so external IoT microcontrollers (ESP32/ESP8266/Arduino)
    can push sensor telemetry directly over Wi-Fi without hardcoding 127.0.0.1.
    """
    import socket
    local_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        try:
            local_ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            local_ip = "127.0.0.1"
    return {
        "ip": local_ip,
        "port": 8000,
        "telemetry_url": f"http://{local_ip}:8000/api/iot/ingest"
    }


# -------------------------------------------------------------
# MULTILINGUAL TEXT-TO-SPEECH (TTS) ENDPOINT
# -------------------------------------------------------------
@app.get("/api/tts")
def api_tts(text: str = Query(..., max_length=1000), lang: str = Query("en")):
    """
    Streams natural audio for English, Hindi, Gujarati, and Marathi.
    Uses gTTS with in-memory MP3 buffer for reliable cross-browser speaker playback.
    """
    clean_text = text.strip()
    if not clean_text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    lang_code = lang.lower()
    if lang_code not in ["hi", "gu", "mr", "en"]:
        lang_code = "en"

    try:
        from gtts import gTTS
        import io
        fp = io.BytesIO()
        tts = gTTS(text=clean_text[:400], lang=lang_code, slow=False)
        tts.write_to_fp(fp)
        fp.seek(0)
        return Response(content=fp.getvalue(), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")


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


def _is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(('127.0.0.1', port)) == 0


def _free_port_if_occupied(port: int):
    if not _is_port_in_use(port):
        return
    import subprocess
    import time
    try:
        res = subprocess.run(
            f'powershell -Command "Get-NetTCPConnection -LocalPort {port} -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess"',
            capture_output=True, text=True, shell=True
        )
        pids = [p.strip() for p in res.stdout.strip().split() if p.strip().isdigit()]
        curr_pid = os.getpid()
        for pid in pids:
            if int(pid) != curr_pid:
                subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
        time.sleep(0.8)
    except Exception:
        pass


if __name__ == "__main__":
    import uvicorn
    target_port = 8000
    if _is_port_in_use(target_port):
        print(f"[Port Check] Port {target_port} is busy. Releasing previous instance...")
        _free_port_if_occupied(target_port)

    if _is_port_in_use(target_port):
        target_port = 8001
        print(f"[Port Fallback] Port 8000 still in use. Starting on alternative port: http://127.0.0.1:{target_port}")

    print(f"Starting AgriSmart AI Server on http://127.0.0.1:{target_port} ...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=target_port, reload=False)
