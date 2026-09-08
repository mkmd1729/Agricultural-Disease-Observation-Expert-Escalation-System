"""
Experimental AI Assistant for Disease Observation.
Provides non-authoritative candidate categories with calibrated confidence.
STRICT REQUIREMENT: Never claims confirmed diagnosis; enforces "Needs expert validation".
Escalates to high priority when confidence < 60%.
"""

from typing import Dict, Any, List, Optional
import random


# Agronomic symptom heuristics based on standard plant pathology knowledge
SYMPTOM_CATEGORY_MAP = {
    # Fungal symptoms
    "leaf_spots": ("Fungal-like symptom", 0.72, "Bacterial leaf spot"),
    "powdery_coating": ("Fungal-like symptom (Powdery mildew)", 0.85, "Abiotic dust/pesticide residue"),
    "rust_pustules": ("Fungal-like symptom (Rust)", 0.82, "Nutrient deficiency"),
    "damping_off": ("Fungal-like symptom (Soil-borne pathogen)", 0.75, "Waterlogging / abiotic rot"),
    
    # Bacterial symptoms
    "water_soaked_lesions": ("Bacterial-like symptom", 0.76, "Fungal leaf spot"),
    "bacterial_ooze": ("Bacterial-like symptom", 0.88, "Secondary saprophyte"),
    "vascular_browning": ("Bacterial wilt symptom", 0.70, "Fusarium wilt (fungal)"),
    
    # Viral symptoms
    "mosaic_pattern": ("Viral-like symptom (Mosaic)", 0.80, "Genetic variegation / zinc deficiency"),
    "leaf_curling": ("Viral-like symptom (Leaf curl)", 0.68, "Mite / thrips feeding injury"),
    "stunting": ("Viral-like symptom / Stunting", 0.58, "Root rot / nutrient deficiency"),
    
    # Abiotic symptoms
    "yellowing_chlorosis": ("Abiotic stress (Nutrient deficiency)", 0.64, "Root fungal infection"),
    "tip_burn": ("Abiotic stress (Salinity/heat scorch)", 0.78, "Potassium deficiency"),
    "wilting": ("Wilting symptom (Water stress or vascular pathogen)", 0.54, "Bacterial wilt"),
    
    # Healthy
    "healthy": ("Healthy crop appearance", 0.90, "Early-stage latent infection")
}


def classify_observation(
    crop: str,
    symptoms: List[str],
    crop_stage: str,
    image_quality_score: float = 80.0,
    has_image: bool = True
) -> Dict[str, Any]:
    """
    Evaluates observation data to produce an experimental candidate classification.
    Calibrates confidence honestly based on symptom specificity, stage, and image quality.
    """
    cleaned_symptoms = [s.strip().lower().replace(" ", "_").replace("-", "_") for s in symptoms if s]
    
    if not cleaned_symptoms or "none" in cleaned_symptoms or "healthy" in cleaned_symptoms:
        category = "Healthy crop appearance"
        confidence = 88.0
        alternative = "Sub-clinical stress"
    else:
        # Match highest specificity symptom
        best_match = None
        highest_weight = 0.0
        
        for sym in cleaned_symptoms:
            for key, (cand_cat, cand_conf, alt) in SYMPTOM_CATEGORY_MAP.items():
                if key in sym or sym in key:
                    if cand_conf > highest_weight:
                        highest_weight = cand_conf
                        best_match = (cand_cat, cand_conf, alt)
                        
        if best_match:
            category, base_conf, alternative = best_match
            confidence = base_conf * 100.0
        else:
            # Ambiguous/unmapped symptoms
            category = "Unclassified foliar symptom"
            confidence = 48.0
            alternative = "Mixed fungal/bacterial complex"

    # Calibration adjustments:
    # 1. Low quality images degrade confidence
    if image_quality_score < 70.0:
        penalty = (70.0 - image_quality_score) * 0.4
        confidence -= penalty
        
    # 2. Lack of image degrades confidence significantly
    if not has_image:
        confidence -= 25.0
        
    # 3. Seedling stage symptoms are notorious for overlapping causes
    if crop_stage.lower() in ["seedling", "sprout"] and "Healthy" not in category:
        confidence -= 8.0

    # Ensure range 25% - 94% (never 100% certainty for an AI prototype)
    confidence = max(25.0, min(92.0, round(confidence, 1)))

    # Low-confidence threshold check (< 60%)
    is_low_confidence = confidence < 60.0
    status_label = "Low confidence — expert review recommended" if is_low_confidence else "AI-assisted observation (needs expert validation)"

    return {
        "possible_category": category,
        "confidence": confidence,
        "alternative_prediction": alternative,
        "status_label": status_label,
        "is_low_confidence": is_low_confidence,
        "requires_escalation": is_low_confidence,
        "disclaimer": (
            "This is an experimental assistance feature and not an authoritative diagnosis. "
            "Model confidence is not the same thing as diagnostic certainty. "
            "Expert review is always required before taking field action."
        )
    }
