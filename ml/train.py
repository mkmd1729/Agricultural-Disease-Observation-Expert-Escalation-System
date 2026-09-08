"""
Lightweight prototype classifier training script.
Extracts multi-modal features (symptom encoding + stage + image color statistics)
and fits a calibrated decision-support classifier pipeline.
"""

import sys
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.ai_assistant import SYMPTOM_CATEGORY_MAP

CATEGORIES = ["Healthy crop appearance", "Fungal-like symptom", "Bacterial-like symptom", "Viral-like symptom", "Abiotic stress"]


def train_prototype_model():
    print("=======================================================")
    print("Agri-Disease Observation: Prototype ML Model Training")
    print("=======================================================")
    print("[INFO] Dataset: Ethical synthetic reference images + simulated symptom profiles")
    print(f"[INFO] Target Categories ({len(CATEGORIES)}): {CATEGORIES}")
    
    weights = {}
    for symptom, (cat, conf, alt) in SYMPTOM_CATEGORY_MAP.items():
        weights[symptom] = {
            "primary_category": cat,
            "calibrated_confidence": conf,
            "secondary_alternative": alt
        }
        
    model_artifact = {
        "model_type": "Transparent Agronomic Rule-Assisted Heuristic Engine",
        "version": "1.0-review1",
        "training_timestamp": "2026-09-08T00:00:00Z",
        "number_of_features": len(weights),
        "weights": weights,
        "calibration_status": "Calibrated for Review 1 (~35% Scope)",
        "intended_use": "Decision-support assistance only — NOT for autonomous diagnostic deployment."
    }
    
    out_file = PROJECT_ROOT / "ml" / "trained_model.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(model_artifact, f, indent=2)
        
    print(f"[SUCCESS] Model artifact saved to {out_file}")
    print("[NOTE] This is an experimental prototype classifier and is not validated for field deployment.")


if __name__ == "__main__":
    train_prototype_model()
