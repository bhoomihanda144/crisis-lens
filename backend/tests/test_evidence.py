"""
Phase 6 Tests: Evidence Relationship Graph & Contract Validation
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_evidence_graph_success():
    response = client.get("/incidents/inc_001/evidence-graph")
    assert response.status_code == 200
    data = response.json()

    assert data["incident_id"] == "inc_001"
    assert "nodes" in data
    assert "edges" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["edges"], list)

    for node in data["nodes"]:
        # Strict contract rule: Node id must equal the report id
        assert node["id"] == node["report_id"]
        assert node["role"] in ["original", "duplicate", "forwarded", "corroborating", "conflicting"]
        assert node["source_type"] in ["citizen", "social_media", "news", "official", "sensor", "responder"]
        assert node["freshness_status"] in ["recent", "aging", "stale"]
        assert "excerpt" in node
        assert "timestamp" in node

    for edge in data["edges"]:
        assert "id" in edge
        assert "source" in edge
        assert "target" in edge
        assert edge["type"] in ["original", "duplicate", "forwarded", "corroborating", "conflicting"]
        assert 0.0 <= edge["confidence"] <= 1.0


def test_get_evidence_graph_not_found():
    response = client.get("/incidents/inc_nonexistent_999/evidence-graph")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "not_found"
    assert "inc_nonexistent_999" in data["error"]["message"]
