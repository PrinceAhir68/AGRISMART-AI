"""
AgriSmart AI - Database Abstraction Layer (SQLite & Supabase Sync)
SIH-2026 Problem Statement 1
Stores:
  - Users (Email or Phone + Hashed Password + Location + Language)
  - Crop Disease Diagnostic History
  - Farm IoT Telemetry & Irrigation Records
"""

import os
import sqlite3
import hashlib
import secrets
import datetime
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "agrismart.db")


def get_db_connection():
    """Returns a SQLite connection with dict-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Creates the SQLite database schema if not exists."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users table (Email or Phone authentication)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email_or_phone TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        password_salt TEXT NOT NULL,
        location TEXT DEFAULT 'Ahmedabad, Gujarat',
        primary_crop TEXT DEFAULT 'Tomato',
        language TEXT DEFAULT 'en',
        created_at TEXT NOT NULL
    )
    """)

    # 2. Diagnoses history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS diagnoses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        image_name TEXT,
        crop TEXT NOT NULL,
        disease TEXT NOT NULL,
        class_label TEXT NOT NULL,
        confidence REAL NOT NULL,
        is_disease BOOLEAN NOT NULL,
        precautions TEXT,
        treatment TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # 3. Farm telemetry & irrigation audit table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS farm_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        soil_moisture REAL,
        temperature REAL,
        humidity REAL,
        soil_ph REAL,
        decision TEXT,
        water_saved_liters REAL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # 4. Crop recommendations audit table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crop_recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        state TEXT,
        district TEXT,
        soil_type TEXT,
        ph REAL,
        n REAL,
        p REAL,
        k REAL,
        season TEXT,
        rainfall REAL,
        temperature REAL,
        top_crops TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # 5. Farmer feedback & continuous model improvement table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        item_type TEXT NOT NULL,
        item_id INTEGER,
        helpful BOOLEAN NOT NULL,
        comments TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


def hash_password(password: str, salt: Optional[str] = None):
    """Secure password hashing using PBKDF2-HMAC-SHA256."""
    if not salt:
        salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()
    return pwd_hash, salt


def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    """Verifies a password against the stored salt and hash."""
    pwd_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(pwd_hash, expected_hash)


def register_user(
    name: str,
    email_or_phone: str,
    password: str,
    location: str = "Gujarat, India",
    primary_crop: str = "Tomato",
    language: str = "en"
) -> Dict[str, Any]:
    """Registers a new farmer user account."""
    conn = get_db_connection()
    cursor = conn.cursor()

    email_or_phone = email_or_phone.strip().lower()
    
    # Check if already exists
    cursor.execute("SELECT id FROM users WHERE email_or_phone = ?", (email_or_phone,))
    if cursor.fetchone():
        conn.close()
        return {"success": False, "error": "An account with this Email or Phone Number already exists."}

    pwd_hash, salt = hash_password(password)
    created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    cursor.execute("""
    INSERT INTO users (name, email_or_phone, password_hash, password_salt, location, primary_crop, language, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, email_or_phone, pwd_hash, salt, location, primary_crop, language, created_at))

    user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "success": True,
        "user": {
            "id": user_id,
            "name": name,
            "email_or_phone": email_or_phone,
            "location": location,
            "primary_crop": primary_crop,
            "language": language
        }
    }


def authenticate_user(email_or_phone: str, password: str) -> Dict[str, Any]:
    """Authenticates a user with Email or Phone + Password."""
    conn = get_db_connection()
    cursor = conn.cursor()

    email_or_phone = email_or_phone.strip().lower()
    cursor.execute("SELECT * FROM users WHERE email_or_phone = ?", (email_or_phone,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"success": False, "error": "Account not found. Please check your email or phone number, or register."}

    if not verify_password(password, row["password_salt"], row["password_hash"]):
        return {"success": False, "error": "Incorrect password. Please try again."}

    return {
        "success": True,
        "user": {
            "id": row["id"],
            "name": row["name"],
            "email_or_phone": row["email_or_phone"],
            "location": row["location"],
            "primary_crop": row["primary_crop"],
            "language": row["language"]
        }
    }


def save_diagnosis_record(
    crop: str,
    disease: str,
    class_label: str,
    confidence: float,
    is_disease: bool,
    precautions: List[str],
    treatment: str,
    user_id: Optional[int] = None,
    image_name: str = "leaf_upload.jpg"
) -> int:
    """Saves a leaf diagnosis to history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    precautions_str = "\n".join(precautions) if isinstance(precautions, list) else str(precautions)

    cursor.execute("""
    INSERT INTO diagnoses (user_id, image_name, crop, disease, class_label, confidence, is_disease, precautions, treatment, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, image_name, crop, disease, class_label, confidence, is_disease, precautions_str, treatment, created_at))

    rec_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rec_id


def get_diagnosis_history(user_id: Optional[int] = None, limit: int = 15) -> List[Dict[str, Any]]:
    """Retrieves recent diagnostic records."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if user_id:
        cursor.execute("SELECT * FROM diagnoses WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit))
    else:
        cursor.execute("SELECT * FROM diagnoses ORDER BY id DESC LIMIT ?", (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": r["id"],
            "crop": r["crop"],
            "disease": r["disease"],
            "confidence": round(r["confidence"] * 100, 1),
            "is_disease": bool(r["is_disease"]),
            "treatment": r["treatment"],
            "created_at": r["created_at"]
        }
        for r in rows
    ]


def save_crop_recommendation(
    user_id: Optional[int],
    state: str,
    district: str,
    soil_type: str,
    ph: float,
    n: float,
    p: float,
    k: float,
    season: str,
    rainfall: float,
    temperature: float,
    top_crops: List[Dict[str, Any]]
) -> int:
    """Saves a crop recommendation query and recommendations to database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    import json
    top_crops_json = json.dumps([c.get("crop", "") for c in top_crops])

    cursor.execute("""
    INSERT INTO crop_recommendations (user_id, state, district, soil_type, ph, n, p, k, season, rainfall, temperature, top_crops, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, state, district, soil_type, ph, n, p, k, season, rainfall, temperature, top_crops_json, created_at))

    rec_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rec_id


def save_feedback(
    item_type: str,
    item_id: Optional[int],
    helpful: bool,
    comments: str = "",
    user_id: Optional[int] = None
) -> int:
    """Saves farmer rating and feedback for continuous model improvement."""
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    cursor.execute("""
    INSERT INTO feedback (user_id, item_type, item_id, helpful, comments, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, item_type, item_id, 1 if helpful else 0, comments, created_at))

    fb_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return fb_id


def get_feedback_summary() -> Dict[str, Any]:
    """Returns feedback statistics."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total, SUM(helpful) as helpful_count FROM feedback")
    row = cursor.fetchone()
    conn.close()
    total = row["total"] or 0
    helpful = row["helpful_count"] or 0
    return {
        "total_feedback": total,
        "helpful_feedback": helpful,
        "accuracy_perception_pct": round((helpful / total * 100), 1) if total > 0 else 100.0
    }


# Initialize on import
init_database()

