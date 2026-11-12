"""Internal request and service schemas for CrisisLens AI Engine.

These schemas define the payload exchanged between Member 2 (Backend) and Member 3 (AI Engine).
"""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReportInput(BaseModel):
    """Normalized report input schema.
    
    Accepts both flat format (Supabase database row sent by Member 2)
    and nested format (API Contract Report object).
    """
    model_config = ConfigDict(extra="ignore")

    id: str = Field(..., description="Report identifier, e.g. rpt_001")
    text: str = Field(..., min_length=1, description="Emergency report text")
    source_type: str = Field(default="citizen", description="citizen, social_media, news, official, sensor, responder")
    source_name: str = Field(default="Anonymous", description="Reporter name or handle")
    location_label: str = Field(default="Unknown", description="Human-readable location")
    lat: Optional[float] = Field(None, description="Latitude coordinate")
    lng: Optional[float] = Field(None, description="Longitude coordinate")
    reported_at: str = Field(..., description="ISO 8601 UTC timestamp")
    received_at: Optional[str] = Field(None, description="ISO 8601 UTC timestamp")
    forwarded_from: Optional[str] = Field(None, description="Parent report ID if forwarded")
    incident_id: Optional[str] = Field(None, description="Associated incident ID if linked")
    status: Optional[str] = Field(None, description="Report status")
    provenance: Optional[str] = Field(None, description="Verifiable source provenance or credentials if established")

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        
        normalized = dict(data)
        
        # Handle nested source: {"type": ..., "name": ...}
        if "source" in normalized and isinstance(normalized["source"], dict):
            src = normalized["source"]
            if "type" in src and "source_type" not in normalized:
                normalized["source_type"] = src["type"]
            if "name" in src and "source_name" not in normalized:
                normalized["source_name"] = src["name"]

        # Handle nested location: {"lat": ..., "lng": ..., "label": ...}
        if "location" in normalized and isinstance(normalized["location"], dict):
            loc = normalized["location"]
            if "label" in loc and "location_label" not in normalized:
                normalized["location_label"] = loc["label"]
            if "lat" in loc and "lat" not in normalized:
                normalized["lat"] = loc["lat"]
            if "lng" in loc and "lng" not in normalized:
                normalized["lng"] = loc["lng"]

        # Handle location_lat / location_lng aliases if present
        if "location_lat" in normalized and "lat" not in normalized:
            normalized["lat"] = normalized["location_lat"]
        if "location_lng" in normalized and "lng" not in normalized:
            normalized["lng"] = normalized["location_lng"]

        return normalized


class AnalyzeRequest(BaseModel):
    """Payload sent by Member 2 to POST /analyze."""
    model_config = ConfigDict(extra="ignore")

    report: ReportInput = Field(..., description="Target report to analyze")
    context_reports: List[ReportInput] = Field(
        default_factory=list,
        description="List of existing candidate reports to compare against"
    )

