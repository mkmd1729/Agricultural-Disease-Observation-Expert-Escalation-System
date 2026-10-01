"""
Integration tests for FastAPI REST endpoints using TestClient.
"""

import sys
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import init_db

init_db()
client = TestClient(app)


def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "agri-disease-observation"


def test_create_case_json():
    payload = {
        "crop": "Tomato",
        "variety": "Arka Rakshak",
        "location": "North Sub-district",
        "latitude": 12.345,
        "longitude": 76.543,
        "crop_stage": "Flowering",
        "symptoms": ["leaf_spots", "yellowing_chlorosis"],
        "severity": "Medium",
        "first_symptom_time": "2026-09-07T08:00:00Z",
        "farmer_notes": "Spots spreading on lower branches."
    }
    res = client.post("/api/cases/json", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["case_id"].startswith("CASE-2026-")
    assert data["anonymous_farmer_id"].startswith("FARMER-ANON-")
    # Coordinates rounded to 2 decimals
    assert data["latitude"] == 12.35
    assert data["longitude"] == 76.54
    assert data["crop"] == "Tomato"
    assert data["status"] == "Submitted"
    assert data["priority"] in ["High", "Medium", "Low"]


def test_get_cases_and_filters():
    res = client.get("/api/cases")
    assert res.status_code == 200
    cases = res.json()
    assert len(cases) > 0
    first_id = cases[0]["case_id"]

    # Test single case retrieval
    detail_res = client.get(f"/api/cases/{first_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["case_id"] == first_id

    # Test filtering by crop
    crop_res = client.get("/api/cases?crop=Tomato")
    assert crop_res.status_code == 200
    for c in crop_res.json():
        assert "Tomato" in c["crop"]


def test_expert_review_workflow():
    # Submit a fresh case
    payload = {
        "crop": "Potato",
        "location": "Western Block",
        "crop_stage": "Fruiting",
        "symptoms": ["leaf_spots"],
        "severity": "Severe",
        "first_symptom_time": "2026-09-06T10:00:00Z"
    }
    create_res = client.post("/api/cases/json", json=payload)
    case_id = create_res.json()["case_id"]

    # Submit Expert Review
    rev_payload = {
        "expert_category": "Fungal Early Blight (Alternaria)",
        "validation_status": "confirmed",
        "comments": "Apply mancozeb spray; prune lower canopy.",
        "urgency": "Prompt"
    }
    rev_res = client.post(f"/api/cases/{case_id}/review", json=rev_payload)
    assert rev_res.status_code == 200
    updated_case = rev_res.json()
    assert updated_case["status"] == "Expert Validated"
    assert updated_case["expert_validation"] == "Fungal Early Blight (Alternaria)"
    assert updated_case["expert_review_time"] is not None


def test_metrics_summary():
    res = client.get("/api/metrics/summary")
    assert res.status_code == 200
    m = res.json()
    assert m["total_observations"] > 0
    assert "comparison_table" in m
    assert m["report_completeness_rate"] >= 0.0
    assert m["image_usability_rate"] >= 0.0
