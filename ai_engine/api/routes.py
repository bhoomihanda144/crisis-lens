"""FastAPI route definitions for CrisisLens AI Engine."""

from typing import Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

from ai_engine.schemas.internal import AnalyzeRequest
from ai_engine.schemas.analysis import Analysis
from ai_engine.modules.analyzer import ReportAnalyzer

router = APIRouter()


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    service: str
    version: str
    port: int
    stage: str


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def get_health() -> HealthResponse:
    """Health check endpoint to verify AI engine status and connectivity."""
    return HealthResponse(
        status="healthy",
        service="crisis-lens-ai-engine",
        version="0.1.0",
        port=8001,
        stage="Stage 3 - Core Intelligence Active",
    )


@router.post("/analyze", response_model=Analysis, tags=["Analysis"])
def analyze_report_endpoint(request: AnalyzeRequest) -> Analysis:
    """Analyzes an emergency report in context of existing reports.
    
    Produces full contract-compliant Analysis object including duplicate detection,
    source independence, freshness calculation, conflicts, and 3-dimensional scores.
    """
    return ReportAnalyzer.analyze(
        report=request.report,
        context_reports=request.context_reports,
    )


@router.get("/", tags=["Root"])
def get_root() -> Dict[str, Any]:
    """Root metadata endpoint."""
    return {
        "service": "CrisisLens AI Engine Microservice",
        "version": "0.1.0",
        "docs_url": "/docs",
        "health_url": "/health",
        "analyze_url": "/analyze",
        "port": 8001,
    }
