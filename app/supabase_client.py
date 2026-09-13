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

def get_supabase_url() -> str:
    return os.environ.get("SUPABASE_URL", "").strip()


def get_supabase_key() -> str:
    return os.environ.get("SUPABASE_KEY", "").strip()


# Module-level aliases for backward compatibility
SUPABASE_URL = get_supabase_url()
SUPABASE_KEY = get_supabase_key()


def is_supabase_configured() -> bool:
    """Checks if valid Supabase connection credentials exist."""
    url = get_supabase_url()
    key = get_supabase_key()
    return bool(url and key and "supabase.co" in url)


def sync_user_to_supabase(user_data: Dict[str, Any]) -> bool:
    """Synchronizes a registered user to the Supabase 'users' table."""
    if not is_supabase_configured():
        return False

    url = f"{get_supabase_url().rstrip('/')}/rest/v1/users"
    headers = {
        "apikey": get_supabase_key(),
        "Authorization": f"Bearer {get_supabase_key()}",
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

    url = f"{get_supabase_url().rstrip('/')}/rest/v1/diagnoses"
    headers = {
        "apikey": get_supabase_key(),
        "Authorization": f"Bearer {get_supabase_key()}",
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
        "url": get_supabase_url() if configured else "Not Set",
        "status": "Connected to Supabase Cloud" if configured else "Local SQLite Active (Ready for Supabase)",
        "setup_guide": "Add SUPABASE_URL and SUPABASE_KEY in your .env file or environment variables to enable cloud sync."
    }
