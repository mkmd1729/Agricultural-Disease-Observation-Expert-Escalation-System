"""
End-to-End System Integration Test.
Validates complete vertical slice workflow from farmer submission to expert validation and T_review.
"""

import sys
from pathlib import Path
import io

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from PIL import Image, ImageDraw
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import init_db, SessionLocal
from backend.app.models import Case, AuditLog

init_db()
client = TestClient(app)


def test_full_vertical_slice_workflow():
    # 1. Create synthetic in-memory image
    img = Image.new("RGB", (300, 300), (220, 230, 215))
    draw = ImageDraw.Draw(img)
    draw.pieslice([40, 30, 260, 270], 30, 330, fill=(46, 139, 87), outline=(20, 70, 20), width=4)
    for i in range(5):
        draw.ellipse([80 + i * 30, 100 + i * 20, 100 + i * 30, 120 + i * 20], fill=(120, 60, 20))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    img_bytes = buf.getvalue()

    # 2. Farmer Submits Case with Image Upload
    multipart_data = {
        "crop": "Tomato",
        "variety": "Roma VF",
        "symptoms": "leaf_spots",
        "crop_stage": "Flowering",
        "location": "Green Valley District",
        "latitude": "11.246",
        "longitude": "77.154",
        "severity": "Severe",
        "first_symptom_time": "2026-09-06T08:00:00Z",
        "farmer_notes": "Concentric rings developing rapidly."
    }
    files = {
        "image_affected": ("affected_leaf.jpg", img_bytes, "image/jpeg")
    }

    create_res = client.post("/api/cases", data=multipart_data, files=files)
    assert create_res.status_code == 201
    case_data = create_res.json()
    case_id = case_data["case_id"]

    # Verify ID format & anonymization
    assert case_id.startswith("CASE-2026-")
    assert case_data["anonymous_farmer_id"].startswith("FARMER-ANON-")
    assert case_data["latitude"] == 11.25  # Rounded to 2 decimals
    assert case_data["longitude"] == 77.15  # Rounded to 2 decimals

    # Verify Image Record & Quality
    assert len(case_data["images"]) == 1
    assert case_data["images"][0]["quality_score"] > 0
    assert case_data["images"][0]["image_type"] == "affected_area"

    # Verify AI Hypothesis & Priority
    assert case_data["ai_prediction"] is not None
    assert case_data["ai_confidence"] is not None
    assert case_data["priority"] == "High"  # Severe + Flowering
    assert case_data["status"] == "Submitted"

    # 3. Extension Officer Inspects Case via API
    get_res = client.get(f"/api/cases/{case_id}")
    assert get_res.status_code == 200
    assert get_res.json()["case_id"] == case_id

    # 4. Expert Validates Case (Testing Expert Override Authority)
    review_payload = {
        "expert_category": "Early Blight (Alternaria solani)",
        "validation_status": "confirmed",
        "comments": "Confirmed early blight. Apply chlorothalonil or copper spray immediately.",
        "urgency": "Prompt"
    }
    rev_res = client.post(f"/api/cases/{case_id}/review", json=review_payload)
    assert rev_res.status_code == 200
    validated_case = rev_res.json()

    assert validated_case["status"] == "Expert Validated"
    assert validated_case["expert_validation"] == "Early Blight (Alternaria solani)"
    assert validated_case["expert_review_time"] is not None

    # 5. Check T_review Metric in Metrics Summary
    metrics_res = client.get("/api/metrics/summary")
    assert metrics_res.status_code == 200
    metrics_data = metrics_res.json()
    assert metrics_data["expert_validated_cases"] >= 1
    assert metrics_data["avg_t_review_hours"] is not None
    assert metrics_data["avg_t_review_hours"] > 0

    # 6. Verify Audit Trail in DB
    db = SessionLocal()
    logs = db.query(AuditLog).filter(AuditLog.case_id == case_id).all()
    assert len(logs) >= 2  # CASE_CREATED and EXPERT_REVIEW_SUBMITTED
    db.close()
    print("End-to-End Vertical Slice Test successfully passed!")
