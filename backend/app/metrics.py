"""
Metrics Engine for Agricultural Disease Observation.
Calculates T_review, report completeness, image usability, and dashboard KPIs.
Ensures strict labeling of baseline assumptions vs prototype measurements.
"""

import json
from typing import Dict, Any, List, Optional
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


def compute_regional_analytics(
    db: Session,
    crop: Optional[str] = None,
    region: Optional[str] = None,
    severity: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """
    Computes aggregated regional epidemiology and microclimate risk analytics.
    Supports multi-criteria filtering by crop, region, severity, priority, and status.
    Clearly labeled as prototype/simulated data.
    """
    query = db.query(Case)
    if crop:
        query = query.filter(Case.crop.ilike(f"%{crop}%"))
    if region:
        query = query.filter(Case.location.ilike(f"%{region}%"))
    if severity:
        query = query.filter(Case.severity == severity)
    if priority:
        query = query.filter(Case.priority == priority)
    if status:
        query = query.filter(Case.status == status)

    cases: List[Case] = query.all()

    # Aggregate by region / location
    region_groups: Dict[str, List[Case]] = {}
    for c in cases:
        loc = c.location or "Unspecified Location"
        if loc not in region_groups:
            region_groups[loc] = []
        region_groups[loc].append(c)

    regions_data = []
    active_alerts = []

    for loc, loc_cases in region_groups.items():
        total_loc = len(loc_cases)
        high_prio = sum(1 for c in loc_cases if c.priority == "High")
        urgent_prio = sum(1 for c in loc_cases if c.priority == "High" or (c.severity in ["High", "Severe"]))
        validated = sum(1 for c in loc_cases if c.status == "Expert Validated")
        needing_info = sum(1 for c in loc_cases if c.status == "More Information Required")
        under_review = sum(1 for c in loc_cases if c.status in ["Submitted", "Under Review"])

        # Coordinates (approximate average)
        lats = [c.latitude for c in loc_cases if c.latitude is not None]
        lons = [c.longitude for c in loc_cases if c.longitude is not None]
        avg_lat = round(sum(lats) / len(lats), 2) if lats else None
        avg_lon = round(sum(lons) / len(lons), 2) if lons else None

        # Disease / symptom pattern
        disease_counts: Dict[str, int] = {}
        for c in loc_cases:
            diag = c.expert_validation or c.ai_prediction or "Undetermined"
            disease_counts[diag] = disease_counts.get(diag, 0) + 1
        dominant_disease = max(disease_counts.items(), key=lambda x: x[1])[0] if disease_counts else "None"

        # Moisture / microclimate risk: count cases with high moisture, flood, or continuous rain
        moisture_risk_count = sum(
            1 for c in loc_cases
            if (c.rainfall_recent in ["Heavy (Flood/Downpour)", "Moderate"] or
                c.humidity_level in ["High (>80%)", "Very High / Saturated"] or
                c.soil_moisture_observation in ["Waterlogged", "Excess / Wet"] or
                c.recent_weather_event in ["Continuous Rain", "Hailstorm"])
        )

        # Risk level logic
        if high_prio >= 4:
            risk_level = "Outbreak Alert"
            badge_class = "danger"
        elif high_prio >= 2 or (total_loc >= 4 and moisture_risk_count >= 2):
            risk_level = "Elevated Watch"
            badge_class = "warning"
        elif high_prio >= 1:
            risk_level = "Moderate Attention"
            badge_class = "info"
        else:
            risk_level = "Normal Observation"
            badge_class = "success"

        # Unique crops
        crops_in_region = sorted(list(set(c.crop for c in loc_cases if c.crop)))

        reg_entry = {
            "region_name": loc,
            "approx_latitude": avg_lat,
            "approx_longitude": avg_lon,
            "total_cases": total_loc,
            "high_priority_count": high_prio,
            "validated_count": validated,
            "under_review_count": under_review,
            "needing_info_count": needing_info,
            "dominant_disease": dominant_disease,
            "moisture_risk_count": moisture_risk_count,
            "risk_level": risk_level,
            "badge_class": badge_class,
            "crops": crops_in_region
        }
        regions_data.append(reg_entry)

        # Trigger active alert if Elevated Watch or Outbreak Alert
        if risk_level in ["Elevated Watch", "Outbreak Alert"]:
            active_alerts.append({
                "region": loc,
                "risk_level": risk_level,
                "high_priority_count": high_prio,
                "total_cases": total_loc,
                "dominant_disease": dominant_disease,
                "message": (
                    f"Cluster notification: {high_prio} high-priority case(s) detected in {loc}. "
                    f"Predominant observation pattern: {dominant_disease}. "
                    f"Moisture-elevated observations: {moisture_risk_count}."
                ),
                "recommended_action": (
                    "Deploy extension field officer for in-person sample collection. "
                    "Alert neighboring farms on preventative sanitation."
                ),
                "disclaimer": "Simulated regional alert — prototype decision support."
            })

    # Sort regions by high_priority_count desc, then total_cases desc
    regions_data.sort(key=lambda r: (r["high_priority_count"], r["total_cases"]), reverse=True)

    # Summaries across filtered cases
    crop_counts: Dict[str, int] = {}
    severity_counts: Dict[str, int] = {"Low": 0, "Medium": 0, "High": 0, "Severe": 0}
    priority_counts: Dict[str, int] = {"High": 0, "Medium": 0, "Low": 0}

    for c in cases:
        crop_counts[c.crop] = crop_counts.get(c.crop, 0) + 1
        if c.severity in severity_counts:
            severity_counts[c.severity] += 1
        else:
            severity_counts[c.severity] = 1
        if c.priority in priority_counts:
            priority_counts[c.priority] += 1

    return {
        "disclaimer": "Prototype / simulated regional summary for decision support — not real-world disease outbreak surveillance.",
        "filters_applied": {
            "crop": crop,
            "region": region,
            "severity": severity,
            "priority": priority,
            "status": status
        },
        "total_matching_cases": len(cases),
        "total_regions": len(regions_data),
        "active_alerts_count": len(active_alerts),
        "active_alerts": active_alerts,
        "regions": regions_data,
        "crop_distribution": crop_counts,
        "severity_distribution": severity_counts,
        "priority_distribution": priority_counts
    }


def compute_t_review_analytics(db: Session) -> Dict[str, Any]:
    """
    Computes detailed T_review operational latency analytics:
    T_review = expert_review_time - first_symptom_time (hours).
    Also computes submission_to_review = expert_review_time - submission_time (hours).
    Reports mean, median, min, max, and count overall and grouped by priority, crop, and region.
    """
    import statistics

    def safe_stats(values: List[float]) -> Dict[str, Any]:
        if not values:
            return {"count": 0, "mean": None, "median": None, "min": None, "max": None}
        return {
            "count": len(values),
            "mean": round(float(statistics.mean(values)), 1),
            "median": round(float(statistics.median(values)), 1),
            "min": round(float(min(values)), 1),
            "max": round(float(max(values)), 1)
        }

    cases = db.query(Case).all()
    validated_cases = [c for c in cases if c.status == "Expert Validated" and c.expert_review_time]

    overall_t_review_hours: List[float] = []
    overall_sub_review_hours: List[float] = []

    by_priority: Dict[str, List[float]] = {"High": [], "Medium": [], "Low": []}
    by_crop: Dict[str, List[float]] = {}
    by_region: Dict[str, List[float]] = {}

    for c in validated_cases:
        if c.expert_review_time and c.first_symptom_time:
            t_first = c.first_symptom_time.replace(tzinfo=timezone.utc) if c.first_symptom_time.tzinfo is None else c.first_symptom_time
            t_review = c.expert_review_time.replace(tzinfo=timezone.utc) if c.expert_review_time.tzinfo is None else c.expert_review_time
            t_sub = c.submission_time.replace(tzinfo=timezone.utc) if c.submission_time.tzinfo is None else c.submission_time

            hrs_from_symptom = max(0.1, (t_review - t_first).total_seconds() / 3600.0)
            hrs_from_sub = max(0.05, (t_review - t_sub).total_seconds() / 3600.0)

            overall_t_review_hours.append(hrs_from_symptom)
            overall_sub_review_hours.append(hrs_from_sub)

            # By priority
            prio = c.priority if c.priority in by_priority else "Medium"
            by_priority[prio].append(hrs_from_symptom)

            # By crop
            crop = c.crop or "Unknown"
            if crop not in by_crop:
                by_crop[crop] = []
            by_crop[crop].append(hrs_from_symptom)

            # By region
            reg = c.location or "Unknown"
            if reg not in by_region:
                by_region[reg] = []
            by_region[reg].append(hrs_from_symptom)

    priority_stats = {p: safe_stats(vals) for p, vals in by_priority.items()}
    crop_stats = {crop: safe_stats(vals) for crop, vals in by_crop.items()}
    region_stats = {reg: safe_stats(vals) for reg, vals in by_region.items()}

    return {
        "disclaimer": "Simulated latency measured across prototype database records — illustrative operational metrics.",
        "baseline_assumption_hours": 120.0,
        "mvp_target_hours": 24.0,
        "total_validated_cases": len(validated_cases),
        "overall_t_review": safe_stats(overall_t_review_hours),
        "overall_submission_to_review": safe_stats(overall_sub_review_hours),
        "by_priority": priority_stats,
        "by_crop": crop_stats,
        "by_region": region_stats
    }


def compute_ai_monitoring_metrics(db: Session) -> Dict[str, Any]:
    """
    Computes live AI performance monitoring metrics, confidence distribution,
    escalation rate, and loads benchmark evaluation results.
    """
    from pathlib import Path
    from backend.app.database import BASE_DIR

    cases = db.query(Case).all()
    reviews = db.query(ExpertReview).all()

    # Confidence distribution buckets
    buckets = {
        "<50%": 0,
        "50-59%": 0,
        "60-69%": 0,
        "70-79%": 0,
        "80-89%": 0,
        "90-100%": 0
    }
    cases_with_conf = [c for c in cases if c.ai_confidence is not None]
    low_confidence_count = 0

    for c in cases_with_conf:
        conf = c.ai_confidence
        if conf < 50.0:
            buckets["<50%"] += 1
        elif conf < 60.0:
            buckets["50-59%"] += 1
        elif conf < 70.0:
            buckets["60-69%"] += 1
        elif conf < 80.0:
            buckets["70-79%"] += 1
        elif conf < 90.0:
            buckets["80-89%"] += 1
        else:
            buckets["90-100%"] += 1

        if conf < 60.0:
            low_confidence_count += 1

    total_with_conf = len(cases_with_conf)
    escalation_rate = round((low_confidence_count / total_with_conf) * 100.0, 1) if total_with_conf > 0 else 0.0

    # Expert agreement vs override stats
    confirmed = sum(1 for r in reviews if r.validation_status == "confirmed")
    rejected_ai = sum(1 for r in reviews if r.validation_status == "rejected_ai")
    more_info = sum(1 for r in reviews if r.validation_status == "more_info_needed")
    uncertain = sum(1 for r in reviews if r.validation_status not in ["confirmed", "rejected_ai", "more_info_needed"])
    total_reviews = len(reviews)

    agreement_rate = round((confirmed / total_reviews) * 100.0, 1) if total_reviews > 0 else None
    override_rate = round((rejected_ai / total_reviews) * 100.0, 1) if total_reviews > 0 else None

    # Load static benchmark evaluation results from ml/models/evaluation_results.json
    eval_file = BASE_DIR / "ml" / "models" / "evaluation_results.json"
    benchmark_metrics = None
    if eval_file.exists():
        try:
            with open(eval_file, "r") as f:
                benchmark_metrics = json.load(f)
                if isinstance(benchmark_metrics, dict):
                    benchmark_metrics.setdefault("model_architecture", "MobileNetV3-Small")
        except Exception:
            benchmark_metrics = None

    return {
        "disclaimer": "AI metrics reflect prototype decision-support performance and simulated triage. Expert review remains authoritative.",
        "total_cases_evaluated": len(cases),
        "cases_with_ai_confidence": total_with_conf,
        "confidence_distribution_buckets": buckets,
        "low_confidence_threshold": 60.0,
        "low_confidence_cases": low_confidence_count,
        "escalation_rate_percent": escalation_rate,
        "expert_review_metrics": {
            "total_reviews": total_reviews,
            "confirmed_ai_agreements": confirmed,
            "expert_overrides_rejections": rejected_ai,
            "more_information_requests": more_info,
            "uncertain_reviews": uncertain,
            "agreement_rate_percent": agreement_rate,
            "override_rate_percent": override_rate
        },
        "model_benchmark": benchmark_metrics or {
            "model_architecture": "MobileNetV3-Small",
            "status": "Benchmark file pending or not loaded"
        }
    }

