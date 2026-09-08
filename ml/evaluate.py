"""
Measurable Experiment and Evaluation Script.
Evaluates AI predictions, confidence calibration, agreement with expert ground truth,
and image quality failures across the prototype benchmark cases.
Adheres strictly to the Non-Negotiable Honesty Rule.
"""

import sys
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database import SessionLocal
from backend.app.models import Case, ImageRecord, ExpertReview
from backend.app.image_quality import analyze_image_quality


def run_experiment_evaluation():
    db = SessionLocal()
    cases = db.query(Case).all()
    images = db.query(ImageRecord).all()

    print("======================================================================")
    print("AGRI-DISEASE OBSERVATION: REVIEW 1 EXPERIMENTAL EVALUATION REPORT")
    print("======================================================================")
    print("STATUS: Prototype/simulated evaluation — not field validation.")
    print("WARNING: The current dataset is insufficient to establish generalizable performance.\n")

    # Evaluation Records Table
    results = []
    total_evaluated = 0
    expert_agreements = 0
    expert_conflicts = 0
    low_confidence_escalations = 0
    confidence_scores = []
    false_positives = 0  # AI predicted disease when plant was healthy
    false_negatives = 0  # AI predicted healthy when disease was present

    print(f"{'Case ID':<13} {'Crop':<8} {'Stage':<11} {'AI Prediction':<24} {'Conf%':<6} {'Expert Validation':<28} {'Agreement':<10}")
    print("-" * 105)

    for c in cases:
        total_evaluated += 1
        conf = c.ai_confidence or 0.0
        confidence_scores.append(conf)
        
        if conf < 60.0:
            low_confidence_escalations += 1

        agreement_str = "Pending"
        if c.expert_validation:
            # Check agreement between AI prediction and expert category/validation
            ai_pred_norm = (c.ai_prediction or "").lower()
            exp_val_norm = (c.expert_validation or "").lower()
            
            # Category match heuristics
            is_match = False
            if "fungal" in ai_pred_norm and "fungal" in exp_val_norm:
                is_match = True
            elif "bacterial" in ai_pred_norm and "bacterial" in exp_val_norm:
                is_match = True
            elif "viral" in ai_pred_norm and "viral" in exp_val_norm:
                is_match = True
            elif "abiotic" in ai_pred_norm and "abiotic" in exp_val_norm:
                is_match = True
            elif "healthy" in ai_pred_norm and "healthy" in exp_val_norm:
                is_match = True

            # False positive/negative check
            if "healthy" in exp_val_norm and "healthy" not in ai_pred_norm:
                false_positives += 1
            if "healthy" in ai_pred_norm and "healthy" not in exp_val_norm:
                false_negatives += 1

            if is_match:
                expert_agreements += 1
                agreement_str = "MATCH"
            else:
                expert_conflicts += 1
                agreement_str = "OVERRIDE"

        crop_short = c.crop[:7]
        stage_short = c.crop_stage[:10]
        ai_short = (c.ai_prediction or "None")[:23]
        exp_short = (c.expert_validation or "Pending Review")[:27]

        print(f"{c.case_id:<13} {crop_short:<8} {stage_short:<11} {ai_short:<24} {conf:<6.1f} {exp_short:<28} {agreement_str:<10}")

        results.append({
            "case_id": c.case_id,
            "crop": c.crop,
            "symptoms": c.symptoms,
            "location": c.location,
            "crop_stage": c.crop_stage,
            "ai_prediction": c.ai_prediction,
            "confidence": conf,
            "priority": c.priority,
            "expert_validation": c.expert_validation,
            "agreement": agreement_str,
            "status": c.status
        })

    # Image Quality Benchmark
    print("\n" + "=" * 55)
    print("IMAGE QUALITY FAILURE ANALYSIS")
    print("=" * 55)
    blur_failures = 0
    dark_failures = 0
    bright_failures = 0
    low_crop_failures = 0
    usable_count = 0

    for img in images:
        if img.quality_score >= 20.0:
            usable_count += 1
        warnings = json.loads(img.quality_warnings or "[]")
        for w in warnings:
            if "blurry" in w.lower():
                blur_failures += 1
            elif "dark" in w.lower():
                dark_failures += 1
            elif "bright" in w.lower() or "overexposed" in w.lower():
                bright_failures += 1
            elif "foliage" in w.lower() or "crop" in w.lower():
                low_crop_failures += 1

    total_images = len(images)
    print(f"Total Images Evaluated:         {total_images}")
    print(f"Usable Images (Score >= 20):    {usable_count} ({usable_count/total_images*100:.1f}%)" if total_images else "0")
    print(f"Blurry Image Warnings:          {blur_failures}")
    print(f"Underexposed (Dark) Warnings:   {dark_failures}")
    print(f"Overexposed (Bright) Warnings:  {bright_failures}")
    print(f"Low Crop / Non-Crop Warnings:   {low_crop_failures}")

    # Summary Statistics
    reviewed_count = expert_agreements + expert_conflicts
    agreement_rate = (expert_agreements / reviewed_count * 100.0) if reviewed_count > 0 else 0.0
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

    print("\n" + "=" * 55)
    print("EVALUATION SUMMARY & PERFORMANCE METRICS")
    print("=" * 55)
    print(f"Total Benchmark Cases:          {total_evaluated}")
    print(f"Cases with Expert Review:       {reviewed_count}")
    print(f"AI/Expert Agreement Rate:       {agreement_rate:.1f}% ({expert_agreements}/{reviewed_count})")
    print(f"Expert Overrides / Conflicts:   {expert_conflicts}")
    print(f"Low Confidence Escalations:     {low_confidence_escalations} (cases with conf < 60%)")
    print(f"False Positives (AI said ill):  {false_positives}")
    print(f"False Negatives (AI said safe): {false_negatives}")
    print(f"Average AI Confidence:          {avg_confidence:.1f}%")
    print(f"Confidence Range:               {min(confidence_scores):.1f}% - {max(confidence_scores):.1f}%")
    print("\n[NOTE] Microclimate-specific generalization cannot yet be established because the prototype dataset is small.")
    print("Prototype/simulated evaluation — not field validation.\n")

    db.close()
    return results


if __name__ == "__main__":
    run_experiment_evaluation()
