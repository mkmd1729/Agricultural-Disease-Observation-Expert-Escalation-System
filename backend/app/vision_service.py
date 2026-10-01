"""
Vision Model Inference Service for Agricultural Disease Observation.
Loads the trained MobileNetV3-Small checkpoint and runs inference on uploaded leaf images.
Applies Softmax strictly during inference to compute class probabilities.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import io
from PIL import Image

# Path constants
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / "ml" / "models" / "mobilenetv3_foliar.pt"
LABELS_PATH = BASE_DIR / "ml" / "models" / "class_labels.json"

CLASSES = ["healthy", "fungal", "bacterial", "viral", "abiotic"]

_MODEL = None
_DEVICE = None
_TRANSFORM = None


def get_vision_model():
    """Lazily loads and caches the MobileNetV3-Small PyTorch model."""
    global _MODEL, _DEVICE, _TRANSFORM
    if _MODEL is not None:
        return _MODEL, _DEVICE, _TRANSFORM

    try:
        import torch
        import torchvision.transforms as transforms
        from ml.train import build_mobilenetv3_model

        device = torch.device("cpu")
        model = build_mobilenetv3_model(num_classes=len(CLASSES), pretrained=False)
        if MODEL_PATH.exists():
            state_dict = torch.load(MODEL_PATH, map_location=device)
            model.load_state_dict(state_dict)
        model.to(device)
        model.eval()

        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        _MODEL = model
        _DEVICE = device
        _TRANSFORM = transform
        return _MODEL, _DEVICE, _TRANSFORM
    except Exception as e:
        print(f"[WARN] Vision model could not be loaded: {e}. Falling back to heuristic-only mode.")
        return None, None, None


def predict_image(image_bytes: bytes) -> Optional[Dict[str, Any]]:
    """
    Runs vision inference on uploaded image bytes.
    Returns:
        {
            "predicted_category": str,
            "visual_confidence": float (0-100),
            "probabilities": Dict[str, float],
            "model_version": "MobileNetV3-Small"
        }
    """
    model, device, transform = get_vision_model()
    if model is None or transform is None:
        return None

    try:
        import torch
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        tensor = transform(img).unsqueeze(0).to(device)

        with torch.no_grad():
            raw_logits = model(tensor)
            probs = torch.softmax(raw_logits, dim=-1)[0]

        pred_idx = torch.argmax(probs).item()
        pred_cat = CLASSES[pred_idx].capitalize()
        prob_dict = {CLASSES[i].capitalize(): round(probs[i].item() * 100.0, 1) for i in range(len(CLASSES))}
        confidence = round(probs[pred_idx].item() * 100.0, 1)

        return {
            "predicted_category": pred_cat,
            "visual_confidence": confidence,
            "probabilities": prob_dict,
            "model_architecture": "MobileNetV3-Small",
            "is_available": True
        }
    except Exception as e:
        print(f"[WARN] Vision inference failed: {e}")
        return None
