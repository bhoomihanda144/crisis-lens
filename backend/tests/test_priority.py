"""
Phase 6 Tests: Smart Rescue Priority & Contract Validation
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_priority_default_urgency():
    response = client.get("/incidents/priority")
    assert response.status_code == 200
    data = response.json()

    assert data["sort"] == "urgency"
    assert "items" in data
    assert isinstance(data["items"], list)

    if data["items"]:
        first = data["items"][0]
        assert first["rank"] == 1
        assert "incident_id" in first
        assert "title" in first
        assert "location" in first

        # Check separate scores (no blended/combined score)
        assert 0 <= first["urgency"]["score"] <= 100
        assert 0 <= first["evidence_confidence"]["score"] <= 100
        assert 0 <= first["verification_priority"]["score"] <= 100

        # Check human decision requirements
        assert first["requires_human_decision"] is True
        assert first["human_decision"]["status"] == "not_decided"
        assert first["human_decision"]["decided_by"] is None

        # Verify sorted descending by urgency
        for i in range(len(data["items"]) - 1):
            assert data["items"][i]["urgency"]["score"] >= data["items"][i + 1]["urgency"]["score"]


def test_get_priority_sort_verification():
    response = client.get("/incidents/priority?sort=verification")
    assert response.status_code == 200
    data = response.json()

    assert data["sort"] == "verification"
    assert "items" in data

    if len(data["items"]) >= 2:
        # Verify sorted descending by verification priority
        for i in range(len(data["items"]) - 1):
            assert data["items"][i]["verification_priority"]["score"] >= data["items"][i + 1]["verification_priority"]["score"]


def test_get_priority_invalid_sort():
    response = client.get("/incidents/priority?sort=invalid_sort")
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "validation_error"
