"""CrisisLens Supabase Database Client.

Member 2: Backend, Database and Integration Lead.
Provides a singleton Supabase client for database operations with proper
environment variable validation and server-side service role authentication.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from backend/.env
# Locates backend/.env relative to this file: backend/app/database/../../.env
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Global client cache (singleton)
_supabase_client: Optional[Client] = None
_supabase_anon_client: Optional[Client] = None


def get_config() -> Dict[str, str]:
    """Retrieve and validate Supabase configuration from environment variables.

    Raises:
        ValueError: If SUPABASE_URL or required keys are missing or placeholders.
    """
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    anon_key = os.getenv("SUPABASE_KEY", "").strip()

    # Fallback to anon key if service role key is not yet provided
    active_key = key if key and "your-" not in key else anon_key

    is_placeholder = (
        not url
        or "your-project-id" in url
        or not active_key
        or "your-supabase" in active_key
    )

    if is_placeholder:
        raise ValueError(
            "Supabase credentials are not configured or still contain placeholder values.\n"
            f"Please update {ENV_PATH} with your actual SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."
        )

    return {
        "url": url,
        "service_role_key": key,
        "anon_key": anon_key,
        "active_key": active_key,
    }


def get_supabase_client() -> Client:
    """Return a singleton Supabase client using the service role key for backend operations.

    The service role key bypasses Row Level Security (RLS) and is strictly used
    for internal backend services (API routes, background workers, AI pipelines).
    """
    global _supabase_client
    if _supabase_client is None:
        config = get_config()
        _supabase_client = create_client(config["url"], config["active_key"])
    return _supabase_client


def get_supabase_anon_client() -> Client:
    """Return a Supabase client using the anonymous/public key.

    Useful for testing RLS policies as an unauthenticated or public client.
    """
    global _supabase_anon_client
    if _supabase_anon_client is None:
        config = get_config()
        anon_key = config["anon_key"] or config["active_key"]
        _supabase_anon_client = create_client(config["url"], anon_key)
    return _supabase_anon_client


def test_connection() -> Dict[str, Any]:
    """Test connectivity to the Supabase database.

    Executes a simple query on the 'reports' table to verify network and credentials.
    """
    try:
        client = get_supabase_client()
        # Ping the reports table with a limit 1 read
        response = client.table("reports").select("id").limit(1).execute()
        return {
            "status": "connected",
            "message": "Successfully connected to Supabase PostgreSQL database.",
            "data_count": len(response.data) if response.data else 0,
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": f"Connection failed: {str(exc)}",
        }


def insert_sample_report(
    title: str = "Simulated Flood Inundation - Main Street Underpass",
    content: str = "Water depth observed at 1.2 meters beneath railway bridge. Vehicle traffic obstructed.",
    source_type: str = "iot_sensor",
    location_name: str = "Downtown Underpass #4",
    latitude: float = 12.9716,
    longitude: float = 77.5946,
) -> Dict[str, Any]:
    """Insert a synthetic sample report for testing without real emergency data."""
    client = get_supabase_client()
    sample_payload = {
        "title": title,
        "content": content,
        "source_type": source_type,
        "author_id": "system_test_runner",
        "location_name": location_name,
        "latitude": latitude,
        "longitude": longitude,
        "status": "pending",
        "media_urls": ["https://example.com/synthetic_sensor_telemetry.png"],
        "metadata": {
            "test_run": True,
            "sensor_id": "TEST-SENSOR-001",
            "water_level_cm": 120,
        },
    }
    response = client.table("reports").insert(sample_payload).execute()
    return response.data[0] if response.data else {}


def get_sample_reports(limit: int = 5) -> List[Dict[str, Any]]:
    """Retrieve recent reports from Supabase."""
    client = get_supabase_client()
    response = client.table("reports").select("*").order("created_at", desc=True).limit(limit).execute()
    return response.data or []
