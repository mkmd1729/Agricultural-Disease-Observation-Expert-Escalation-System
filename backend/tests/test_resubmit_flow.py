"""
Automated unit and integration tests for Phase 2.5:
Farmer Case Tracking & Resubmission Workflow.
"""

import io
from PIL import Image
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_track_case_by_id():
    """Verify farmer can retrieve observation status and history using case reference ID."""
    # Seed a case
    payload = {
        "crop": "Tomato",
        "location": "Delta Sector 4",
        "crop_stage": "Vegetative",
        "symptoms": ["leaf_spots"],
        "severity": "Medium",
        "first_symptom_time": "2026-10-01T12:00:00Z"
    }
    create_res = client.post("/api/cases/json", json=payload)
    assert create_res.status_code == 201
    case_id = create_res.json()["case_id"]

    # Retrieve case
    track_res = client.get(f"/api/cases/{case_id}")
    assert track_res.status_code == 200
    data = track_res.json()
    assert data["case_id"] == case_id
    assert data["status"] == "Submitted"
    assert data["crop"] == "Tomato"


def test_track_nonexistent_case_returns_404():
    """Verify lookup with invalid ID returns proper 404 error."""
    res = client.get("/api/cases/CASE-NONEXISTENT-999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_farmer_resubmission_flow():
    """
    Complete lifecycle test:
    1. Case submitted
    2. Expert flags 'more_info_needed'
    3. Farmer provides clarification via /resubmit
    4. Case returns to 'Under Review' with updated farmer notes
    """
    # 1. Create case
    c_res = client.post("/api/cases/json", json={
        "crop": "Paddy / Rice",
        "location": "Thanjavur Basin",
        "crop_stage": "Tillering",
        "symptoms": ["bacterial_ooze"],
        "severity": "High",
        "first_symptom_time": "2026-10-01T08:00:00Z"
    })
    case_id = c_res.json()["case_id"]

    # 2. Expert reviews and requests more information
    rev_payload = {
        "expert_category": "Bacterial Blight",
        "validation_status": "more_info_needed",
        "comments": "Please check if wilting is visible on upper leaf tips as well.",
        "urgency": "Prompt"
    }
    rev_res = client.post(f"/api/cases/{case_id}/review", json=rev_payload)
    assert rev_res.status_code == 200
    assert rev_res.json()["status"] == "More Information Required"

    # 3. Farmer resubmits clarifying notes
    resub_res = client.post(
        f"/api/cases/{case_id}/resubmit",
        data={"additional_notes": "Wilting observed only on lower leaves, upper canopy looks green."}
    )
    assert resub_res.status_code == 200
    resub_data = resub_res.json()
    assert resub_data["status"] == "Under Review"
    assert "lower leaves" in resub_data["farmer_notes"]


def test_farmer_resubmission_with_photo():
    """Verify farmer can attach an additional photo during resubmission."""
    c_res = client.post("/api/cases/json", json={
        "crop": "Maize",
        "location": "Green Valley Block A",
        "crop_stage": "Seedling",
        "symptoms": ["yellowing_chlorosis"],
        "severity": "Medium",
        "first_symptom_time": "2026-10-01T09:00:00Z"
    })
    case_id = c_res.json()["case_id"]

    # Create dummy image
    img = Image.new("RGB", (100, 100), color=(100, 200, 100))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    resub_res = client.post(
        f"/api/cases/{case_id}/resubmit",
        data={"additional_notes": "Attached clearer close-up photo of leaf margins."},
        files={"new_image": ("clarification_leaf.jpg", buf, "image/jpeg")}
    )
    assert resub_res.status_code == 200
    resub_data = resub_res.json()
    assert resub_data["status"] == "Under Review"
    assert len(resub_data["images"]) >= 1
    assert resub_data["images"][-1]["image_type"] == "resubmitted_detail"
