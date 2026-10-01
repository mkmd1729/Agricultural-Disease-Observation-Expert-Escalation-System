"""
Seeds the database with 12 diverse, synthetic demonstration cases covering all required
review states, edge cases, and crop categories.
Also writes data/sample_cases.json.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from datetime import datetime, timezone, timedelta
import json
import shutil
from backend.app.database import init_db, SessionLocal, UPLOADS_DIR, DATA_DIR, BASE_DIR
from backend.app.models import Case, ImageRecord, ExpertReview, AuditLog

init_db()

DATASET_DIR = BASE_DIR / "ml" / "dataset"
TEST_IMG_DIR = DATA_DIR / "test_images"


def now_minus(hours: float) -> datetime:
    return datetime.now(timezone.utc) - timedelta(hours=hours)


def copy_to_uploads(src: Path, case_id: str, tag: str) -> str:
    """Copies a sample image to uploads directory and returns the public URL."""
    if not src.exists():
        src = DATASET_DIR / "healthy" / "REF-HEA-001.jpg"
    dest_name = f"{case_id}_{tag}_{src.name}"
    dest_path = UPLOADS_DIR / dest_name
    shutil.copyfile(src, dest_path)
    return f"/uploads/{dest_name}"


def seed_database():
    db = SessionLocal()
    # Clear existing demo records
    db.query(AuditLog).delete()
    db.query(ExpertReview).delete()
    db.query(ImageRecord).delete()
    db.query(Case).delete()
    db.commit()

    demo_cases = [
        # Case 1: Standard Fungal Case - Submitted & High Priority
        {
            "case_id": "CASE-2026-001",
            "anonymous_farmer_id": "FARMER-ANON-8812",
            "crop": "Tomato",
            "variety": "Roma VF",
            "location": "Green Valley District, Sector 4",
            "latitude": 11.24,
            "longitude": 77.15,
            "crop_stage": "Flowering",
            "symptoms": "leaf_spots, yellowing_chlorosis",
            "severity": "Severe",
            "first_symptom_time": now_minus(36.0),
            "submission_time": now_minus(18.0),
            "ai_prediction": "Fungal-like symptom",
            "ai_confidence": 74.0,
            "ai_alternative": "Bacterial leaf spot",
            "priority": "High",
            "priority_reason": "Reported high symptom severity; Critical growth stage (flowering/fruiting)",
            "status": "Under Review",
            "farmer_notes": "Concentric rings observed on lower leaves. Spreading upward rapidly.",
            "environmental_notes": "Heavy rains and high humidity over the past 3 days.",
            "images": [
                {
                    "id": "IMG-001-A",
                    "type": "affected_area",
                    "src": DATASET_DIR / "fungal" / "REF-FUN-001.jpg",
                    "score": 88.0,
                    "warnings": [],
                    "advice": []
                }
            ]
        },
        # Case 2: Expert Validated Fungal Case (Demonstrating Fast T_review calculation)
        {
            "case_id": "CASE-2026-002",
            "anonymous_farmer_id": "FARMER-ANON-3341",
            "crop": "Tomato",
            "variety": "Local Hybrid",
            "location": "Riverside Agro Zone",
            "latitude": 11.31,
            "longitude": 77.08,
            "crop_stage": "Fruiting",
            "symptoms": "leaf_spots",
            "severity": "Medium",
            "first_symptom_time": now_minus(24.0),
            "submission_time": now_minus(8.0),
            "ai_prediction": "Fungal-like symptom",
            "ai_confidence": 72.0,
            "ai_alternative": "Bacterial leaf spot",
            "priority": "Medium",
            "priority_reason": "Standard routine triage; Critical growth stage",
            "status": "Expert Validated",
            "expert_validation": "Fungal leaf blight (Early blight - Alternaria solani)",
            "expert_comments": "Classic Alternaria target-board concentric rings. Apply copper oxychloride or azoxystrobin spray. Remove lower infected leaves.",
            "expert_review_time": now_minus(2.0),
            "farmer_notes": "Small brown spots on tomato leaves.",
            "images": [
                {
                    "id": "IMG-002-A",
                    "type": "leaf_detail",
                    "src": DATASET_DIR / "fungal" / "REF-FUN-001.jpg",
                    "score": 92.0,
                    "warnings": [],
                    "advice": []
                }
            ],
            "reviews": [
                {
                    "id": "REV-002",
                    "expert_category": "Fungal",
                    "status": "confirmed",
                    "comments": "Confirmed early blight. Clear concentric lesions.",
                    "urgency": "Prompt",
                    "time": now_minus(2.0)
                }
            ]
        },
        # Case 3: Edge Case 1 - Poor / Blurry Image
        {
            "case_id": "CASE-2026-003",
            "anonymous_farmer_id": "FARMER-ANON-9014",
            "crop": "Potato",
            "variety": "Kufri Jyoti",
            "location": "Highland Agricultural Block",
            "latitude": 11.45,
            "longitude": 76.92,
            "crop_stage": "Vegetative",
            "symptoms": "leaf_spots",
            "severity": "Low",
            "first_symptom_time": now_minus(48.0),
            "submission_time": now_minus(12.0),
            "ai_prediction": "Fungal-like symptom",
            "ai_confidence": 58.0,
            "ai_alternative": "Unclassified foliar symptom",
            "priority": "High",
            "priority_reason": "Low AI confidence (58.0% < 60%) — urgent expert escalation required; Image quality degraded",
            "status": "Submitted",
            "farmer_notes": "Camera shook while taking photo in the field.",
            "images": [
                {
                    "id": "IMG-003-A",
                    "type": "leaf_detail",
                    "src": TEST_IMG_DIR / "edge_case_blurry.jpg",
                    "score": 20.0,
                    "warnings": ["Image may be blurry", "Image may be underexposed"],
                    "advice": ["Hold the phone steady and take another photo.", "Move to better lighting."]
                }
            ]
        },
        # Case 4: Edge Case 2 - Low Confidence (< 60%) -> High Priority Escalation
        {
            "case_id": "CASE-2026-004",
            "anonymous_farmer_id": "FARMER-ANON-5521",
            "crop": "Rice",
            "variety": "Basmati 370",
            "location": "Delta Paddy Belt",
            "latitude": 10.78,
            "longitude": 79.14,
            "crop_stage": "Seedling",
            "symptoms": "wilting, stunting",
            "severity": "Medium",
            "first_symptom_time": now_minus(18.0),
            "submission_time": now_minus(6.0),
            "ai_prediction": "Wilting symptom (Water stress or vascular pathogen)",
            "ai_confidence": 51.0,
            "ai_alternative": "Bacterial wilt",
            "priority": "High",
            "priority_reason": "Low AI confidence (51.0% < 60%) — urgent expert escalation required; Early seedling vulnerability",
            "status": "Submitted",
            "farmer_notes": "Seedlings suddenly drooping in corner of seedbed.",
            "environmental_notes": "Standing water after sudden cloudburst.",
            "images": [
                {
                    "id": "IMG-004-A",
                    "type": "whole_plant",
                    "src": DATASET_DIR / "healthy" / "REF-HEA-003.jpg",
                    "score": 85.0,
                    "warnings": [],
                    "advice": []
                }
            ]
        },
        # Case 5: Edge Case 3 - Conflicting Expert Validation (AI = Fungal, Expert = Abiotic Stress)
        {
            "case_id": "CASE-2026-005",
            "anonymous_farmer_id": "FARMER-ANON-7712",
            "crop": "Maize",
            "variety": "Pioneer Hybrid",
            "location": "Eastern Dryland Sub-basin",
            "latitude": 11.12,
            "longitude": 77.40,
            "crop_stage": "Vegetative",
            "symptoms": "yellowing_chlorosis, tip_burn",
            "severity": "Medium",
            "first_symptom_time": now_minus(72.0),
            "submission_time": now_minus(14.0),
            "ai_prediction": "Abiotic stress (Salinity/heat scorch)",
            "ai_confidence": 68.0,
            "ai_alternative": "Potassium deficiency",
            "priority": "Medium",
            "priority_reason": "Standard routine triage",
            "status": "Expert Validated",
            "expert_validation": "Abiotic Nitrogen Deficiency (Not a biological disease)",
            "expert_comments": "V-shaped chlorosis extending along midrib from tip inward is diagnostic for Nitrogen deficiency, not fungal blight. Apply top-dressing urea 25 kg/acre. No fungicide needed.",
            "expert_review_time": now_minus(4.0),
            "farmer_notes": "Lower maize leaves turning yellow in V-shape.",
            "images": [
                {
                    "id": "IMG-005-A",
                    "type": "affected_area",
                    "src": DATASET_DIR / "abiotic" / "REF-ABI-001.jpg",
                    "score": 90.0,
                    "warnings": [],
                    "advice": []
                }
            ],
            "reviews": [
                {
                    "id": "REV-005",
                    "expert_category": "Abiotic",
                    "status": "rejected_ai",
                    "comments": "AI predicted Salinity scorch; actual diagnosis is severe Nitrogen deficiency. Expert override applied.",
                    "urgency": "Routine",
                    "time": now_minus(4.0)
                }
            ]
        },
        # Case 6: Bacterial Leaf Blight
        {
            "case_id": "CASE-2026-006",
            "anonymous_farmer_id": "FARMER-ANON-1082",
            "crop": "Rice",
            "variety": "IR64",
            "location": "Delta Paddy Belt",
            "latitude": 10.82,
            "longitude": 79.20,
            "crop_stage": "Tillering",
            "symptoms": "water_soaked_lesions",
            "severity": "Severe",
            "first_symptom_time": now_minus(40.0),
            "submission_time": now_minus(16.0),
            "ai_prediction": "Bacterial-like symptom",
            "ai_confidence": 76.0,
            "ai_alternative": "Fungal leaf spot",
            "priority": "High",
            "priority_reason": "Reported high symptom severity; Symptom indicates potential rapid contagion/spread risk",
            "status": "Expert Validated",
            "expert_validation": "Bacterial Leaf Blight (Xanthomonas oryzae)",
            "expert_comments": "Water-soaked stripes along leaf margins with bacterial ooze beads. Drain field water temporarily, avoid nitrogen fertilizer top-dressing.",
            "expert_review_time": now_minus(5.0),
            "farmer_notes": "Yellow-orange wavy margins starting from leaf tips.",
            "images": [
                {
                    "id": "IMG-006-A",
                    "type": "leaf_detail",
                    "src": DATASET_DIR / "bacterial" / "REF-BAC-002.jpg",
                    "score": 91.0,
                    "warnings": [],
                    "advice": []
                }
            ],
            "reviews": [
                {
                    "id": "REV-006",
                    "expert_category": "Bacterial",
                    "status": "confirmed",
                    "comments": "Confirmed Xanthomonas oryzae.",
                    "urgency": "Urgent",
                    "time": now_minus(5.0)
                }
            ]
        },
        # Case 7: Viral Mosaic Case
        {
            "case_id": "CASE-2026-007",
            "anonymous_farmer_id": "FARMER-ANON-6643",
            "crop": "Cassava",
            "variety": "Local Cassava",
            "location": "Southern Uplands",
            "latitude": 9.95,
            "longitude": 78.10,
            "crop_stage": "Vegetative",
            "symptoms": "mosaic_pattern, leaf_curling",
            "severity": "Medium",
            "first_symptom_time": now_minus(96.0),
            "submission_time": now_minus(20.0),
            "ai_prediction": "Viral-like symptom (Mosaic)",
            "ai_confidence": 80.0,
            "ai_alternative": "Genetic variegation / zinc deficiency",
            "priority": "Medium",
            "priority_reason": "Standard routine triage",
            "status": "Expert Validated",
            "expert_validation": "Cassava Mosaic Geminivirus (CMD)",
            "expert_comments": "Severe mosaic mottled leaves and twisted growth. Whitefly vector transmitted. Rogue infected plants to protect neighboring crops.",
            "expert_review_time": now_minus(6.0),
            "farmer_notes": "Leaves showing mottled yellow-green patterns and curling.",
            "images": [
                {
                    "id": "IMG-007-A",
                    "type": "whole_plant",
                    "src": DATASET_DIR / "viral" / "REF-VIR-002.jpg",
                    "score": 86.0,
                    "warnings": [],
                    "advice": []
                }
            ],
            "reviews": [
                {
                    "id": "REV-007",
                    "expert_category": "Viral",
                    "status": "confirmed",
                    "comments": "Cassava mosaic confirmed. Rogueing advised.",
                    "urgency": "Prompt",
                    "time": now_minus(6.0)
                }
            ]
        },
        # Case 8: Healthy Observation (Routine Monitoring)
        {
            "case_id": "CASE-2026-008",
            "anonymous_farmer_id": "FARMER-ANON-4419",
            "crop": "Wheat",
            "variety": "HD 2967",
            "location": "Northern Plains Block",
            "latitude": 28.60,
            "longitude": 77.20,
            "crop_stage": "Tillering",
            "symptoms": "healthy",
            "severity": "Low",
            "first_symptom_time": now_minus(20.0),
            "submission_time": now_minus(10.0),
            "ai_prediction": "Healthy crop appearance",
            "ai_confidence": 88.0,
            "ai_alternative": "Early-stage latent infection",
            "priority": "Low",
            "priority_reason": "Standard routine triage",
            "status": "Expert Validated",
            "expert_validation": "Healthy Crop - No Pathogen Detected",
            "expert_comments": "Foliage shows vigorous green coloration and uniform tillering. No fungal pustules or rust noticed. Continue standard weed management.",
            "expert_review_time": now_minus(3.0),
            "farmer_notes": "Checking crop before second irrigation.",
            "images": [
                {
                    "id": "IMG-008-A",
                    "type": "whole_plant",
                    "src": DATASET_DIR / "healthy" / "REF-HEA-002.jpg",
                    "score": 95.0,
                    "warnings": [],
                    "advice": []
                }
            ],
            "reviews": [
                {
                    "id": "REV-008",
                    "expert_category": "Healthy",
                    "status": "confirmed",
                    "comments": "Confirmed healthy stand.",
                    "urgency": "Routine",
                    "time": now_minus(3.0)
                }
            ]
        },
        # Case 9: Needs More Information (Follow-up Workflow Demonstration)
        {
            "case_id": "CASE-2026-009",
            "anonymous_farmer_id": "FARMER-ANON-9901",
            "crop": "Potato",
            "variety": "Atlantic",
            "location": "Highland Agricultural Block",
            "latitude": 11.42,
            "longitude": 76.88,
            "crop_stage": "Flowering",
            "symptoms": "wilting",
            "severity": "Medium",
            "first_symptom_time": now_minus(30.0),
            "submission_time": now_minus(15.0),
            "ai_prediction": "Wilting symptom (Water stress or vascular pathogen)",
            "ai_confidence": 54.0,
            "ai_alternative": "Bacterial wilt",
            "priority": "High",
            "priority_reason": "Low AI confidence (54.0% < 60%) — urgent expert escalation required; Critical growth stage",
            "status": "More Information Required",
            "expert_comments": "Please cut the lower stem at soil level and place in a glass of clear water. Report whether milky bacterial streaming oozes out.",
            "expert_review_time": now_minus(5.0),
            "farmer_notes": "Single plant wilting while neighboring plants look okay.",
            "images": [
                {
                    "id": "IMG-009-A",
                    "type": "affected_area",
                    "src": DATASET_DIR / "healthy" / "REF-HEA-001.jpg",
                    "score": 82.0,
                    "warnings": [],
                    "advice": []
                }
            ],
            "reviews": [
                {
                    "id": "REV-009",
                    "expert_category": "Bacterial",
                    "status": "more_info_needed",
                    "comments": "Stem ooze test required to distinguish Ralstonia from Fusarium.",
                    "urgency": "Prompt",
                    "time": now_minus(5.0)
                }
            ]
        },
        # Case 10: Dark / Underexposed Edge Case
        {
            "case_id": "CASE-2026-010",
            "anonymous_farmer_id": "FARMER-ANON-2209",
            "crop": "Tomato",
            "variety": "Pusa Ruby",
            "location": "Green Valley District",
            "latitude": 11.26,
            "longitude": 77.12,
            "crop_stage": "Fruiting",
            "symptoms": "leaf_spots",
            "severity": "Medium",
            "first_symptom_time": now_minus(48.0),
            "submission_time": now_minus(8.0),
            "ai_prediction": "Fungal-like symptom",
            "ai_confidence": 57.0,
            "ai_alternative": "Unclassified foliar symptom",
            "priority": "High",
            "priority_reason": "Low AI confidence (57.0% < 60%) — urgent expert escalation required; Image quality degraded",
            "status": "Submitted",
            "farmer_notes": "Taken in evening dusk under canopy shade.",
            "images": [
                {
                    "id": "IMG-010-A",
                    "type": "leaf_detail",
                    "src": TEST_IMG_DIR / "edge_case_dark.jpg",
                    "score": 38.0,
                    "warnings": ["Image is too dark (average brightness: 23.5 < 40)"],
                    "advice": ["The photo is quite dark. Please take another photo in natural daylight or avoid heavy shadows."]
                }
            ]
        },
        # Case 11: Rapid Spread Powdery Mildew
        {
            "case_id": "CASE-2026-011",
            "anonymous_farmer_id": "FARMER-ANON-7788",
            "crop": "Tomato",
            "variety": "Cherry Tomato",
            "location": "Suburban Greenhouse Cluster",
            "latitude": 12.92,
            "longitude": 77.58,
            "crop_stage": "Flowering",
            "symptoms": "powdery_coating",
            "severity": "High",
            "first_symptom_time": now_minus(52.0),
            "submission_time": now_minus(22.0),
            "ai_prediction": "Fungal-like symptom (Powdery mildew)",
            "ai_confidence": 85.0,
            "ai_alternative": "Abiotic dust/pesticide residue",
            "priority": "High",
            "priority_reason": "Reported high symptom severity; Critical growth stage (flowering/fruiting)",
            "status": "Expert Validated",
            "expert_validation": "Powdery Mildew (Oidium neolycopersici)",
            "expert_comments": "White talcum-like fungal powder on upper leaf surfaces. Apply wettable sulfur 2g/L or potassium bicarbonate.",
            "expert_review_time": now_minus(10.0),
            "farmer_notes": "White powder spreading over leaves in greenhouse.",
            "images": [
                {
                    "id": "IMG-011-A",
                    "type": "leaf_detail",
                    "src": DATASET_DIR / "fungal" / "REF-FUN-001.jpg",
                    "score": 89.0,
                    "warnings": [],
                    "advice": []
                }
            ],
            "reviews": [
                {
                    "id": "REV-011",
                    "expert_category": "Fungal",
                    "status": "confirmed",
                    "comments": "Confirmed greenhouse powdery mildew.",
                    "urgency": "Urgent",
                    "time": now_minus(10.0)
                }
            ]
        },
        # Case 12: Resubmitted Case with Follow-up Evidence
        {
            "case_id": "CASE-2026-012",
            "anonymous_farmer_id": "FARMER-ANON-1154",
            "crop": "Rice",
            "variety": "Swarna",
            "location": "Delta Paddy Belt",
            "latitude": 10.79,
            "longitude": 79.16,
            "crop_stage": "Tillering",
            "symptoms": "rust_pustules, yellowing_chlorosis",
            "severity": "Medium",
            "first_symptom_time": now_minus(60.0),
            "submission_time": now_minus(24.0),
            "ai_prediction": "Fungal-like symptom (Rust)",
            "ai_confidence": 82.0,
            "ai_alternative": "Nutrient deficiency",
            "priority": "Medium",
            "priority_reason": "Symptom indicates potential rapid contagion/spread risk",
            "status": "Under Review",
            "farmer_notes": "Orange-brown pustules on leaf blades.\n[Resubmission update]: Added clear close-up of pustules scraping onto white paper as requested.",
            "images": [
                {
                    "id": "IMG-012-A",
                    "type": "affected_area",
                    "src": DATASET_DIR / "fungal" / "REF-FUN-002.jpg",
                    "score": 93.0,
                    "warnings": [],
                    "advice": []
                }
            ]
        }
    ]

    for c in demo_cases:
        db_case = Case(
            case_id=c["case_id"],
            anonymous_farmer_id=c["anonymous_farmer_id"],
            crop=c["crop"],
            variety=c.get("variety"),
            location=c["location"],
            latitude=c.get("latitude"),
            longitude=c.get("longitude"),
            crop_stage=c["crop_stage"],
            symptoms=c["symptoms"],
            severity=c["severity"],
            first_symptom_time=c["first_symptom_time"],
            submission_time=c["submission_time"],
            ai_prediction=c.get("ai_prediction"),
            ai_confidence=c.get("ai_confidence"),
            ai_alternative=c.get("ai_alternative"),
            priority=c["priority"],
            priority_reason=c.get("priority_reason"),
            status=c["status"],
            expert_validation=c.get("expert_validation"),
            expert_comments=c.get("expert_comments"),
            expert_review_time=c.get("expert_review_time"),
            farmer_notes=c.get("farmer_notes"),
            environmental_notes=c.get("environmental_notes"),
            rainfall_recent=c.get("rainfall_recent", "Unknown"),
            humidity_level=c.get("humidity_level", "Unknown"),
            temperature_band=c.get("temperature_band", "Unknown"),
            recent_weather_event=c.get("recent_weather_event", "None"),
            irrigation_status=c.get("irrigation_status", "Unknown"),
            soil_moisture_observation=c.get("soil_moisture_observation", "Unknown"),
            field_condition=c.get("field_condition", "Unknown")
        )
        db.add(db_case)

        # Add images
        for img in c.get("images", []):
            url = copy_to_uploads(img["src"], c["case_id"], img["type"])
            img_rec = ImageRecord(
                image_id=img["id"],
                case_id=c["case_id"],
                image_type=img["type"],
                file_path=url,
                quality_score=img["score"],
                quality_warnings=json.dumps(img["warnings"]),
                farmer_advice=json.dumps(img["advice"]),
                source="Synthetic Demonstration Dataset",
                license="CC-BY-4.0 (Non-identifiable synthetic crop asset)"
            )
            db.add(img_rec)

        # Add reviews
        for rev in c.get("reviews", []):
            rev_rec = ExpertReview(
                review_id=rev["id"],
                case_id=c["case_id"],
                expert_category=rev["expert_category"],
                validation_status=rev["status"],
                comments=rev["comments"],
                urgency=rev["urgency"],
                reviewed_at=rev["time"]
            )
            db.add(rev_rec)

        db.add(AuditLog(
            case_id=c["case_id"],
            action="SEEDED_DEMO_CASE",
            actor_role="System",
            details=f"Synthetic demo case initialized with status: {c['status']}"
        ))

    db.commit()

    # Save demo cases to data/sample_cases.json
    export_list = []
    for c in demo_cases:
        item = dict(c)
        item["first_symptom_time"] = c["first_symptom_time"].isoformat()
        item["submission_time"] = c["submission_time"].isoformat()
        if item.get("expert_review_time"):
            item["expert_review_time"] = c["expert_review_time"].isoformat()
        # strip non-serializable Path objects from images
        serializable_images = []
        for im in item.get("images", []):
            im_copy = dict(im)
            im_copy["src"] = str(im["src"].name)
            serializable_images.append(im_copy)
        item["images"] = serializable_images
        if "reviews" in item:
            for r in item["reviews"]:
                r["time"] = r["time"].isoformat()
        export_list.append(item)

    json_file = DATA_DIR / "sample_cases.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(export_list, f, indent=2)

    db.close()
    print(f"Successfully seeded {len(demo_cases)} synthetic demo cases and updated sample_cases.json.")


if __name__ == "__main__":
    seed_database()
