"""
Phase 7 Tests: What-If Simulation & Contract Validation
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_simulation_success():
    payload = {
        "scenario_name": "Heavy rain, 3 roads blocked",
        "affected_population": 12000,
        "disaster_severity": 4,
        "rescue_teams": 6,
        "blocked_roads": 3,
        "available_ambulances": 5
    }
    response = client.post("/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Verify root fields
    assert data["scenario_id"].startswith("sim_")
    assert data["is_simulation"] is True
    assert "generated_at" in data

    # Verify echoed inputs
    assert data["inputs"]["scenario_name"] == payload["scenario_name"]
    assert data["inputs"]["affected_population"] == 12000
    assert data["inputs"]["disaster_severity"] == 4
    assert data["inputs"]["rescue_teams"] == 6

    # Verify results
    results = data["results"]
    assert "resource_demand" in results
    assert "shortages" in results
    assert "estimated_response_delay_minutes" in results
    assert "priority_changes" in results
    assert "summary" in results

    assert isinstance(results["resource_demand"]["rescue_teams"], int)
    assert isinstance(results["resource_demand"]["ambulances"], int)
    assert isinstance(results["estimated_response_delay_minutes"], int)


def test_simulation_invalid_severity():
    # Severity must be between 1 and 5
    invalid_payload = {
        "scenario_name": "Severe earthquake",
        "affected_population": 5000,
        "disaster_severity": 10,  # Invalid
        "rescue_teams": 4,
        "blocked_roads": 2,
        "available_ambulances": 3
    }
    response = client.post("/simulate", json=invalid_payload)
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "validation_error"


def test_simulation_negative_numbers():
    invalid_payload = {
        "scenario_name": "Invalid negative input",
        "affected_population": -100,  # Invalid
        "disaster_severity": 3,
        "rescue_teams": 2,
        "blocked_roads": 0,
        "available_ambulances": 1
    }
    response = client.post("/simulate", json=invalid_payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "validation_error"
