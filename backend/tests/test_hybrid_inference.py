"""
Automated unit and integration tests for Phase 2.2 (Vision Inference & Hybrid Decision Support)
and Phase 2.3 (Environmental / Microclimate Context).
"""

import pytest
import io
from PIL import Image
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.ai_assistant import classify_observation
from backend.app.priority import calculate_priority_score
from backend.app.vision_service import predict_image

client = TestClient(app)


def test_hybrid_concordance_reinforces_confidence():
    """When vision and symptoms agree (e.g. fungal foliar spots), confidence is reinforced."""
    vision_mock = {
        "predicted_category": "Fungal",
        "visual_confidence": 85.0,
        "is_available": True
    }
    result = classify_observation(
        crop="Tomato",
        symptoms=["leaf_spots", "powdery_coating"],
        crop_stage="Vegetative",
        image_quality_score=90.0,
        has_image=True,
        vision_result=vision_mock
    )
    assert "Fungal" in result["possible_category"]
    assert result["confidence"] >= 75.0
    assert result["requires_escalation"] is False
    assert result["vision_assisted"] is True


def test_hybrid_conflict_triggers_low_confidence_escalation():
    """
    STRICT SAFETY RULE: When vision (e.g. Fungal) conflicts with symptoms (e.g. Mosaic pattern - viral),
    confidence is penalized into < 60% escalation zone.
    """
    vision_mock = {
        "predicted_category": "Fungal",
        "visual_confidence": 75.0,
        "is_available": True
    }
    result = classify_observation(
        crop="Tomato",
        symptoms=["mosaic_pattern"],  # Strongly viral
        crop_stage="Vegetative",
        image_quality_score=85.0,
        has_image=True,
        vision_result=vision_mock
    )
    assert "Ambiguous" in result["possible_category"]
    assert result["confidence"] < 60.0
    assert result["requires_escalation"] is True
    assert "urgent expert escalation" in result["status_label"].lower()


def test_environmental_context_prioritization():
    """High rainfall / humidity / waterlogging adds triage priority points."""
    # Base low severity case without environmental amplification
    p_normal, _ = calculate_priority_score(
        severity="Low",
        crop_stage="Vegetative",
        ai_confidence=78.0,
        symptoms=["yellowing_chlorosis"],
        rainfall_recent="None",
        humidity_level="Normal",
        soil_moisture="Dry"
    )
    assert p_normal == "Low"

    # Same case with critical microclimate factors (high rain + waterlogging)
    p_env, reason = calculate_priority_score(
        severity="Medium",
        crop_stage="Vegetative",
        ai_confidence=70.0,
        symptoms=["leaf_spots"],
        rainfall_recent="High",
        humidity_level="High",
        soil_moisture="Waterlogged"
    )
    assert p_env in ["Medium", "High"]
    assert "environmental" in reason.lower() or "humidity" in reason.lower()


def test_vision_status_endpoint():
    """Verify /api/vision/status returns loaded MobileNetV3 status."""
    response = client.get("/api/vision/status")
    assert response.status_code == 200
    data = response.json()
    assert data["model_architecture"] == "MobileNetV3-Small"
    assert data["num_classes"] == 5
    assert "fungal" in data["classes"]
    assert data["checkpoint_exists"] is True
    assert data["status"] == "loaded"


def test_vision_predict_endpoint_with_synthetic_leaf():
    """Verify direct image inference on /api/vision-predict."""
    img = Image.new("RGB", (224, 224), color=(34, 139, 34))  # Forest green
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    response = client.post(
        "/api/vision-predict",
        files={"image": ("test_leaf.jpg", buf, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "predicted_category" in data
    assert "visual_confidence" in data
    assert "probabilities" in data
    assert len(data["probabilities"]) == 5
    assert data["is_available"] is True


def test_case_submission_with_environmental_context_persisted():
    """Verify environmental fields are accepted and persisted via JSON submission."""
    payload = {
        "crop": "Paddy / Rice",
        "location": "Thanjavur, Tamil Nadu",
        "crop_stage": "Tillering",
        "symptoms": ["leaf_spots"],
        "severity": "Medium",
        "first_symptom_time": "2026-10-01T10:00:00Z",
        "rainfall_recent": "High",
        "humidity_level": "High",
        "temperature_band": "Hot (>30°C)",
        "recent_weather_event": "Monsoon downpour",
        "irrigation_status": "Canal Irrigated",
        "soil_moisture_observation": "Waterlogged",
        "field_condition": "Flooded furrow",
        "farmer_notes": "Heavy rains for 3 consecutive days."
    }
    response = client.post("/api/cases/json", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["rainfall_recent"] == "High"
    assert data["humidity_level"] == "High"
    assert data["soil_moisture_observation"] == "Waterlogged"
    assert data["field_condition"] == "Flooded furrow"

    # Retrieve case
    case_id = data["case_id"]
    get_res = client.get(f"/api/cases/{case_id}")
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["rainfall_recent"] == "High"
    assert get_data["humidity_level"] == "High"
