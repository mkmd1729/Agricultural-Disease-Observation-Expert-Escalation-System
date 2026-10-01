"""
Pydantic schemas for request validation and response serialization.
Uses modern Pydantic v2 ConfigDict and robust field validators.
Includes Phase 2.3 environmental context and Phase 2.5 tracking extensions.
"""

from datetime import datetime
import json
import ast
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict, field_validator


def _coerce_to_str_list(v: Any) -> List[str]:
    if v is None:
        return []
    if isinstance(v, (list, tuple)):
        return [str(x) for x in v]
    if isinstance(v, str):
        v_str = v.strip()
        if not v_str or v_str in ("[]", "null", "None"):
            return []
        try:
            parsed = json.loads(v_str)
            if isinstance(parsed, list):
                return [str(x) for x in parsed]
            if isinstance(parsed, str):
                try:
                    p2 = json.loads(parsed)
                    if isinstance(p2, list):
                        return [str(x) for x in p2]
                except Exception:
                    pass
                return [parsed]
            return [str(parsed)]
        except Exception:
            try:
                ev = ast.literal_eval(v_str)
                if isinstance(ev, (list, tuple)):
                    return [str(x) for x in ev]
            except Exception:
                pass
            return [v_str]
    return [str(v)]


class ImageRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    image_id: str
    case_id: str
    image_type: str
    file_path: str
    quality_score: float
    quality_warnings: List[str] = []
    farmer_advice: List[str] = []
    source: str
    license: str
    created_at: datetime

    @field_validator("quality_warnings", "farmer_advice", mode="before")
    @classmethod
    def parse_json_lists(cls, v: Any) -> List[str]:
        return _coerce_to_str_list(v)


class ExpertReviewCreate(BaseModel):
    expert_category: str = Field(..., description="Confirmed category e.g. Fungal, Bacterial, Viral, Abiotic, Healthy")
    validation_status: str = Field(..., description="confirmed | rejected_ai | more_info_needed | uncertain")
    comments: Optional[str] = Field(None, description="Agronomic advice and expert observations")
    urgency: str = Field("Prompt", description="Routine | Prompt | Urgent")

    @field_validator("validation_status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid = {"confirmed", "rejected_ai", "more_info_needed", "uncertain"}
        if v.lower() not in valid:
            raise ValueError(f"Status must be one of: {valid}")
        return v.lower()


class ExpertReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    review_id: str
    case_id: str
    expert_category: str
    validation_status: str
    comments: Optional[str]
    urgency: str
    review_duration_seconds: Optional[float]
    reviewed_at: datetime


class CaseCreate(BaseModel):
    anonymous_farmer_id: Optional[str] = None
    crop: str
    variety: Optional[str] = None
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    crop_stage: str
    symptoms: List[str]
    severity: str = "Medium"
    first_symptom_time: datetime
    farmer_notes: Optional[str] = None
    environmental_notes: Optional[str] = None

    # Phase 2.3 Environmental Context
    rainfall_recent: Optional[str] = "Unknown"
    humidity_level: Optional[str] = "Unknown"
    temperature_band: Optional[str] = "Unknown"
    recent_weather_event: Optional[str] = "None"
    irrigation_status: Optional[str] = "Unknown"
    soil_moisture_observation: Optional[str] = "Unknown"
    field_condition: Optional[str] = "Unknown"


class CaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    case_id: str
    anonymous_farmer_id: str
    crop: str
    variety: Optional[str]
    location: str
    latitude: Optional[float]
    longitude: Optional[float]
    crop_stage: str
    symptoms: str
    severity: str
    first_symptom_time: datetime
    submission_time: datetime
    ai_prediction: Optional[str]
    ai_confidence: Optional[float]
    ai_alternative: Optional[str]
    priority: str
    priority_reason: Optional[str]
    status: str
    expert_validation: Optional[str]
    expert_comments: Optional[str]
    expert_review_time: Optional[datetime]
    farmer_notes: Optional[str]
    environmental_notes: Optional[str]

    # Phase 2.3 Environmental Context
    rainfall_recent: Optional[str] = "Unknown"
    humidity_level: Optional[str] = "Unknown"
    temperature_band: Optional[str] = "Unknown"
    recent_weather_event: Optional[str] = "None"
    irrigation_status: Optional[str] = "Unknown"
    soil_moisture_observation: Optional[str] = "Unknown"
    field_condition: Optional[str] = "Unknown"

    created_at: datetime
    updated_at: datetime
    images: List[ImageRecordOut] = []
    reviews: List[ExpertReviewOut] = []


class ImageQualityResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    quality_score: float
    is_usable: bool
    blur_score: float
    mean_luminance: float
    vegetation_ratio: float
    is_duplicate: bool
    warnings: List[str] = []
    farmer_advice: List[str] = []

    @field_validator("warnings", "farmer_advice", mode="before")
    @classmethod
    def parse_result_lists(cls, v: Any) -> List[str]:
        return _coerce_to_str_list(v)


class MetricsSummary(BaseModel):
    total_observations: int
    pending_reviews: int
    high_priority_cases: int
    expert_validated_cases: int
    low_confidence_cases: int
    cases_needing_info: int
    avg_t_review_hours: Optional[float]
    avg_submission_to_review_hours: Optional[float]
    report_completeness_rate: float
    image_usability_rate: float
    expert_recontact_rate: float
    ai_agreement_rate: Optional[float]
    cases_by_crop: Dict[str, int]
    cases_by_location: Dict[str, int]
    cases_by_symptom_category: Dict[str, int]
    cases_by_priority: Dict[str, int]
    cases_by_status: Dict[str, int]
    comparison_table: List[Dict[str, Any]]
