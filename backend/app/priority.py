"""
Case Prioritization Engine for Agricultural Extension Triage.
Implements decision-support priority scoring (High, Medium, Low).
Note: This is a triage mechanism to speed up expert attention, not an agronomic diagnosis.
"""

from typing import Tuple, List, Optional


def calculate_priority_score(
    severity: str,
    crop_stage: str,
    ai_confidence: Optional[float],
    symptoms: List[str],
    environmental_notes: Optional[str] = None
) -> Tuple[str, str]:
    """
    Computes priority level and explanatory rationale based on triage factors.
    Returns: (priority_level: 'High' | 'Medium' | 'Low', reason_description: str)
    """
    score = 0
    reasons: List[str] = []
    
    # 1. Symptom Severity Factor
    sev = severity.lower() if severity else "medium"
    if "severe" in sev or "critical" in sev or "high" in sev:
        score += 3
        reasons.append("Reported high symptom severity")
    elif "moderate" in sev or "medium" in sev:
        score += 2
    else:
        score += 1

    # 2. Vulnerable Crop Growth Stage
    stage = crop_stage.lower() if crop_stage else ""
    if any(k in stage for k in ["flowering", "fruiting", "bloom"]):
        score += 3
        reasons.append("Critical growth stage (flowering/fruiting with imminent yield loss)")
    elif "seedling" in stage or "sprout" in stage:
        score += 2
        reasons.append("Early seedling vulnerability")
    else:
        score += 1

    # 3. Low Model Confidence Rule (Strict Requirement: < 60% -> High Priority)
    if ai_confidence is not None and ai_confidence < 60.0:
        score += 4
        reasons.append(f"Low AI confidence ({ai_confidence:.1f}% < 60%) — urgent expert escalation required")

    # 4. Rapid Contagion / Spread Risk Indicator
    spread_risk_keywords = ["ooze", "wilting", "rust", "canker", "blight", "damping_off", "rot"]
    joined_symptoms = " ".join(symptoms).lower()
    if any(k in joined_symptoms for k in spread_risk_keywords):
        score += 2
        reasons.append("Symptom indicates potential rapid contagion/spread risk")

    # 5. Environmental Stress Amplifiers
    if environmental_notes:
        env_lower = environmental_notes.lower()
        if any(w in env_lower for w in ["rain", "flood", "humid", "hail", "fog"]):
            score += 1
            reasons.append("Humid/wet conditions favoring pathogen proliferation")

    # Final mapping
    if score >= 6 or (ai_confidence is not None and ai_confidence < 60.0):
        priority = "High"
    elif score >= 4:
        priority = "Medium"
    else:
        priority = "Low"

    explanation = "; ".join(reasons) if reasons else "Standard routine triage"
    return priority, explanation
