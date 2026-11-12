"""FastAPI route definitions for CrisisLens AI Engine."""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict

from ai_engine.schemas.internal import AnalyzeRequest, GenerateGraphRequest
from ai_engine.schemas.analysis import Analysis
from ai_engine.schemas.graph import EvidenceGraphResponse
from ai_engine.modules.analyzer import ReportAnalyzer
from ai_engine.modules.graph import EvidenceGraphBuilder, GraphValidationError

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
        stage="Stage 4 - Evidence Graph Generation Active",
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


@router.post(
    "/incidents/{incident_id}/evidence-graph",
    response_model=EvidenceGraphResponse,
    status_code=status.HTTP_200_OK,
    tags=["Evidence Graph"],
    summary="Generate incident evidence relationship graph",
)
def generate_incident_evidence_graph(
    incident_id: str,
    request: GenerateGraphRequest,
) -> EvidenceGraphResponse:
    """Generates an Evidence Relationship Graph for a specific incident.
    
    Adheres strictly to API Contract v1.0 Section 4.8:
    - Node id equals report id
    - Edge directed from later/derived report (source) to earlier/reference report (target)
    - Validates DAG, self-loops, and edge directions using NetworkX
    """
    target_incident_id = incident_id or request.incident_id
    try:
        return EvidenceGraphBuilder.build_graph(
            incident_id=target_incident_id,
            reports=request.reports,
            conflicts=request.conflicts or [],
        )
    except GraphValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": {"code": "validation_error", "message": str(e), "details": None}},
        )


@router.post(
    "/graph/generate",
    response_model=EvidenceGraphResponse,
    status_code=status.HTTP_200_OK,
    tags=["Evidence Graph"],
    summary="Generate evidence relationship graph (RPC style)",
)
def generate_graph_rpc(request: GenerateGraphRequest) -> EvidenceGraphResponse:
    """Generates an Evidence Relationship Graph from a GenerateGraphRequest payload."""
    try:
        return EvidenceGraphBuilder.build_graph(
            incident_id=request.incident_id,
            reports=request.reports,
            conflicts=request.conflicts or [],
        )
    except GraphValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": {"code": "validation_error", "message": str(e), "details": None}},
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
        "graph_url": "/graph/generate",
        "incident_graph_url": "/incidents/{id}/evidence-graph",
        "port": 8001,
    }
