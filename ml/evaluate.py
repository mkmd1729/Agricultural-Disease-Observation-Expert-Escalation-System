"""
Measurable Experiment and Evaluation Script.
Phase 1: Evaluates AI predictions, confidence calibration, and agreement with expert ground truth across prototype database cases.
Phase 2.1: Evaluates trained MobileNetV3-Small on the held-out unaugmented TEST split.
Adheres strictly to the Non-Negotiable Honesty Rule.
"""

import sys
from pathlib import Path
import json
import time
import platform
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database import SessionLocal
from backend.app.models import Case, ImageRecord, ExpertReview
from backend.app.image_quality import analyze_image_quality

# Phase 2.1 imports
try:
    import torch
    import torch.nn as nn
    import torchvision.transforms as transforms
    from ml.train import build_mobilenetv3_model, CLASSES, CLASS_TO_IDX, MODEL_SAVE_PATH, MANIFEST_PATH, MODELS_DIR
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


def evaluate_vision_model():
    """
    Phase 2.1 Evaluation: Evaluates MobileNetV3-Small on the untouched, held-out TEST set.
    Computes Accuracy, Precision, Recall, Macro F1, Weighted F1, Confusion Matrix,
    Empirically Measured Latency, and Systematic Error Cases.
    """
    print("\n" + "=" * 70)
    print("PHASE 2.1: MOBILENETV3-SMALL COMPUTER VISION MODEL EVALUATION")
    print("=" * 70)
    print("STATUS: Prototype benchmark evaluation — NOT validated field deployment.")
    print("DATASET: Synthetic prototype benchmark foliar assets (CC-BY-4.0).")
    print("RULE: Held-out test split is strictly unaugmented and untouched during training.")
    print("=" * 70 + "\n")

    if not TORCH_AVAILABLE:
        print("[ERROR] PyTorch or torchvision not available.")
        return {}

    if not MANIFEST_PATH.exists():
        print(f"[ERROR] Dataset manifest not found at {MANIFEST_PATH}")
        return {}

    if not MODEL_SAVE_PATH.exists():
        print(f"[ERROR] Trained model checkpoint not found at {MODEL_SAVE_PATH}")
        return {}

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Filter for held-out TEST split
    test_records = [r for r in manifest if r["split"] == "test"]
    if not test_records:
        print("[ERROR] No test records found in manifest.")
        return {}

    print(f"[INFO] Evaluating on {len(test_records)} held-out unaugmented test images across {len(CLASSES)} classes.\n")

    # Load Model
    device = torch.device("cpu")
    model = build_mobilenetv3_model(num_classes=len(CLASSES), pretrained=False)
    state_dict = torch.load(MODEL_SAVE_PATH, map_location=device)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()

    # Preprocessing
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # Confusion matrix: rows = true_label, cols = pred_label
    num_classes = len(CLASSES)
    confusion_matrix = [[0 for _ in range(num_classes)] for _ in range(num_classes)]
    
    test_results = []
    latencies_ms = []
    confidences_correct = []
    confidences_incorrect = []

    for item in test_records:
        img_path = PROJECT_ROOT / item["file_path"]
        raw_img = Image.open(img_path).convert("RGB")
        tensor = val_transform(raw_img).unsqueeze(0).to(device)
        true_idx = item["class_index"]

        # Measure latency
        t0 = time.perf_counter()
        with torch.no_grad():
            raw_logits = model(tensor)
            probs = torch.softmax(raw_logits, dim=-1)
        t_elapsed = (time.perf_counter() - t0) * 1000.0  # ms
        latencies_ms.append(t_elapsed)

        pred_idx = torch.argmax(probs, dim=-1).item()
        conf = probs[0, pred_idx].item() * 100.0
        
        confusion_matrix[true_idx][pred_idx] += 1
        is_correct = (pred_idx == true_idx)

        if is_correct:
            confidences_correct.append(conf)
        else:
            confidences_incorrect.append(conf)

        test_results.append({
            "image_id": item["image_id"],
            "source_image_id": item["source_image_id"],
            "crop": item["crop"],
            "true_class": CLASSES[true_idx],
            "pred_class": CLASSES[pred_idx],
            "confidence": round(conf, 2),
            "correct": is_correct,
            "latency_ms": round(t_elapsed, 2)
        })

    total_test = len(test_results)
    correct_count = sum(1 for r in test_results if r["correct"])
    overall_accuracy = (correct_count / total_test) * 100.0 if total_test > 0 else 0.0

    # Compute Per-Class Metrics
    per_class_metrics = {}
    macro_precisions = []
    macro_recalls = []
    macro_f1s = []
    weighted_f1_sum = 0.0

    for i, c_name in enumerate(CLASSES):
        tp = confusion_matrix[i][i]
        fp = sum(confusion_matrix[row][i] for row in range(num_classes) if row != i)
        fn = sum(confusion_matrix[i][col] for col in range(num_classes) if col != i)
        support = sum(confusion_matrix[i][col] for col in range(num_classes))

        precision = (tp / (tp + fp)) * 100.0 if (tp + fp) > 0 else 0.0
        recall = (tp / (tp + fn)) * 100.0 if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        per_class_metrics[c_name] = {
            "support": support,
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "precision": round(precision, 2),
            "recall": round(recall, 2),
            "f1_score": round(f1, 2)
        }

        macro_precisions.append(precision)
        macro_recalls.append(recall)
        macro_f1s.append(f1)
        weighted_f1_sum += f1 * support

    macro_precision = round(sum(macro_precisions) / num_classes, 2)
    macro_recall = round(sum(macro_recalls) / num_classes, 2)
    macro_f1 = round(sum(macro_f1s) / num_classes, 2)
    weighted_f1 = round(weighted_f1_sum / total_test, 2) if total_test > 0 else 0.0

    # Latency Stats
    mean_latency = round(sum(latencies_ms) / len(latencies_ms), 2) if latencies_ms else 0.0
    min_latency = round(min(latencies_ms), 2) if latencies_ms else 0.0
    max_latency = round(max(latencies_ms), 2) if latencies_ms else 0.0

    # Print Formatted Evaluation Report
    print(f"{'Class':<12} {'Support':<8} {'Precision':<12} {'Recall':<10} {'F1-Score':<10}")
    print("-" * 55)
    for c_name, m in per_class_metrics.items():
        print(f"{c_name:<12} {m['support']:<8} {m['precision']:>6.1f}%     {m['recall']:>6.1f}%    {m['f1_score']:>6.1f}%")
    print("-" * 55)
    print(f"{'Overall Acc':<12} {total_test:<8} {'':<12} {'':<10} {overall_accuracy:>6.1f}%")
    print(f"{'Macro Avg':<12} {total_test:<8} {macro_precision:>6.1f}%     {macro_recall:>6.1f}%    {macro_f1:>6.1f}%")
    print(f"{'Weighted Avg':<12} {total_test:<8} {'':<12} {'':<10} {weighted_f1:>6.1f}%\n")

    # Print Confusion Matrix Table
    print("=" * 65)
    print("CONFUSION MATRIX (Rows: True Class | Columns: Predicted Class)")
    print("=" * 65)
    header = f"{'True Class':<12} | " + " | ".join(f"{c[:5]:>5}" for c in CLASSES)
    print(header)
    print("-" * 65)
    for i, c_name in enumerate(CLASSES):
        row_str = " | ".join(f"{confusion_matrix[i][j]:>5}" for j in range(num_classes))
        print(f"{c_name:<12} | {row_str}")
    print("=" * 65 + "\n")

    # Print Confidence Distribution
    all_confs = confidences_correct + confidences_incorrect
    mean_conf = round(sum(all_confs) / len(all_confs), 1) if all_confs else 0.0
    mean_corr_conf = round(sum(confidences_correct) / len(confidences_correct), 1) if confidences_correct else 0.0
    print("CONFIDENCE DISTRIBUTION:")
    print(f"  - Overall Mean Confidence:    {mean_conf}%")
    print(f"  - Correct Predictions Mean:   {mean_corr_conf}%")
    if confidences_incorrect:
        mean_inc_conf = round(sum(confidences_incorrect) / len(confidences_incorrect), 1)
        print(f"  - Incorrect Predictions Mean: {mean_inc_conf}%")
    print(f"  - Min / Max Confidence:       {min(all_confs):.1f}% / {max(all_confs):.1f}%\n")

    # Print Measured Runtime Hardware & Latency
    hw_info = f"{platform.system()} {platform.release()} ({platform.machine()}), Python {platform.python_version()}"
    print("EMPIRICAL LATENCY & RUNTIME ENVIRONMENT:")
    print(f"  - Hardware / OS:              {hw_info}")
    print(f"  - Device:                     CPU (PyTorch single-image forward pass)")
    print(f"  - Mean Inference Latency:     {mean_latency} ms per image")
    print(f"  - Latency Range:              {min_latency} ms - {max_latency} ms\n")

    # Systematic Error Analysis
    error_cases = [r for r in test_results if not r["correct"]]
    print("=" * 65)
    print(f"SYSTEMATIC ERROR CASES ({len(error_cases)} misclassifications)")
    print("=" * 65)
    if error_cases:
        for err in error_cases:
            print(f"  • Image: {err['image_id']} (Source: {err['source_image_id']}, Crop: {err['crop']})")
            print(f"    True: {err['true_class']} -> Predicted: {err['pred_class']} (Confidence: {err['confidence']}%)")
    else:
        print("  • Zero misclassifications observed on the held-out test split.")
    print("=" * 65 + "\n")

    # Save structured results to disk
    eval_output = {
        "evaluation_type": "Phase 2.1 Held-Out Test Evaluation",
        "dataset_type": "prototype_benchmark_synthetic",
        "total_test_samples": total_test,
        "overall_accuracy": overall_accuracy,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "per_class_metrics": per_class_metrics,
        "confusion_matrix": confusion_matrix,
        "class_names": CLASSES,
        "confidence_stats": {
            "overall_mean": mean_conf,
            "correct_mean": mean_corr_conf,
            "min_confidence": min(all_confs) if all_confs else 0.0,
            "max_confidence": max(all_confs) if all_confs else 0.0
        },
        "latency_stats": {
            "runtime_environment": hw_info,
            "device": "CPU",
            "mean_ms": mean_latency,
            "min_ms": min_latency,
            "max_ms": max_latency
        },
        "systematic_errors": error_cases,
        "disclaimer": "Prototype benchmark evaluation. Results reflect synthetic reference assets and are not field validated."
    }

    eval_results_path = MODELS_DIR / "evaluation_results.json"
    cm_path = MODELS_DIR / "confusion_matrix.json"

    with open(eval_results_path, "w", encoding="utf-8") as f:
        json.dump(eval_output, f, indent=2)

    with open(cm_path, "w", encoding="utf-8") as f:
        json.dump({
            "classes": CLASSES,
            "matrix": confusion_matrix
        }, f, indent=2)

    print(f"[COMPLETE] Saved evaluation results to {eval_results_path}")
    print(f"[COMPLETE] Saved confusion matrix to {cm_path}\n")

    return eval_output


def run_experiment_evaluation():
    """
    Phase 1 Legacy Benchmark Evaluation on Database Cases.
    Preserved exactly for full backward compatibility with acceptance tests.
    """
    db = SessionLocal()
    cases = db.query(Case).all()
    images = db.query(ImageRecord).all()

    print("======================================================================")
    print("AGRI-DISEASE OBSERVATION: EXPERIMENTAL EVALUATION REPORT")
    print("======================================================================")
    print("STATUS: Prototype/simulated evaluation — not field validation.")
    print("WARNING: The current dataset is insufficient to establish generalizable performance.\n")

    results = []
    total_evaluated = 0
    expert_agreements = 0
    expert_conflicts = 0
    low_confidence_escalations = 0
    confidence_scores = []
    false_positives = 0
    false_negatives = 0

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
            ai_pred_norm = (c.ai_prediction or "").lower()
            exp_val_norm = (c.expert_validation or "").lower()
            
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
    # If vision model checkpoint exists, run both vision evaluation and database case evaluation
    if MODEL_SAVE_PATH.exists():
        evaluate_vision_model()
    run_experiment_evaluation()
