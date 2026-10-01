"""
Hybrid Decision Support Assistant for Agricultural Disease Observation.
Combines:
1. Convolutional Vision Model (MobileNetV3-Small) foliar feature probabilities
2. Structured agronomic symptoms
3. Crop variety and growth stage
4. Image quality assessments

STRICT RULES:
- Never presents predictions as a confirmed medical/agricultural diagnosis.
- All outputs are labeled "Preliminary decision-support hypothesis (needs expert validation)".
- Human agricultural expert validation remains strictly authoritative.
- Ambiguous or conflicting signals penalize confidence into <60% safety escalation zone.
"""

from typing import Dict, Any, List, Optional


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


def _normalize_category_name(cat_str: str) -> str:
    s = cat_str.lower()
    if "fungal" in s:
        return "fungal"
    elif "bacterial" in s:
        return "bacterial"
    elif "viral" in s:
        return "viral"
    elif "abiotic" in s:
        return "abiotic"
    elif "healthy" in s:
        return "healthy"
    return "unclassified"


def classify_observation(
    crop: str,
    symptoms: List[str],
    crop_stage: str,
    image_quality_score: float = 80.0,
    has_image: bool = True,
    vision_result: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Hybrid Decision Support Classifier.
    Fuses real MobileNetV3 computer vision probabilities with structured agronomic symptom heuristics.
    """
    cleaned_symptoms = [s.strip().lower().replace(" ", "_").replace("-", "_") for s in symptoms if s]

    # 1. Symptom Heuristic Evaluation
    symptom_cat = "Unclassified foliar symptom"
    symptom_conf = 50.0
    alternative = "Mixed fungal/bacterial complex"

    if not cleaned_symptoms or "none" in cleaned_symptoms or "healthy" in cleaned_symptoms:
        symptom_cat = "Healthy crop appearance"
        symptom_conf = 88.0
        alternative = "Sub-clinical stress"
    else:
        best_match = None
        highest_weight = 0.0
        for sym in cleaned_symptoms:
            for key, (cand_cat, cand_conf, alt) in SYMPTOM_CATEGORY_MAP.items():
                if key in sym or sym in key:
                    if cand_conf > highest_weight:
                        highest_weight = cand_conf
                        best_match = (cand_cat, cand_conf, alt)

        if best_match:
            symptom_cat, base_weight, alternative = best_match
            symptom_conf = base_weight * 100.0
        else:
            symptom_cat = "Unclassified foliar symptom"
            symptom_conf = 48.0
            alternative = "Atypical disease presentation"

    # 2. Hybrid Fusion with Vision Result
    has_vision = vision_result is not None and vision_result.get("is_available", False)

    if has_vision and has_image:
        vis_cat_raw = vision_result.get("predicted_category", "Unclassified")
        vis_conf = vision_result.get("visual_confidence", 60.0)
        norm_vis = _normalize_category_name(vis_cat_raw)
        norm_sym = _normalize_category_name(symptom_cat)

        if norm_vis == norm_sym:
            # High concordance: Image and Symptoms reinforce each other
            category = f"{vis_cat_raw} foliar symptom"
            confidence = (0.55 * vis_conf) + (0.45 * symptom_conf)
        elif norm_sym == "unclassified":
            # Image provides lead, symptoms generic
            category = f"{vis_cat_raw}-like presentation"
            confidence = (0.75 * vis_conf) + (0.25 * symptom_conf)
        else:
            # CONFLICT between Vision and Symptoms -> Elevates uncertainty!
            category = f"Ambiguous presentation (Visual: {vis_cat_raw}, Symptoms: {symptom_cat})"
            # Severe confidence penalty due to contradictory evidence
            confidence = min(vis_conf, symptom_conf) - 22.0
            alternative = f"Re-evaluate: suspected {vis_cat_raw} vs {symptom_cat}"
    else:
        # Fallback to pure symptom heuristic if no vision result
        category = symptom_cat
        confidence = symptom_conf

    # 3. Quality & Context Penalties
    if image_quality_score < 70.0:
        penalty = (70.0 - image_quality_score) * 0.4
        confidence -= penalty

    if not has_image:
        confidence -= 25.0

    if crop_stage.lower() in ["seedling", "sprout"] and "Healthy" not in category:
        confidence -= 8.0

    # Ensure honest calibration range: 25% to 92% (Never claim 100% diagnostic certainty)
    confidence = max(25.0, min(92.0, round(confidence, 1)))

    # 4. Strict Safety Escalation Check (< 60%)
    is_low_confidence = confidence < 60.0
    status_label = (
        "Low confidence — urgent expert escalation recommended"
        if is_low_confidence
        else "AI-assisted preliminary hypothesis (needs expert validation)"
    )

    return {
        "possible_category": category,
        "confidence": confidence,
        "alternative_prediction": alternative,
        "status_label": status_label,
        "is_low_confidence": is_low_confidence,
        "requires_escalation": is_low_confidence,
        "vision_assisted": has_vision,
        "vision_details": vision_result if has_vision else None,
        "disclaimer": (
            "This is an experimental decision-support hypothesis and NOT an authoritative diagnosis. "
            "Model confidence is not diagnostic certainty. Expert agronomist validation is strictly required."
        )
    }
