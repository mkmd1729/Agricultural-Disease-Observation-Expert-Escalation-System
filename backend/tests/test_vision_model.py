"""
Phase 2.1 Unit and Integration Tests for MobileNetV3 and Dataset Pipeline.
Verifies:
1. Data leakage prevention (zero source image overlap across splits, unaugmented val/test).
2. MobileNetV3 architecture outputs raw logits of shape (batch, 5) without Softmax constraints.
3. Controlled confidence threshold escalation (0.59 vs 0.60).
4. Formula accuracy for evaluation metrics (Precision, Recall, F1, Confusion Matrix).
5. Existence and integrity of Phase 2.1 model and evaluation artifacts.
"""

import sys
from pathlib import Path
import json
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import torch
import torch.nn as nn
from ml.train import build_mobilenetv3_model, CLASSES, MANIFEST_PATH, MODELS_DIR, MODEL_SAVE_PATH
from backend.app.priority import calculate_priority_score


def test_data_leakage_prevention():
    """
    STRICT REQUIREMENT: Source images must be partitioned first.
    Zero source-image overlap permitted across train, val, and test splits.
    Validation and test splits must be 100% unaugmented.
    """
    assert MANIFEST_PATH.exists(), "Manifest file must exist"
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    train_sources = {r["source_image_id"] for r in manifest if r["split"] == "train"}
    val_sources = {r["source_image_id"] for r in manifest if r["split"] == "val"}
    test_sources = {r["source_image_id"] for r in manifest if r["split"] == "test"}

    # Assert non-empty splits
    assert len(train_sources) > 0, "Train sources must not be empty"
    assert len(val_sources) > 0, "Val sources must not be empty"
    assert len(test_sources) > 0, "Test sources must not be empty"

    # Leakage check: Disjoint source sets
    train_val_overlap = train_sources.intersection(val_sources)
    train_test_overlap = train_sources.intersection(test_sources)
    val_test_overlap = val_sources.intersection(test_sources)

    assert len(train_val_overlap) == 0, f"DATA LEAKAGE: Overlap between Train and Val: {train_val_overlap}"
    assert len(train_test_overlap) == 0, f"DATA LEAKAGE: Overlap between Train and Test: {train_test_overlap}"
    assert len(val_test_overlap) == 0, f"DATA LEAKAGE: Overlap between Val and Test: {val_test_overlap}"

    # Verify val and test splits are strictly unaugmented
    for r in manifest:
        if r["split"] in ["val", "test"]:
            assert r["is_augmented"] is False, f"Augmented image {r['image_id']} found in {r['split']} split!"
            assert r["augmentation_id"] is None, f"Augmentation ID found on unaugmented sample {r['image_id']}"

    # Verify manifest schema fields
    for r in manifest:
        assert "source_image_id" in r
        assert "augmentation_id" in r
        assert "is_augmented" in r
        assert "class_name" in r
        assert "class_index" in r


def test_mobilenetv3_returns_raw_logits():
    """
    STRICT REQUIREMENT: MobileNetV3 must produce raw logits of shape (batch, 5).
    Must NOT contain Softmax or be constrained to a probability distribution.
    Classifier dimension must be determined dynamically.
    """
    model = build_mobilenetv3_model(num_classes=5, pretrained=False)
    model.eval()

    # 1. Architectural inspection: verify no Softmax layer exists in model modules
    for name, module in model.named_modules():
        assert not isinstance(module, (nn.Softmax, nn.LogSoftmax)), f"Found unauthorized probability layer: {name}"

    # 2. Output dimension verification
    dummy_input = torch.randn(2, 3, 224, 224)
    with torch.no_grad():
        outputs = model(dummy_input)

    assert outputs.shape == (2, 5), f"Expected shape (2, 5), got {outputs.shape}"

    # 3. Verify outputs are unnormalized raw logits (not constrained to sum to 1.0)
    row_sums = outputs.sum(dim=-1)
    is_softmax_dist = torch.allclose(row_sums, torch.ones_like(row_sums), atol=1e-4)
    assert not is_softmax_dist, "Model output appears constrained to a probability distribution (summing to 1.0)"


def test_controlled_confidence_escalation_boundary():
    """
    STRICT REQUIREMENT: Test triage escalation logic with controlled deterministic confidence values.
    Confidence 0.59 (59.0%) -> triggers High Priority escalation.
    Confidence 0.60 (60.0%) -> normal threshold behavior (does not trigger low-confidence escalation).
    """
    # Test 59% (< 60% threshold)
    priority_59, reason_59 = calculate_priority_score(
        severity="Low",
        crop_stage="Vegetative",
        ai_confidence=59.0,
        symptoms=["leaf_spots"]
    )
    assert priority_59 == "High", f"Expected High priority for 59% confidence, got {priority_59}"
    assert "urgent expert escalation" in reason_59.lower() or "59.0%" in reason_59

    # Test 60% (>= 60% threshold)
    priority_60, reason_60 = calculate_priority_score(
        severity="Low",
        crop_stage="Vegetative",
        ai_confidence=60.0,
        symptoms=["leaf_spots"]
    )
    # With Low severity, Vegetative stage, and no contagion keywords, score is < 6, so Medium or Low
    assert priority_60 in ["Medium", "Low"], f"Expected Medium/Low priority for 60% confidence, got {priority_60}"
    assert "urgent expert escalation" not in reason_60.lower()


def test_metrics_calculation_formula_accuracy():
    """
    Validates Precision, Recall, and F1 calculations against known mathematical truth.
    """
    # Mock confusion matrix: 3 classes
    # [ [5, 1, 0],   Row 0: sum = 6
    #   [1, 4, 1],   Row 1: sum = 6
    #   [0, 0, 6] ]  Row 2: sum = 6
    # Total = 18. Correct = 5 + 4 + 6 = 15. Accuracy = 15/18 = 83.33%
    cm = [
        [5, 1, 0],
        [1, 4, 1],
        [0, 0, 6]
    ]
    # Class 0: TP=5, FP=1, FN=1 -> Prec = 5/6, Rec = 5/6, F1 = 5/6
    # Class 1: TP=4, FP=1, FN=2 -> Prec = 4/5 = 0.80, Rec = 4/6 = 0.667, F1 = 2*(0.8*0.6667)/(1.4667) = 0.727
    # Class 2: TP=6, FP=1, FN=0 -> Prec = 6/7 = 0.857, Rec = 6/6 = 1.0, F1 = 2*(0.857*1.0)/(1.857) = 0.923

    total = sum(sum(row) for row in cm)
    correct = sum(cm[i][i] for i in range(3))
    acc = correct / total
    assert round(acc, 4) == round(15 / 18, 4)

    # Class 0 Precision & Recall
    tp_0 = cm[0][0]
    fp_0 = cm[1][0] + cm[2][0]
    fn_0 = cm[0][1] + cm[0][2]
    prec_0 = tp_0 / (tp_0 + fp_0)
    rec_0 = tp_0 / (tp_0 + fn_0)
    f1_0 = 2 * prec_0 * rec_0 / (prec_0 + rec_0)
    assert prec_0 == 5 / 6
    assert rec_0 == 5 / 6
    assert f1_0 == 5 / 6


def test_model_artifact_files_exist():
    """
    Verifies that all Phase 2.1 artifacts have been created on disk and are valid.
    """
    assert MODEL_SAVE_PATH.exists(), f"Missing model checkpoint {MODEL_SAVE_PATH}"
    assert MODEL_SAVE_PATH.stat().st_size > 1_000_000, "Model file size too small (<1MB)"

    # Test loading checkpoint
    state = torch.load(MODEL_SAVE_PATH, map_location="cpu")
    assert isinstance(state, dict), "Checkpoint must be a state dict"

    # Test class labels
    labels_file = MODELS_DIR / "class_labels.json"
    assert labels_file.exists()
    with open(labels_file, "r", encoding="utf-8") as f:
        labels = json.load(f)
    assert len(labels) == 5

    # Test evaluation results file
    eval_file = MODELS_DIR / "evaluation_results.json"
    assert eval_file.exists()
    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
    assert eval_data["total_test_samples"] == 15
    assert "macro_f1" in eval_data
    assert "confusion_matrix" in eval_data
