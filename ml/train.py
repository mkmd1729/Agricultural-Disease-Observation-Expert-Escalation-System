"""
Phase 2.1: MobileNetV3-Small Training Pipeline.
Trains a lightweight foliar disease classifier on the partitioned training dataset.
Strict Rules:
- Model outputs RAW LOGITS without embedded Softmax.
- nn.CrossEntropyLoss consumes raw unnormalized logits directly.
- Classifier input dimension is determined dynamically from torchvision architecture.
- Only the 'train' split is used for optimization; 'val' split for checkpointing.
- The held-out 'test' split is NOT loaded or touched during training.
"""

import sys
from pathlib import Path
import json
import time
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.models as models
import torchvision.transforms as transforms

MANIFEST_PATH = PROJECT_ROOT / "ml" / "dataset_manifest.json"
MODELS_DIR = PROJECT_ROOT / "ml" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_SAVE_PATH = MODELS_DIR / "mobilenetv3_foliar.pt"
LABELS_SAVE_PATH = MODELS_DIR / "class_labels.json"
SUMMARY_SAVE_PATH = MODELS_DIR / "training_summary.json"

CLASSES = ["healthy", "fungal", "bacterial", "viral", "abiotic"]
CLASS_TO_IDX = {c: i for i, c in enumerate(CLASSES)}


class FoliarDataset(Dataset):
    def __init__(self, records, transform=None):
        self.records = records
        self.transform = transform

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx):
        item = self.records[idx]
        img_path = PROJECT_ROOT / item["file_path"]
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        label = item["class_index"]
        return image, label


def build_mobilenetv3_model(num_classes: int = 5, pretrained: bool = True) -> nn.Module:
    """
    Constructs MobileNetV3-Small with dynamic classifier dimensioning.
    RETURNS RAW UNNORMALIZED LOGITS. Does NOT include Softmax in forward pass.
    """
    if pretrained:
        try:
            weights = models.MobileNet_V3_Small_Weights.DEFAULT
            model = models.mobilenet_v3_small(weights=weights)
        except Exception:
            model = models.mobilenet_v3_small(weights=None)
    else:
        model = models.mobilenet_v3_small(weights=None)

    # Dynamically determine the classifier input feature dimension
    last_layer = model.classifier[-1]
    in_features = getattr(last_layer, "in_features")
    model.classifier[-1] = nn.Linear(in_features, num_classes)
    
    return model


def train_vision_model(epochs: int = 15, batch_size: int = 16, lr: float = 1e-3):
    print("======================================================================")
    print("PHASE 2.1: MOBILENETV3-SMALL TRAINING (RAW LOGITS + CROSS-ENTROPY)")
    print("======================================================================")
    print(f"[CONFIG] Target Classes: {CLASSES}")
    print(f"[CONFIG] Preprocessing: Resize(224, 224), ImageNet Norm (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])")
    print(f"[CONFIG] Loss Function: nn.CrossEntropyLoss (consumes raw logits)")

    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Manifest not found at {MANIFEST_PATH}. Run scripts/build_vision_dataset.py first.")

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    train_records = [r for r in manifest if r["split"] == "train"]
    val_records = [r for r in manifest if r["split"] == "val"]
    
    print(f"[DATASET] Train records: {len(train_records)} | Val records: {len(val_records)}")
    print(f"[DATASET] Held-out test records: {sum(1 for r in manifest if r['split'] == 'test')} (untouched)")

    # Standard ImageNet normalization
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    train_dataset = FoliarDataset(train_records, transform=train_transform)
    val_dataset = FoliarDataset(val_records, transform=val_transform)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    torch.manual_seed(42)
    device = torch.device("cpu")
    model = build_mobilenetv3_model(num_classes=len(CLASSES), pretrained=True)
    model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)

    best_val_loss = float("inf")
    best_epoch = 0
    history = []

    start_time = time.time()

    for epoch in range(1, epochs + 1):
        # Training loop
        model.train()
        running_loss = 0.0
        correct_train = 0
        total_train = 0

        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            # Raw logits from model forward pass
            logits = model(images)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            preds = torch.argmax(logits, dim=1)
            correct_train += (preds == labels).sum().item()
            total_train += labels.size(0)

        epoch_train_loss = running_loss / total_train
        epoch_train_acc = (correct_train / total_train) * 100.0

        # Validation loop
        model.eval()
        val_loss = 0.0
        correct_val = 0
        total_val = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(device)
                labels = labels.to(device)

                logits = model(images)
                loss = criterion(logits, labels)

                val_loss += loss.item() * images.size(0)
                preds = torch.argmax(logits, dim=1)
                correct_val += (preds == labels).sum().item()
                total_val += labels.size(0)

        epoch_val_loss = val_loss / total_val if total_val > 0 else 0.0
        epoch_val_acc = (correct_val / total_val) * 100.0 if total_val > 0 else 0.0

        history.append({
            "epoch": epoch,
            "train_loss": round(epoch_train_loss, 4),
            "train_acc": round(epoch_train_acc, 2),
            "val_loss": round(epoch_val_loss, 4),
            "val_acc": round(epoch_val_acc, 2)
        })

        print(f"Epoch [{epoch:02d}/{epochs:02d}] "
              f"Train Loss: {epoch_train_loss:.4f} | Train Acc: {epoch_train_acc:5.1f}% | "
              f"Val Loss: {epoch_val_loss:.4f} | Val Acc: {epoch_val_acc:5.1f}%")

        # Save best model based on validation loss
        if epoch_val_loss < best_val_loss:
            best_val_loss = epoch_val_loss
            best_epoch = epoch
            torch.save(model.state_dict(), MODEL_SAVE_PATH)

    total_training_time = round(time.time() - start_time, 2)
    print(f"\n[COMPLETE] Best checkpoint saved at Epoch {best_epoch} (Val Loss: {best_val_loss:.4f}) to {MODEL_SAVE_PATH}")
    print(f"[COMPLETE] Total Training Duration: {total_training_time}s")

    # Save class labels
    with open(LABELS_SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump({str(i): c for i, c in enumerate(CLASSES)}, f, indent=2)

    # Save training summary
    summary = {
        "model_architecture": "MobileNetV3-Small",
        "num_classes": len(CLASSES),
        "classes": CLASSES,
        "epochs": epochs,
        "best_epoch": best_epoch,
        "best_val_loss": round(best_val_loss, 4),
        "total_training_time_seconds": total_training_time,
        "device": str(device),
        "history": history,
        "disclaimer": "Trained on synthetic prototype benchmark dataset. Not validated for autonomous field deployment."
    }
    with open(SUMMARY_SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"[COMPLETE] Class labels saved to {LABELS_SAVE_PATH}")
    print(f"[COMPLETE] Training summary saved to {SUMMARY_SAVE_PATH}\n")


if __name__ == "__main__":
    train_vision_model()
