"""
Automated Execution Script for Section 34 Final Acceptance Tests.
Runs all 15 tests sequentially and outputs a verified test report.
"""

import sys
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal, init_db
from backend.app.models import Case, ImageRecord, ExpertReview
from backend.app.metrics import compute_metrics_summary
from ml.evaluate import run_experiment_evaluation

init_db()
client = TestClient(app)

results = {}


def run_all_acceptance_tests():
    print("======================================================================")
    print("       FINAL ACCEPTANCE TEST EXECUTION (SECTION 34: TESTS 1-15)")
    print("======================================================================\n")

    # Sample reference image path
    ref_img_path = PROJECT_ROOT / "ml" / "dataset" / "fungal" / "REF-FUN-001.jpg"
    with open(ref_img_path, "rb") as f:
        ref_bytes = f.read()

    # TEST 1-6: Farmer Case Creation Flow
    print("[TEST 1-6] Creating Farmer Case with Crop, Symptoms, Stage, Location & Image...")
    first_sym_time = (datetime.now(timezone.utc) - timedelta(hours=30.0)).isoformat()
    form_data = {
        "crop": "Tomato",                       # TEST 2: Select crop
        "symptoms": "leaf_spots",               # TEST 3: Enter symptoms
        "crop_stage": "Flowering",              # TEST 4: Enter crop stage
        "location": "Delta Paddy Belt Sector B",# TEST 5: Enter approximate location
        "latitude": "10.824",
        "longitude": "79.198",
        "severity": "Severe",
        "first_symptom_time": first_sym_time,
        "farmer_notes": "Concentric dark brown rings on middle leaves."
    }
    files = {
        "image_affected": ("field_leaf.jpg", ref_bytes, "image/jpeg") # TEST 6: Upload crop image
    }

    res = client.post("/api/cases", data=form_data, files=files)
    assert res.status_code == 201, f"Failed case creation: {res.status_code}"
    case_data = res.json()
    case_id = case_data["case_id"]

    results["Test 1: Create farmer case"] = "PASS"
    results["Test 2: Select crop"] = f"PASS (Crop: {case_data['crop']})"
    results["Test 3: Enter symptoms"] = f"PASS (Symptoms: {case_data['symptoms']})"
    results["Test 4: Enter crop stage"] = f"PASS (Stage: {case_data['crop_stage']})"
    results["Test 5: Enter approximate location"] = f"PASS ({case_data['location']}, Lat: {case_data['latitude']}, Lon: {case_data['longitude']})"
    results["Test 6: Upload project-created crop image"] = f"PASS (Images uploaded: {len(case_data['images'])})"

    # TEST 7: Generate Anonymous Case ID
    assert case_id.startswith("CASE-2026-")
    assert case_data["anonymous_farmer_id"].startswith("FARMER-ANON-")
    results["Test 7: Generate anonymous case ID"] = f"PASS (Case ID: {case_id}, Farmer ID: {case_data['anonymous_farmer_id']})"

    # TEST 8: Run Image-Quality/Confidence Logic
    img_rec = case_data["images"][0]
    quality_score = img_rec["quality_score"]
    confidence = case_data["ai_confidence"]
    prediction = case_data["ai_prediction"]
    priority = case_data["priority"]
    assert quality_score > 0
    assert confidence > 0
    results["Test 8: Run image-quality/confidence logic"] = f"PASS (Score: {quality_score}, AI: {prediction}, Conf: {confidence}%, Priority: {priority})"

    # TEST 9: Display Case in Expert Dashboard
    list_res = client.get(f"/api/cases/{case_id}")
    assert list_res.status_code == 200
    results["Test 9: Display case in expert dashboard"] = f"PASS (Retrieved case {case_id} via API)"

    # TEST 10: Expert Validates the Case
    review_data = {
        "expert_category": "Early Blight (Alternaria solani)",
        "validation_status": "confirmed",
        "comments": "Confirmed Alternaria solani. Spray azoxystrobin; remove lower affected leaves.",
        "urgency": "Prompt"
    }
    rev_res = client.post(f"/api/cases/{case_id}/review", json=review_data)
    assert rev_res.status_code == 200
    rev_case = rev_res.json()
    results["Test 10: Expert validates the case"] = f"PASS (Validation: {rev_case['expert_validation']})"

    # TEST 11: Update Case Status
    assert rev_case["status"] == "Expert Validated"
    results["Test 11: Update case status"] = f"PASS (Status updated to: {rev_case['status']})"

    # TEST 12: Record Expert Review Timestamp
    rev_time = rev_case["expert_review_time"]
    assert rev_time is not None
    results["Test 12: Record expert review timestamp"] = f"PASS (Timestamp: {rev_time})"

    # TEST 13: Calculate Time From First Symptom to Useful Expert Review
    db = SessionLocal()
    metrics = compute_metrics_summary(db)
    avg_t_review = metrics["avg_t_review_hours"]
    assert avg_t_review is not None and avg_t_review > 0
    db.close()
    results["Test 13: Calculate T_review"] = f"PASS (Calculated Avg T_review: {avg_t_review} hours)"

    # TEST 14: Run at least Three Failure Cases
    # Edge Case 1: Poor image
    edge1_res = client.get("/api/cases/CASE-2026-003")
    assert edge1_res.status_code == 200
    raw_warnings = edge1_res.json()["images"][0]["quality_warnings"]
    e1_warnings = raw_warnings if isinstance(raw_warnings, list) else json.loads(raw_warnings or "[]")
    assert len(e1_warnings) > 0

    # Edge Case 2: Low confidence (< 60%)
    edge2_res = client.get("/api/cases/CASE-2026-004")
    assert edge2_res.status_code == 200
    assert edge2_res.json()["ai_confidence"] < 60.0
    assert edge2_res.json()["priority"] == "High"

    # Edge Case 3: Conflicting expert validation (AI override)
    edge3_res = client.get("/api/cases/CASE-2026-005")
    assert edge3_res.status_code == 200
    e3_case = edge3_res.json()
    assert "Abiotic" in e3_case["expert_validation"]
    assert e3_case["status"] == "Expert Validated"
    results["Test 14: Run at least three failure cases"] = (
        f"PASS (Edge 1 Poor Image: {e1_warnings[0]} | "
        f"Edge 2 Low Conf: {edge2_res.json()['ai_confidence']}% -> High Priority | "
        f"Edge 3 Conflict: Expert override '{e3_case['expert_validation']}' authoritative)"
    )

    # TEST 15: Generate/Update Experiment Results
    exp_results = run_experiment_evaluation()
    assert len(exp_results) > 0
    results["Test 15: Generate/update experiment results"] = f"PASS (Evaluated {len(exp_results)} cases; experiment report updated)"

    # Print Final Test Matrix
    print("\n======================================================================")
    print("                     ACCEPTANCE TEST MATRIX RESULTS")
    print("======================================================================")
    all_passed = True
    for test_name, status_str in results.items():
        print(f"{test_name:<46}: {status_str}")
        if not status_str.startswith("PASS"):
            all_passed = False

    print("======================================================================")
    if all_passed:
        print("ALL 15 ACCEPTANCE TESTS COMPLETED SUCCESSFULLY WITH 100% PASS RATE.")
    else:
        print("SOME TESTS FAILED. PLEASE INSPECT LOGS.")
    print("======================================================================\n")


if __name__ == "__main__":
    run_all_acceptance_tests()
