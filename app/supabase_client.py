"""
AgriSmart AI - Supabase Cloud Synchronization Client
SIH-2026 Problem Statement 1
Enables connecting AgriSmart AI to Supabase Cloud PostgreSQL.
Syncs users, disease diagnoses, and IoT sensor streams.
"""

import os
import requests
import json
from typing import Dict, Any, Optional

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")


def is_supabase_configured() -> bool:
    """Checks if valid Supabase connection credentials exist."""
    return bool(SUPABASE_URL and SUPABASE_KEY and "supabase.co" in SUPABASE_URL)


def sync_user_to_supabase(user_data: Dict[str, Any]) -> bool:
    """Synchronizes a registered user to the Supabase 'users' table."""
    if not is_supabase_configured():
        return False

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/users"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    payload = {
        "name": user_data.get("name"),
        "email_or_phone": user_data.get("email_or_phone"),
        "location": user_data.get("location"),
        "primary_crop": user_data.get("primary_crop"),
        "language": user_data.get("language")
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=4)
        return resp.status_code in [200, 201]
    except Exception as e:
        print(f"Supabase user sync error: {e}")
        return False


def sync_diagnosis_to_supabase(diag_data: Dict[str, Any]) -> bool:
    """Synchronizes a disease diagnosis to the Supabase 'diagnoses' table."""
    if not is_supabase_configured():
        return False

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/diagnoses"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(url, headers=headers, json=diag_data, timeout=4)
        return resp.status_code in [200, 201]
    except Exception as e:
        print(f"Supabase diagnosis sync error: {e}")
        return False


def get_supabase_status() -> Dict[str, Any]:
    """Returns the current connection state of Supabase."""
    configured = is_supabase_configured()
    return {
        "configured": configured,
        "url": SUPABASE_URL if configured else "Not Set",
        "status": "Connected to Supabase Cloud" if configured else "Local SQLite Active (Ready for Supabase)",
        "setup_guide": "Add SUPABASE_URL and SUPABASE_KEY in your .env file or environment variables to enable cloud sync."
    }
