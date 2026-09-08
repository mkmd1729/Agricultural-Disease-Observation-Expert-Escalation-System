"""
Metrics Engine for Agricultural Disease Observation.
Calculates T_review, report completeness, image usability, and dashboard KPIs.
Ensures strict labeling of baseline assumptions vs prototype measurements.
"""

from typing import Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.app.models import Case, ImageRecord, ExpertReview


def compute_metrics_summary(db: Session) -> Dict[str, Any]:
    """
    Computes all operational and research metrics across cases in the database.
    Calculates T_review = expert_review_time - first_symptom_time.
    """
    cases: List[Case] = db.query(Case).all()
    images: List[ImageRecord] = db.query(ImageRecord).all()
    
    total_obs = len(cases)
    pending_reviews = sum(1 for c in cases if c.status in ["Submitted", "Under Review"])
    high_priority = sum(1 for c in cases if c.priority == "High")
    validated_cases = [c for c in cases if c.status == "Expert Validated" and c.expert_review_time]
    low_confidence = sum(1 for c in cases if c.ai_confidence and c.ai_confidence < 60.0)
    needing_info = sum(1 for c in cases if c.status == "More Information Required")

    # Calculate T_review (hours)
    t_review_deltas = []
    submission_to_review_deltas = []
    for c in validated_cases:
        if c.expert_review_time and c.first_symptom_time:
            # Handle timezone-aware / naive conversions safely
            t_first = c.first_symptom_time.replace(tzinfo=timezone.utc) if c.first_symptom_time.tzinfo is None else c.first_symptom_time
            t_review = c.expert_review_time.replace(tzinfo=timezone.utc) if c.expert_review_time.tzinfo is None else c.expert_review_time
            t_sub = c.submission_time.replace(tzinfo=timezone.utc) if c.submission_time.tzinfo is None else c.submission_time
            
            hours_from_first = max(0.1, (t_review - t_first).total_seconds() / 3600.0)
            hours_from_sub = max(0.05, (t_review - t_sub).total_seconds() / 3600.0)
            t_review_deltas.append(hours_from_first)
            submission_to_review_deltas.append(hours_from_sub)

    avg_t_review = round(sum(t_review_deltas) / len(t_review_deltas), 1) if t_review_deltas else None
    avg_sub_to_review = round(sum(submission_to_review_deltas) / len(submission_to_review_deltas), 1) if submission_to_review_deltas else None

    # Report completeness (checking if crop, symptoms, stage, location, image, first_symptom_time present)
    complete_count = 0
    for c in cases:
        has_crop = bool(c.crop)
        has_symptoms = bool(c.symptoms)
        has_stage = bool(c.crop_stage)
        has_location = bool(c.location)
        has_first_time = bool(c.first_symptom_time)
        has_img = len(c.images) > 0
        if has_crop and has_symptoms and has_stage and has_location and has_first_time and has_img:
            complete_count += 1
    completeness_rate = round((complete_count / total_obs) * 100.0, 1) if total_obs > 0 else 0.0

    # Image usability
    usable_images = sum(1 for img in images if img.quality_score >= 20.0)
    image_usability_rate = round((usable_images / len(images)) * 100.0, 1) if images else 100.0

    # Expert re-contact rate (percentage of reviewed cases where more info was required)
    reviewed_total = len(validated_cases) + needing_info
    recontact_rate = round((needing_info / reviewed_total) * 100.0, 1) if reviewed_total > 0 else 0.0

    # AI Agreement rate (cases where expert confirmed AI proposal)
    confirmed_ai = 0
    expert_reviewed_reviews = db.query(ExpertReview).all()
    for rev in expert_reviewed_reviews:
        if rev.validation_status == "confirmed":
            confirmed_ai += 1
    agreement_rate = round((confirmed_ai / len(expert_reviewed_reviews)) * 100.0, 1) if expert_reviewed_reviews else None

    # Breakdown dictionaries
    cases_by_crop: Dict[str, int] = {}
    cases_by_location: Dict[str, int] = {}
    cases_by_symptom: Dict[str, int] = {}
    cases_by_priority: Dict[str, int] = {"High": 0, "Medium": 0, "Low": 0}
    cases_by_status: Dict[str, int] = {"Submitted": 0, "Under Review": 0, "More Information Required": 0, "Expert Validated": 0}

    for c in cases:
        cases_by_crop[c.crop] = cases_by_crop.get(c.crop, 0) + 1
        cases_by_location[c.location] = cases_by_location.get(c.location, 0) + 1
        cases_by_priority[c.priority] = cases_by_priority.get(c.priority, 0) + 1
        cases_by_status[c.status] = cases_by_status.get(c.status, 0) + 1
        
        # Split symptoms
        sym_list = [s.strip() for s in c.symptoms.split(",") if s.strip()]
        for s in sym_list:
            cases_by_symptom[s] = cases_by_symptom.get(s, 0) + 1

    # Before vs After comparison table
    comparison_table = [
        {
            "metric": "Time from first symptom to useful expert review",
            "baseline": "120 hours (illustrative assumption)",
            "mvp_target": "24 hours",
            "mvp_result": f"{avg_t_review} hours" if avg_t_review is not None else "Pending test cases",
            "evaluation_label": "Prototype/simulated evaluation — not field validation"
        },
        {
            "metric": "Complete standardized reports",
            "baseline": "35% (illustrative assumption)",
            "mvp_target": "85%",
            "mvp_result": f"{completeness_rate}%",
            "evaluation_label": "Measured across prototype database cases"
        },
        {
            "metric": "Usable photographic evidence",
            "baseline": "40% (illustrative assumption)",
            "mvp_target": "85%",
            "mvp_result": f"{image_usability_rate}%",
            "evaluation_label": "Measured across prototype database images"
        },
        {
            "metric": "Follow-up / Re-contact requests",
            "baseline": "65% (illustrative assumption)",
            "mvp_target": "15%",
            "mvp_result": f"{recontact_rate}%",
            "evaluation_label": "Measured across reviewed prototype cases"
        }
    ]

    return {
        "total_observations": total_obs,
        "pending_reviews": pending_reviews,
        "high_priority_cases": high_priority,
        "expert_validated_cases": len(validated_cases),
        "low_confidence_cases": low_confidence,
        "cases_needing_info": needing_info,
        "avg_t_review_hours": avg_t_review,
        "avg_submission_to_review_hours": avg_sub_to_review,
        "report_completeness_rate": completeness_rate,
        "image_usability_rate": image_usability_rate,
        "expert_recontact_rate": recontact_rate,
        "ai_agreement_rate": agreement_rate,
        "cases_by_crop": cases_by_crop,
        "cases_by_location": cases_by_location,
        "cases_by_symptom_category": cases_by_symptom,
        "cases_by_priority": cases_by_priority,
        "cases_by_status": cases_by_status,
        "comparison_table": comparison_table
    }
