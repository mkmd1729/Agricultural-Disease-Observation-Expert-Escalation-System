"""
Automated unit and integration tests for Phase 2.6:
Expert Validation Workstation improvements and authoritative override logic.
"""

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_expert_confirmation_updates_status():
    """Expert agrees with preliminary hypothesis and confirms case."""
    c_res = client.post("/api/cases/json", json={
        "crop": "Tomato",
        "location": "Sector 1",
        "crop_stage": "Fruiting",
        "symptoms": ["leaf_spots", "powdery_coating"],
        "severity": "Medium",
        "first_symptom_time": "2026-10-01T08:00:00Z"
    })
    case_id = c_res.json()["case_id"]

    rev_res = client.post(f"/api/cases/{case_id}/review", json={
        "expert_category": "Powdery Mildew (Fungal)",
        "validation_status": "confirmed",
        "comments": "Confirmed foliar powdery mildew. Apply wettable sulfur at 2g/L.",
        "urgency": "Prompt"
    })
    assert rev_res.status_code == 200
    data = rev_res.json()
    assert data["status"] == "Expert Validated"
    assert data["expert_validation"] == "Powdery Mildew (Fungal)"
    assert "wettable sulfur" in data["expert_comments"]


def test_expert_override_preserves_ai_prediction_for_audit():
    """
    STRICT RULE: Expert override supersedes AI suggestion,
    while AI proposal is preserved unchanged on the case for error analysis.
    """
    c_res = client.post("/api/cases/json", json={
        "crop": "Tomato",
        "location": "Sector 2",
        "crop_stage": "Vegetative",
        "symptoms": ["yellowing_chlorosis", "tip_burn"],
        "severity": "High",
        "first_symptom_time": "2026-10-01T08:00:00Z"
    })
    initial = c_res.json()
    case_id = initial["case_id"]
    original_ai = initial["ai_prediction"]

    # Expert overrides AI proposal
    rev_res = client.post(f"/api/cases/{case_id}/review", json={
        "expert_category": "Nitrogen Deficiency (Abiotic)",
        "validation_status": "rejected_ai",
        "comments": "Uniform lower leaf chlorosis indicates nitrogen starvation, not fungal blight.",
        "urgency": "Routine"
    })
    assert rev_res.status_code == 200
    data = rev_res.json()
    assert data["status"] == "Expert Validated"
    assert data["expert_validation"] == "Nitrogen Deficiency (Abiotic)"
    # Verify AI prediction is preserved
    assert data["ai_prediction"] == original_ai


def test_expert_urgent_review_elevates_priority_to_high():
    """If expert designates review urgency as 'Urgent', case priority is elevated to High."""
    c_res = client.post("/api/cases/json", json={
        "crop": "Paddy / Rice",
        "location": "Delta Sector 5",
        "crop_stage": "Tillering",
        "symptoms": ["healthy"],
        "severity": "Low",
        "first_symptom_time": "2026-10-01T08:00:00Z"
    })
    case_id = c_res.json()["case_id"]
    assert c_res.json()["priority"] in ["Low", "Medium"]

    rev_res = client.post(f"/api/cases/{case_id}/review", json={
        "expert_category": "Bacterial Leaf Streak",
        "validation_status": "confirmed",
        "comments": "High contagion threat in waterlogged basin. Immediate field quarantine advised.",
        "urgency": "Urgent"
    })
    assert rev_res.status_code == 200
    assert rev_res.json()["priority"] == "High"


def test_expert_uncertain_review_status():
    """Expert marks case as uncertain pending laboratory microbiological analysis."""
    c_res = client.post("/api/cases/json", json={
        "crop": "Tomato",
        "location": "Green Valley",
        "crop_stage": "Flowering",
        "symptoms": ["wilting"],
        "severity": "High",
        "first_symptom_time": "2026-10-01T08:00:00Z"
    })
    case_id = c_res.json()["case_id"]

    rev_res = client.post(f"/api/cases/{case_id}/review", json={
        "expert_category": "Vascular Wilt Complex",
        "validation_status": "uncertain",
        "comments": "Stem pith browning requires laboratory streak plating to differentiate Ralstonia vs Fusarium.",
        "urgency": "Prompt"
    })
    assert rev_res.status_code == 200
    assert rev_res.json()["status"] == "Under Review (Uncertain)"
