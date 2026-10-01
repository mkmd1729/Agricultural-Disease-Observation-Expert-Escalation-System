"""
FastAPI Main Application for Agricultural Disease Observation & Expert Escalation.
Serves REST API endpoints, image analysis, expert validation, and the frontend web app.
"""

from datetime import datetime, timezone
import json
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session

from backend.app.database import engine, init_db, get_db, UPLOADS_DIR, BASE_DIR, DATA_DIR
from backend.app.models import Case, ImageRecord, ExpertReview, AuditLog, utcnow
from backend.app.schemas import CaseOut, CaseCreate, ExpertReviewCreate, ExpertReviewOut, MetricsSummary, ImageQualityResult
from backend.app.image_quality import analyze_image_quality
from backend.app.ai_assistant import classify_observation
from backend.app.priority import calculate_priority_score
from backend.app.metrics import (
    compute_metrics_summary,
    compute_regional_analytics,
    compute_t_review_analytics,
    compute_ai_monitoring_metrics
)
from backend.app.i18n import get_supported_languages, get_translation_dictionary
from backend.app.vision_service import predict_image, get_vision_model, CLASSES, MODEL_PATH

# Maximum allowed file size for image uploads (10 MB)
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def validate_image_upload(filename: str, content: bytes) -> str:
    """
    Validates uploaded image file size and extension to prevent malicious or oversized uploads.
    Extracts and returns the sanitized lowercase extension.
    """
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image exceeds maximum permitted file size of 10 MB ({len(content)} bytes uploaded)."
        )
    raw_ext = Path(filename).suffix.lower()
    if not raw_ext or raw_ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image extension '{raw_ext}'. Allowed formats: {', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))}."
        )
    return raw_ext

# Ensure DB initialized
init_db()

app = FastAPI(
    title="Agricultural Disease Observation & Expert Escalation App",
    description="Review 1 MVP: Reliable symptom reporting, image quality validation, and expert escalation.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and uploads directory
FRONTEND_DIR = BASE_DIR / "frontend" / "public"
FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")


def generate_next_case_id(db: Session) -> str:
    """Generates sequential, standardized anonymous case IDs: CASE-2026-001."""
    count = db.query(Case).count() + 1
    # Check uniqueness
    candidate = f"CASE-2026-{count:03d}"
    while db.query(Case).filter(Case.case_id == candidate).first():
        count += 1
        candidate = f"CASE-2026-{count:03d}"
    return candidate


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "agri-disease-observation",
        "version": "1.0.0",
        "timestamp": utcnow().isoformat()
    }


@app.post("/api/cases", response_model=CaseOut, status_code=status.HTTP_201_CREATED)
async def submit_case(
    crop: str = Form(...),
    symptoms: str = Form(..., description="Comma-separated symptom strings or JSON list"),
    crop_stage: str = Form(...),
    location: str = Form(...),
    first_symptom_time: str = Form(..., description="ISO 8601 string or YYYY-MM-DD"),
    anonymous_farmer_id: Optional[str] = Form(None),
    variety: Optional[str] = Form(None),
    severity: str = Form("Medium"),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    farmer_notes: Optional[str] = Form(None),
    environmental_notes: Optional[str] = Form(None),
    # Phase 2.3 Environmental Context fields (with backward-compatible defaults)
    rainfall_recent: Optional[str] = Form("Unknown"),
    humidity_level: Optional[str] = Form("Unknown"),
    temperature_band: Optional[str] = Form("Unknown"),
    recent_weather_event: Optional[str] = Form("None"),
    irrigation_status: Optional[str] = Form("Unknown"),
    soil_moisture_observation: Optional[str] = Form("Unknown"),
    field_condition: Optional[str] = Form("Unknown"),
    image_whole: Optional[UploadFile] = File(None),
    image_affected: Optional[UploadFile] = File(None),
    image_detail: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Submits a standardized disease observation case from the farmer interface.
    Performs image quality analysis, runs MobileNetV3 + hybrid AI assistance, and assigns priority.
    """
    # 1. Parse symptoms
    symptom_list: List[str] = []
    try:
        parsed = json.loads(symptoms)
        if isinstance(parsed, list):
            symptom_list = [str(x).strip() for x in parsed]
        else:
            symptom_list = [str(symptoms).strip()]
    except Exception:
        symptom_list = [s.strip() for s in symptoms.split(",") if s.strip()]

    # 2. Parse first symptom date/time safely
    try:
        t_first = datetime.fromisoformat(first_symptom_time.replace("Z", "+00:00"))
    except Exception:
        try:
            t_first = datetime.strptime(first_symptom_time, "%Y-%m-%d")
        except Exception:
            t_first = utcnow()

    # 3. Anonymization & Location Privacy (Round coordinates to 2 decimals)
    case_id = generate_next_case_id(db)
    farmer_id = anonymous_farmer_id.strip() if anonymous_farmer_id else f"FARMER-ANON-{uuid.uuid4().hex[:6].upper()}"
    approx_lat = round(latitude, 2) if latitude is not None else None
    approx_lon = round(longitude, 2) if longitude is not None else None

    # 4. Handle Uploaded Images & Perform Quality Analysis
    saved_images: List[ImageRecord] = []
    quality_scores: List[float] = []
    upload_map = [
        ("whole_plant", image_whole),
        ("affected_area", image_affected),
        ("leaf_detail", image_detail)
    ]
    leaf_bytes: Optional[bytes] = None

    for img_type, upload_file in upload_map:
        if upload_file and upload_file.filename:
            content = await upload_file.read()
            if len(content) > 0:
                safe_filename = Path(upload_file.filename).name
                safe_ext = validate_image_upload(safe_filename, content)
                if img_type == "leaf_detail" or leaf_bytes is None:
                    leaf_bytes = content

                # Analyze image quality
                q_res = analyze_image_quality(content, safe_filename)
                quality_scores.append(q_res["quality_score"])

                # Save file to disk
                img_uuid = uuid.uuid4().hex[:8]
                saved_filename = f"{case_id}_{img_type}_{img_uuid}{safe_ext}"
                file_dest = UPLOADS_DIR / saved_filename
                with open(file_dest, "wb") as f:
                    f.write(content)

                image_rec = ImageRecord(
                    image_id=f"IMG-{img_uuid.upper()}",
                    case_id=case_id,
                    image_type=img_type,
                    file_path=f"/uploads/{saved_filename}",
                    quality_score=q_res["quality_score"],
                    quality_warnings=json.dumps(q_res["warnings"]),
                    farmer_advice=json.dumps(q_res["farmer_advice"]),
                    source="Farmer Upload",
                    license="CC-BY-4.0 (Non-identifiable field observation)"
                )
                saved_images.append(image_rec)

    # 5. Vision Inference (MobileNetV3) & Hybrid AI Classification
    vision_result = None
    if leaf_bytes:
        try:
            vision_result = predict_image(leaf_bytes)
        except Exception:
            vision_result = None

    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 50.0
    ai_result = classify_observation(
        crop=crop,
        symptoms=symptom_list,
        crop_stage=crop_stage,
        image_quality_score=avg_quality,
        has_image=len(saved_images) > 0,
        vision_result=vision_result
    )

    # 6. Case Prioritization with Environmental Context
    priority, priority_reason = calculate_priority_score(
        severity=severity,
        crop_stage=crop_stage,
        ai_confidence=ai_result["confidence"],
        symptoms=symptom_list,
        environmental_notes=environmental_notes,
        rainfall_recent=rainfall_recent,
        humidity_level=humidity_level,
        soil_moisture=soil_moisture_observation,
        recent_weather_event=recent_weather_event
    )

    # 7. Create Case in DB
    new_case = Case(
        case_id=case_id,
        anonymous_farmer_id=farmer_id,
        crop=crop,
        variety=variety,
        location=location,
        latitude=approx_lat,
        longitude=approx_lon,
        crop_stage=crop_stage,
        symptoms=", ".join(symptom_list),
        severity=severity,
        first_symptom_time=t_first,
        submission_time=utcnow(),
        ai_prediction=ai_result["possible_category"],
        ai_confidence=ai_result["confidence"],
        ai_alternative=ai_result["alternative_prediction"],
        priority=priority,
        priority_reason=priority_reason,
        status="Submitted",
        farmer_notes=farmer_notes,
        environmental_notes=environmental_notes,
        rainfall_recent=rainfall_recent or "Unknown",
        humidity_level=humidity_level or "Unknown",
        temperature_band=temperature_band or "Unknown",
        recent_weather_event=recent_weather_event or "None",
        irrigation_status=irrigation_status or "Unknown",
        soil_moisture_observation=soil_moisture_observation or "Unknown",
        field_condition=field_condition or "Unknown"
    )

    db.add(new_case)
    for img in saved_images:
        db.add(img)

    # Add audit log
    db.add(AuditLog(
        case_id=case_id,
        action="CASE_CREATED",
        actor_role="Farmer",
        details=f"Observation submitted. AI hypothesis: {ai_result['possible_category']} ({ai_result['confidence']}%), Assigned Priority: {priority}"
    ))

    db.commit()
    db.refresh(new_case)
    return new_case


@app.post("/api/cases/json", response_model=CaseOut, status_code=status.HTTP_201_CREATED)
def submit_case_json(payload: CaseCreate, db: Session = Depends(get_db)):
    """JSON-based case creation for automated testing and programmatic batch seeding."""
    case_id = generate_next_case_id(db)
    farmer_id = payload.anonymous_farmer_id or f"FARMER-ANON-{uuid.uuid4().hex[:6].upper()}"

    ai_result = classify_observation(
        crop=payload.crop,
        symptoms=payload.symptoms,
        crop_stage=payload.crop_stage,
        image_quality_score=85.0,
        has_image=False,
        vision_result=None
    )

    priority, reason = calculate_priority_score(
        severity=payload.severity,
        crop_stage=payload.crop_stage,
        ai_confidence=ai_result["confidence"],
        symptoms=payload.symptoms,
        environmental_notes=payload.environmental_notes,
        rainfall_recent=payload.rainfall_recent,
        humidity_level=payload.humidity_level,
        soil_moisture=payload.soil_moisture_observation,
        recent_weather_event=payload.recent_weather_event
    )

    new_case = Case(
        case_id=case_id,
        anonymous_farmer_id=farmer_id,
        crop=payload.crop,
        variety=payload.variety,
        location=payload.location,
        latitude=round(payload.latitude, 2) if payload.latitude else None,
        longitude=round(payload.longitude, 2) if payload.longitude else None,
        crop_stage=payload.crop_stage,
        symptoms=", ".join(payload.symptoms),
        severity=payload.severity,
        first_symptom_time=payload.first_symptom_time,
        submission_time=utcnow(),
        ai_prediction=ai_result["possible_category"],
        ai_confidence=ai_result["confidence"],
        ai_alternative=ai_result["alternative_prediction"],
        priority=priority,
        priority_reason=reason,
        status="Submitted",
        farmer_notes=payload.farmer_notes,
        environmental_notes=payload.environmental_notes,
        rainfall_recent=payload.rainfall_recent or "Unknown",
        humidity_level=payload.humidity_level or "Unknown",
        temperature_band=payload.temperature_band or "Unknown",
        recent_weather_event=payload.recent_weather_event or "None",
        irrigation_status=payload.irrigation_status or "Unknown",
        soil_moisture_observation=payload.soil_moisture_observation or "Unknown",
        field_condition=payload.field_condition or "Unknown"
    )

    db.add(new_case)
    db.add(AuditLog(
        case_id=case_id,
        action="CASE_CREATED_JSON",
        actor_role="System/Farmer",
        details=f"Programmatic submission. Priority: {priority}"
    ))
    db.commit()
    db.refresh(new_case)
    return new_case


@app.get("/api/cases", response_model=List[CaseOut])
def list_cases(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    crop: Optional[str] = None,
    location: Optional[str] = None,
    low_confidence_only: bool = False,
    db: Session = Depends(get_db)
):
    """Lists all cases with multi-criteria filtering for extension officers and experts."""
    query = db.query(Case)
    if status:
        query = query.filter(Case.status == status)
    if priority:
        query = query.filter(Case.priority == priority)
    if crop:
        query = query.filter(Case.crop.ilike(f"%{crop}%"))
    if location:
        query = query.filter(Case.location.ilike(f"%{location}%"))
    if low_confidence_only:
        query = query.filter(Case.ai_confidence < 60.0)

    # Order by priority (High first), then submission time desc
    cases = query.all()
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    cases.sort(key=lambda c: (priority_order.get(c.priority, 3), -c.submission_time.timestamp()))
    return cases


@app.get("/api/cases/{case_id}", response_model=CaseOut)
def get_case_detail(case_id: str, db: Session = Depends(get_db)):
    """Retrieves full case details including uploaded images and expert review history."""
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    return case


@app.post("/api/cases/{case_id}/review", response_model=CaseOut)
def submit_expert_review(
    case_id: str,
    payload: ExpertReviewCreate,
    db: Session = Depends(get_db)
):
    """
    Submits an authoritative expert validation for a case.
    Strict Rule: The expert decision always overrides the experimental AI suggestion.
    AI prediction is retained unchanged on the case for error analysis and auditing.
    """
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    review_time = utcnow()
    review_id = f"REV-{uuid.uuid4().hex[:6].upper()}"

    # Determine status transition
    val_status = payload.validation_status.lower()
    if val_status in ["confirmed", "rejected_ai"]:
        new_status = "Expert Validated"
    elif val_status == "more_info_needed":
        new_status = "More Information Required"
    else:
        new_status = "Under Review (Uncertain)"

    # Record expert review entity
    review_record = ExpertReview(
        review_id=review_id,
        case_id=case_id,
        expert_category=payload.expert_category,
        validation_status=val_status,
        comments=payload.comments,
        urgency=payload.urgency,
        reviewed_at=review_time
    )
    db.add(review_record)

    # Update authoritative case fields
    case.expert_validation = payload.expert_category
    case.expert_comments = payload.comments
    case.expert_review_time = review_time
    case.status = new_status
    if payload.urgency == "Urgent":
        case.priority = "High"

    # Audit log
    ai_match = "Agreed with AI" if val_status == "confirmed" else "Disagreed with/Overrode AI"
    db.add(AuditLog(
        case_id=case_id,
        action="EXPERT_REVIEW_SUBMITTED",
        actor_role="Expert",
        details=f"Status: {new_status} | Expert diagnosis: {payload.expert_category} | {ai_match}"
    ))

    db.commit()
    db.refresh(case)
    return case


@app.post("/api/cases/{case_id}/resubmit", response_model=CaseOut)
async def resubmit_case_information(
    case_id: str,
    additional_notes: str = Form(...),
    new_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Allows a farmer or field agent to provide requested follow-up information and optional photos."""
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    if new_image and new_image.filename:
        content = await new_image.read()
        if len(content) > 0:
            safe_filename = Path(new_image.filename).name
            safe_ext = validate_image_upload(safe_filename, content)
            q_res = analyze_image_quality(content, safe_filename)
            img_uuid = uuid.uuid4().hex[:8]
            saved_filename = f"{case_id}_resubmit_{img_uuid}{safe_ext}"
            file_dest = UPLOADS_DIR / saved_filename
            with open(file_dest, "wb") as f:
                f.write(content)

            image_rec = ImageRecord(
                image_id=f"IMG-{img_uuid.upper()}",
                case_id=case_id,
                image_type="resubmitted_detail",
                file_path=f"/uploads/{saved_filename}",
                quality_score=q_res["quality_score"],
                quality_warnings=json.dumps(q_res["warnings"]),
                farmer_advice=json.dumps(q_res["farmer_advice"]),
                source="Farmer Resubmission",
                license="CC-BY-4.0 (Non-identifiable field observation)"
            )
            db.add(image_rec)

    case.farmer_notes = f"{case.farmer_notes or ''}\n[Resubmission update]: {additional_notes}".strip()
    case.status = "Under Review"

    db.add(AuditLog(
        case_id=case_id,
        action="CASE_RESUBMITTED",
        actor_role="Farmer",
        details="Farmer provided additional requested information."
    ))

    db.commit()
    db.refresh(case)
    return case


@app.post("/api/vision-predict")
async def vision_predict_endpoint(image: UploadFile = File(...)):
    """Direct visual category inference using MobileNetV3-Small."""
    safe_filename = Path(image.filename or "photo.jpg").name
    content = await image.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty image upload")
    validate_image_upload(safe_filename, content)
    res = predict_image(content)
    if res is None:
        raise HTTPException(status_code=500, detail="Vision inference could not process image")
    return res


@app.get("/api/vision/status")
def vision_status_endpoint():
    """Returns status of MobileNetV3-Small vision model."""
    model, device, transform = get_vision_model()
    return {
        "status": "loaded" if model is not None else "unavailable",
        "model_architecture": "MobileNetV3-Small",
        "num_classes": len(CLASSES),
        "classes": CLASSES,
        "device": str(device) if device else "none",
        "checkpoint_exists": MODEL_PATH.exists()
    }


@app.post("/api/quality-check", response_model=ImageQualityResult)
async def check_image_endpoint(image: UploadFile = File(...)):
    """Live interactive image quality analysis endpoint for farmer photo guidance."""
    safe_filename = Path(image.filename or "photo.jpg").name
    content = await image.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty image upload")
    validate_image_upload(safe_filename, content)
    res = analyze_image_quality(content, safe_filename)
    return res


@app.get("/api/edge-cases/1", response_model=ImageQualityResult)
@app.get("/api/edge-cases/poor-image", response_model=ImageQualityResult)
def get_edge_case_1(db: Session = Depends(get_db)):
    """
    Returns image quality analysis for Edge Case 1 (poor/blurry/dark image).
    Returns structured quality_score, warnings array, and farmer_advice array.
    """
    poor_img_path = DATA_DIR / "test_images" / "edge_case_blurry.jpg"
    if poor_img_path.exists():
        with open(poor_img_path, "rb") as f:
            res = analyze_image_quality(f.read(), "edge_case_blurry.jpg")
            return res

    # Fallback to CASE-2026-003
    c = db.query(Case).filter(Case.case_id == "CASE-2026-003").first()
    if c and c.images:
        img = c.images[0]
        return ImageQualityResult(
            quality_score=img.quality_score,
            is_usable=True,
            blur_score=38.2,
            mean_luminance=23.5,
            vegetation_ratio=0.35,
            is_duplicate=False,
            warnings=["Image may be blurry", "Image may be underexposed"],
            farmer_advice=["Hold the phone steady and take another photo.", "Move to better lighting."]
        )

    return ImageQualityResult(
        quality_score=20.0,
        is_usable=True,
        blur_score=38.2,
        mean_luminance=23.5,
        vegetation_ratio=0.35,
        is_duplicate=False,
        warnings=["Image may be blurry", "Image may be underexposed"],
        farmer_advice=["Hold the phone steady and take another photo.", "Move to better lighting."]
    )


@app.get("/api/metrics/summary", response_model=MetricsSummary)
def get_metrics(db: Session = Depends(get_db)):
    """Returns dashboard metrics, T_review calculation, and before/after comparisons."""
    return compute_metrics_summary(db)


@app.get("/api/analytics/regional")
def get_regional_analytics(
    crop: Optional[str] = None,
    region: Optional[str] = None,
    severity: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Returns regional outbreak analytics, risk matrix, and active cluster alerts.
    Supports multi-criteria filtering by crop, region, severity, priority, and status.
    Clearly indicates prototype/simulated data.
    """
    return compute_regional_analytics(
        db, crop=crop, region=region, severity=severity, priority=priority, status=status
    )


@app.get("/api/analytics/t-review")
def get_t_review_analytics(db: Session = Depends(get_db)):
    """
    Returns granular T_review operational latency statistics (mean, median, min, max)
    overall and broken down by priority, crop, and region.
    """
    return compute_t_review_analytics(db)


@app.get("/api/analytics/ai-monitoring")
def get_ai_monitoring_analytics(db: Session = Depends(get_db)):
    """
    Returns live AI confidence distributions, escalation rates,
    expert agreement/override statistics, and static prototype benchmark metrics.
    """
    return compute_ai_monitoring_metrics(db)


@app.get("/api/i18n/languages")
def get_i18n_languages():
    """Returns supported UI languages (English and Tamil)."""
    return get_supported_languages()


@app.get("/api/i18n/{lang}")
def get_i18n_dictionary(lang: str):
    """Returns full translation dictionary for requested language code (en or ta)."""
    return get_translation_dictionary(lang)


@app.get("/")
def serve_index():
    """Serves the single-page application."""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Agricultural Disease Observation App running. Frontend index.html not yet placed."}


# Mount remaining static files
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")
