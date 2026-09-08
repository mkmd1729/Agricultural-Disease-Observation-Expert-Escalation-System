"""
Database models for Case, ImageRecord, ExpertReview, and AuditLog.
Adheres to Review 1 Schema requirements.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Case(Base):
    __tablename__ = "cases"

    case_id = Column(String(64), primary_key=True, index=True)
    anonymous_farmer_id = Column(String(64), nullable=False, index=True)
    crop = Column(String(64), nullable=False, index=True)
    variety = Column(String(64), nullable=True)
    location = Column(String(128), nullable=False, index=True)
    latitude = Column(Float, nullable=True)   # Approximate, rounded to 2 decimals
    longitude = Column(Float, nullable=True)  # Approximate, rounded to 2 decimals
    crop_stage = Column(String(64), nullable=False)
    symptoms = Column(Text, nullable=False)   # Comma-separated or JSON list
    severity = Column(String(32), nullable=False, default="Medium")
    first_symptom_time = Column(DateTime, nullable=False)
    submission_time = Column(DateTime, nullable=False, default=utcnow)
    
    # AI Assistance (Experimental, non-authoritative)
    ai_prediction = Column(String(128), nullable=True)
    ai_confidence = Column(Float, nullable=True)
    ai_alternative = Column(String(128), nullable=True)
    
    # Triage & Status
    priority = Column(String(32), nullable=False, default="Medium")
    priority_reason = Column(Text, nullable=True)
    status = Column(String(64), nullable=False, default="Submitted")
    
    # Expert Validation (Authoritative)
    expert_validation = Column(String(128), nullable=True)
    expert_comments = Column(Text, nullable=True)
    expert_review_time = Column(DateTime, nullable=True)
    
    # Notes & Metadata
    farmer_notes = Column(Text, nullable=True)
    environmental_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=utcnow)
    updated_at = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)

    images = relationship("ImageRecord", back_populates="case", cascade="all, delete-orphan")
    reviews = relationship("ExpertReview", back_populates="case", cascade="all, delete-orphan")


class ImageRecord(Base):
    __tablename__ = "images"

    image_id = Column(String(64), primary_key=True, index=True)
    case_id = Column(String(64), ForeignKey("cases.case_id"), nullable=False, index=True)
    image_type = Column(String(32), nullable=False)  # whole_plant, affected_area, leaf_detail
    file_path = Column(String(256), nullable=False)
    quality_score = Column(Float, nullable=False, default=100.0)
    quality_warnings = Column(Text, nullable=True)   # JSON list of warnings
    farmer_advice = Column(Text, nullable=True)      # JSON list of actionable advice
    source = Column(String(128), nullable=False, default="Project-created synthetic/demo image")
    license = Column(String(128), nullable=False, default="Open Agricultural License (CC-BY-4.0)")
    created_at = Column(DateTime, nullable=False, default=utcnow)

    case = relationship("Case", back_populates="images")


class ExpertReview(Base):
    __tablename__ = "expert_reviews"

    review_id = Column(String(64), primary_key=True, index=True)
    case_id = Column(String(64), ForeignKey("cases.case_id"), nullable=False, index=True)
    expert_category = Column(String(64), nullable=False)  # Fungal, Bacterial, Viral, Abiotic, Healthy
    validation_status = Column(String(64), nullable=False)  # confirmed, rejected_ai, more_info_needed, uncertain
    comments = Column(Text, nullable=True)
    urgency = Column(String(32), nullable=False, default="Prompt")
    review_duration_seconds = Column(Float, nullable=True)
    reviewed_at = Column(DateTime, nullable=False, default=utcnow)

    case = relationship("Case", back_populates="reviews")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String(64), nullable=False, index=True)
    action = Column(String(64), nullable=False)
    actor_role = Column(String(64), nullable=False)  # Farmer, Extension Officer, Expert, System
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=utcnow)
