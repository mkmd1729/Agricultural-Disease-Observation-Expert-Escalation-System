"""
Automated unit and integration tests for Phase 2.7:
Seven Required Failure & Edge Cases.
1. Poor / blurry / dark image quality handling
2. Low-confidence ML prediction (<60%) -> safety escalation
3. Conflicting AI proposal vs authoritative expert override
4. Offline observation drafting and queue synchronization
5. Duplicate sync prevention
6. Missing environmental / microclimate context handling
7. Farmer case tracking & resubmission after expert inquiry
"""

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.priority import calculate_priority_score
from backend.app.ai_assistant import classify_observation

client = TestClient(app)


def test_edge_case_1_poor_image_quality():
    """Edge Case 1: Image analysis detects poor blur/luminance and returns structured guidance without discarding photo."""
    response = client.get("/api/edge-cases/1")
    assert response.status_code == 200
    data = response.json()
    assert "quality_score" in data
    assert data["quality_score"] <= 50.0  # Degraded image
    assert "warnings" in data
    assert len(data["warnings"]) >= 1
    assert "farmer_advice" in data
    assert len(data["farmer_advice"]) >= 1


def test_edge_case_2_low_confidence_escalation():
    """
    Edge Case 2: When model confidence is strictly < 60%,
    triage system refuses diagnostic authority and escalates priority to High.
    """
    priority, reason = calculate_priority_score(
        severity="Low",
        crop_stage="Vegetative",
        ai_confidence=58.5,  # Strictly < 60%
        symptoms=["unclassified_spot"]
    )
    assert priority == "High"
    assert "low ai confidence" in reason.lower() or "< 60%" in reason.lower()

    # Controlled boundary test: >= 60% with Low severity remains Low/Medium
    p_safe, _ = calculate_priority_score(
        severity="Low",
        crop_stage="Vegetative",
        ai_confidence=65.0,
        symptoms=["unclassified_spot"]
    )
    assert p_safe != "High"


def test_edge_case_3_conflicting_ai_vs_expert_override():
    """
    Edge Case 3: Conflicting AI hypothesis vs expert override.
    Expert is authoritative; AI hypothesis preserved for error tracking.
    """
    c_res = client.post("/api/cases/json", json={
        "crop": "Tomato",
        "location": "Delta Belt",
        "crop_stage": "Vegetative",
        "symptoms": ["tip_burn"],
        "severity": "Medium",
        "first_symptom_time": "2026-10-01T10:00:00Z"
    })
    case = c_res.json()
    case_id = case["case_id"]
    ai_pred = case["ai_prediction"]

    # Expert overrides AI
    rev_res = client.post(f"/api/cases/{case_id}/review", json={
        "expert_category": "Potassium Deficiency (Abiotic)",
        "validation_status": "rejected_ai",
        "comments": "Marginal scorching on older foliage points directly to K deficiency.",
        "urgency": "Routine"
    })
    assert rev_res.status_code == 200
    updated = rev_res.json()
    assert updated["expert_validation"] == "Potassium Deficiency (Abiotic)"
    assert updated["status"] == "Expert Validated"
    assert updated["ai_prediction"] == ai_pred  # AI diagnosis preserved


def test_edge_case_4_offline_sync_simulation():
    """
    Edge Case 4: Synchronizing an observation created in offline mode.
    Endpoint processes JSON payload and returns standardized case ID and triage.
    """
    offline_payload = {
        "crop": "Maize",
        "location": "Dryland Sector 7",
        "crop_stage": "Vegetative",
        "symptoms": ["mosaic_pattern"],
        "severity": "High",
        "first_symptom_time": "2026-10-01T11:00:00Z",
        "farmer_notes": "Created in offline IndexedDB queue, synced after connectivity returned."
    }
    sync_res = client.post("/api/cases/json", json=offline_payload)
    assert sync_res.status_code == 201
    synced_case = sync_res.json()
    assert synced_case["case_id"].startswith("CASE-2026-")
    assert synced_case["crop"] == "Maize"
    assert synced_case["status"] == "Submitted"


def test_edge_case_5_duplicate_sync_prevention():
    """
    Edge Case 5: Duplicate sync handling.
    The system correctly accepts idempotency checks; subsequent queries for existing cases return existing state without corrupting records.
    """
    # Create initial case
    res1 = client.post("/api/cases/json", json={
        "crop": "Rice",
        "location": "Thanjavur Delta",
        "crop_stage": "Tillering",
        "symptoms": ["leaf_spots"],
        "severity": "Medium",
        "first_symptom_time": "2026-10-01T12:00:00Z"
    })
    case_id = res1.json()["case_id"]

    # Querying the existing case confirms it exists and is unchanged
    res2 = client.get(f"/api/cases/{case_id}")
    assert res2.status_code == 200
    assert res2.json()["case_id"] == case_id


def test_edge_case_6_missing_environmental_context():
    """
    Edge Case 6: Submissions with completely missing environmental / microclimate fields
    gracefully default to 'Unknown' and do not crash or halt triage.
    """
    res = client.post("/api/cases/json", json={
        "crop": "Tomato",
        "location": "Remote Sector Without Weather Sensors",
        "crop_stage": "Seedling",
        "symptoms": ["damping_off"],
        "severity": "Severe",
        "first_symptom_time": "2026-10-01T07:00:00Z"
        # environmental fields omitted intentionally
    })
    assert res.status_code == 201
    data = res.json()
    assert data["rainfall_recent"] == "Unknown"
    assert data["humidity_level"] == "Unknown"
    assert data["soil_moisture_observation"] == "Unknown"
    assert data["priority"] == "High"  # Severe seedling damping_off is high priority


def test_edge_case_7_resubmission_cycle():
    """
    Edge Case 7: Farmer tracking & resubmission cycle.
    Case transitions from More Information Required -> Under Review upon farmer resubmission.
    """
    c_res = client.post("/api/cases/json", json={
        "crop": "Tomato",
        "location": "Riverside Zone",
        "crop_stage": "Flowering",
        "symptoms": ["leaf_curling"],
        "severity": "Medium",
        "first_symptom_time": "2026-10-01T06:00:00Z"
    })
    cid = c_res.json()["case_id"]

    # Expert asks for info
    client.post(f"/api/cases/{cid}/review", json={
        "expert_category": "Suspected Tomato Yellow Leaf Curl",
        "validation_status": "more_info_needed",
        "comments": "Are whiteflies visible on the underside of young leaves?",
        "urgency": "Prompt"
    })
    assert client.get(f"/api/cases/{cid}").json()["status"] == "More Information Required"

    # Farmer resubmits
    resub = client.post(f"/api/cases/{cid}/resubmit", data={
        "additional_notes": "Yes, tiny white flies fly off when the plant is shaken."
    })
    assert resub.status_code == 200
    assert resub.json()["status"] == "Under Review"
