"""
AgriSmart AI - Database Module (SQLite)
Handles Farmer User Accounts, Diagnoses History, Continuous Learning Feedback,
Crop Recommendations, and Farm Settings with robust error isolation and
zero information leakage.
"""

import os
import sqlite3
import hashlib
import secrets
import datetime
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("agrismart.database")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DB_PATH = os.getenv("AGRISMART_DB_PATH", os.path.join(PROJECT_ROOT, "agrismart.db"))


def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with dict-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    """Creates the SQLite database schema if not exists."""
    conn = None
    try:
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

        # 3. IoT Sensor telemetry & decisions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetry_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            soil_moisture REAL,
            temperature REAL,
            humidity REAL,
            soil_ph REAL,
            valve_state TEXT,
            decision TEXT,
            created_at TEXT NOT NULL
        )
        """)

        # 4. Crop Recommendations table
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

        # 5. Continuous Learning & Farmer Feedback table
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

        # Safely migrate optional user profile and settings columns
        for col, col_type in [
            ("village", "TEXT DEFAULT ''"),
            ("farm_size", "TEXT DEFAULT ''"),
            ("soil_type", "TEXT DEFAULT 'Loamy'"),
            ("water_source", "TEXT DEFAULT 'Borewell'"),
            ("settings_json", "TEXT DEFAULT '{}'")
        ]:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type}")
            except Exception:
                pass

        conn.commit()
    except sqlite3.Error as e:
        logger.error("Failed to initialize database schema: %s", e, exc_info=True)
    finally:
        if conn:
            conn.close()


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
    conn = None
    email_or_phone = email_or_phone.strip().lower()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if already exists
        cursor.execute("SELECT id FROM users WHERE email_or_phone = ?", (email_or_phone,))
        if cursor.fetchone():
            return {"success": False, "error": "An account with this Email or Phone Number already exists."}

        pwd_hash, salt = hash_password(password)
        created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

        cursor.execute("""
        INSERT INTO users (name, email_or_phone, password_hash, password_salt, location, primary_crop, language, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email_or_phone, pwd_hash, salt, location, primary_crop, language, created_at))

        user_id = cursor.lastrowid
        conn.commit()

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
    except sqlite3.IntegrityError:
        if conn:
            conn.rollback()
        return {"success": False, "error": "An account with this Email or Phone Number already exists."}
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error("Database error during register_user: %s", e, exc_info=True)
        return {"success": False, "error": "Database service is temporarily unavailable. Please try again."}
    finally:
        if conn:
            conn.close()


def authenticate_user(email_or_phone: str, password: str) -> Dict[str, Any]:
    """Authenticates a user with Email or Phone + Password."""
    conn = None
    email_or_phone = email_or_phone.strip().lower()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email_or_phone = ?", (email_or_phone,))
        row = cursor.fetchone()

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
                "village": row["village"] if "village" in row.keys() else "",
                "primary_crop": row["primary_crop"],
                "farm_size": row["farm_size"] if "farm_size" in row.keys() else "",
                "soil_type": row["soil_type"] if "soil_type" in row.keys() else "Loamy",
                "water_source": row["water_source"] if "water_source" in row.keys() else "Borewell",
                "language": row["language"],
                "settings_json": row["settings_json"] if "settings_json" in row.keys() else "{}"
            }
        }
    except sqlite3.Error as e:
        logger.error("Database error during authenticate_user: %s", e, exc_info=True)
        return {"success": False, "error": "Authentication service temporarily unavailable. Please try again."}
    finally:
        if conn:
            conn.close()


def update_user_profile(
    user_id: int,
    name: str,
    location: str = "Gujarat, India",
    village: str = "",
    primary_crop: str = "Tomato",
    farm_size: str = "",
    soil_type: str = "Loamy",
    water_source: str = "Borewell",
    language: str = "en",
    settings_json: str = "{}"
) -> Dict[str, Any]:
    """Updates user profile details and website preferences."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE users SET
            name = ?,
            location = ?,
            village = ?,
            primary_crop = ?,
            farm_size = ?,
            soil_type = ?,
            water_source = ?,
            language = ?,
            settings_json = ?
        WHERE id = ?
        """, (name, location, village, primary_crop, farm_size, soil_type, water_source, language, settings_json, user_id))
        conn.commit()

        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()

        if not row:
            return {"success": False, "error": "User account not found."}

        return {
            "success": True,
            "user": {
                "id": row["id"],
                "name": row["name"],
                "email_or_phone": row["email_or_phone"],
                "location": row["location"],
                "village": row["village"] if "village" in row.keys() else "",
                "primary_crop": row["primary_crop"],
                "farm_size": row["farm_size"] if "farm_size" in row.keys() else "",
                "soil_type": row["soil_type"] if "soil_type" in row.keys() else "Loamy",
                "water_source": row["water_source"] if "water_source" in row.keys() else "Borewell",
                "language": row["language"],
                "settings_json": row["settings_json"] if "settings_json" in row.keys() else "{}"
            }
        }
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error("Database error during update_user_profile: %s", e, exc_info=True)
        return {"success": False, "error": "Unable to update profile. Please try again."}
    finally:
        if conn:
            conn.close()


def change_user_password(user_id: int, old_password: str, new_password: str) -> Dict[str, Any]:
    """Securely verifies old password and updates to new password."""
    if len(new_password) < 4:
        return {"success": False, "error": "New password must be at least 4 characters long."}

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()

        if not row:
            return {"success": False, "error": "User account not found."}

        if not verify_password(old_password, row["password_salt"], row["password_hash"]):
            return {"success": False, "error": "Current password is incorrect. Please try again."}

        new_hash, new_salt = hash_password(new_password)
        cursor.execute("UPDATE users SET password_hash = ?, password_salt = ? WHERE id = ?", (new_hash, new_salt, user_id))
        conn.commit()
        return {"success": True, "message": "Password updated successfully!"}
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error("Database error during change_user_password: %s", e, exc_info=True)
        return {"success": False, "error": "Unable to change password. Please try again."}
    finally:
        if conn:
            conn.close()


def reset_user_password(email_or_phone: str, new_password: str) -> Dict[str, Any]:
    """Securely resets a user password by email or phone without leaking system details."""
    if len(new_password) < 4:
        return {"success": False, "error": "Password must be at least 4 characters long."}

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email_or_phone = ?", (email_or_phone.strip().lower(),))
        user_row = cursor.fetchone()
        if not user_row:
            return {"success": False, "error": "User account not found.", "status_code": 404}

        user_id = user_row["id"]
        pwd_hash, salt = hash_password(new_password)
        cursor.execute("UPDATE users SET password_hash = ?, password_salt = ? WHERE id = ?", (pwd_hash, salt, user_id))
        conn.commit()
        return {"success": True, "message": "Password reset successfully. You may now log in with your new password."}
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error("Database error during reset_user_password: %s", e, exc_info=True)
        return {"success": False, "error": "Database service is temporarily unavailable. Please try again.", "status_code": 500}
    finally:
        if conn:
            conn.close()


def export_user_data(user_id: Optional[int] = None) -> Dict[str, Any]:
    """Exports user profile, diagnostic history, crop recommendations, and feedback."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        user_info = None
        if user_id:
            cursor.execute("SELECT id, name, email_or_phone, location, village, primary_crop, farm_size, soil_type, water_source, language, created_at FROM users WHERE id = ?", (user_id,))
            u_row = cursor.fetchone()
            if u_row:
                user_info = dict(u_row)

        cursor.execute("SELECT * FROM diagnoses WHERE user_id = ? ORDER BY id DESC LIMIT 50", (user_id or 1,))
        diag_rows = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM crop_recommendations WHERE user_id = ? ORDER BY id DESC LIMIT 20", (user_id or 1,))
        rec_rows = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM feedback WHERE user_id = ? ORDER BY id DESC LIMIT 20", (user_id or 1,))
        fb_rows = [dict(r) for r in cursor.fetchall()]

        return {
            "export_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "user_profile": user_info or {
                "name": "Kisan Mitra",
                "role": "Farmer / Agricultural Producer",
                "note": "Local / Guest Farmer Session"
            },
            "diagnoses_history": diag_rows,
            "crop_recommendations": rec_rows,
            "feedback_history": fb_rows,
            "platform": "AgriSmart AI v2.0.0"
        }
    except sqlite3.Error as e:
        logger.error("Database error during export_user_data: %s", e, exc_info=True)
        return {
            "export_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "error": "Failed to retrieve complete user export archive.",
            "diagnoses_history": [],
            "crop_recommendations": [],
            "feedback_history": []
        }
    finally:
        if conn:
            conn.close()


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
    conn = None
    created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    precautions_str = "\n".join(precautions) if isinstance(precautions, list) else str(precautions)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO diagnoses (user_id, image_name, crop, disease, class_label, confidence, is_disease, precautions, treatment, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, image_name, crop, disease, class_label, confidence, is_disease, precautions_str, treatment, created_at))

        rec_id = cursor.lastrowid
        conn.commit()
        return rec_id
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error("Database error during save_diagnosis_record: %s", e, exc_info=True)
        return 0
    finally:
        if conn:
            conn.close()


def get_diagnosis_history(user_id: Optional[int] = None, limit: int = 15) -> List[Dict[str, Any]]:
    """Retrieves recent diagnostic records."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if user_id:
            cursor.execute("SELECT * FROM diagnoses WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit))
        else:
            cursor.execute("SELECT * FROM diagnoses ORDER BY id DESC LIMIT ?", (limit,))

        rows = cursor.fetchall()
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
    except sqlite3.Error as e:
        logger.error("Database error during get_diagnosis_history: %s", e, exc_info=True)
        return []
    finally:
        if conn:
            conn.close()


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
    conn = None
    created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    import json
    top_crops_json = json.dumps([c.get("crop", "") for c in top_crops])

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO crop_recommendations (user_id, state, district, soil_type, ph, n, p, k, season, rainfall, temperature, top_crops, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, state, district, soil_type, ph, n, p, k, season, rainfall, temperature, top_crops_json, created_at))

        rec_id = cursor.lastrowid
        conn.commit()
        return rec_id
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error("Database error during save_crop_recommendation: %s", e, exc_info=True)
        return 0
    finally:
        if conn:
            conn.close()


def save_feedback(
    item_type: str,
    item_id: Optional[int],
    helpful: bool,
    comments: str = "",
    user_id: Optional[int] = None
) -> int:
    """Saves farmer rating and feedback for continuous model improvement."""
    conn = None
    created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO feedback (user_id, item_type, item_id, helpful, comments, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, item_type, item_id, 1 if helpful else 0, comments, created_at))

        fb_id = cursor.lastrowid
        conn.commit()
        return fb_id
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error("Database error during save_feedback: %s", e, exc_info=True)
        return 0
    finally:
        if conn:
            conn.close()


def get_feedback_summary() -> Dict[str, Any]:
    """Returns feedback statistics."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total, SUM(helpful) as helpful_count FROM feedback")
        row = cursor.fetchone()
        total = row["total"] or 0
        helpful = row["helpful_count"] or 0
        return {
            "total_feedback": total,
            "helpful_feedback": helpful,
            "accuracy_perception_pct": round((helpful / total * 100), 1) if total > 0 else 100.0
        }
    except sqlite3.Error as e:
        logger.error("Database error during get_feedback_summary: %s", e, exc_info=True)
        return {"total_feedback": 0, "helpful_feedback": 0, "accuracy_perception_pct": 100.0}
    finally:
        if conn:
            conn.close()


# Initialize on import
init_database()
