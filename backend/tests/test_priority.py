"""
Unit tests for the Case Prioritization Engine.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.priority import calculate_priority_score


def test_low_confidence_forces_high_priority():
    """Strict Requirement: Model confidence < 60% must escalate case to High Priority."""
    priority, reason = calculate_priority_score(
        severity="Low",
        crop_stage="Vegetative",
        ai_confidence=52.0,
        symptoms=["leaf_spots"]
    )
    assert priority == "High"
    assert "urgent expert escalation" in reason.lower() or "52.0%" in reason


def test_severe_symptoms_and_flowering_stage_escalates():
    """Severe symptoms during vulnerable flowering stage should result in High Priority."""
    priority, reason = calculate_priority_score(
        severity="Severe",
        crop_stage="Flowering",
        ai_confidence=78.0,
        symptoms=["leaf_spots", "wilting"]
    )
    assert priority == "High"
    assert "flowering" in reason.lower() or "severity" in reason.lower()


def test_mild_routine_case_gives_low_or_medium():
    """Mild symptoms at early vegetative stage with good confidence should be Low/Medium."""
    priority, reason = calculate_priority_score(
        severity="Low",
        crop_stage="Vegetative",
        ai_confidence=85.0,
        symptoms=["healthy"]
    )
    assert priority in ["Low", "Medium"]
