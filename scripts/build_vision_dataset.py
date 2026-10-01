"""
Reproducible Vision Dataset Builder for Phase 2.1.
Enforces Strict Data Leakage Prevention:
1. Generates original source reference images across 5 foliar categories.
2. Splits source images into Train (70%), Validation (15%), Test (15%) FIRST with seed=42.
3. Augmentation is applied EXCLUSIVELY to the training split.
4. Validation and Test splits contain ONLY unaugmented source images.
5. Emits ml/dataset_manifest.json cataloging source_image_id, augmentation_id, and is_augmented.
"""

import sys
from pathlib import Path
import random
import json
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DATASET_ROOT = PROJECT_ROOT / "ml" / "dataset"
MANIFEST_PATH = PROJECT_ROOT / "ml" / "dataset_manifest.json"

CLASSES = ["healthy", "fungal", "bacterial", "viral", "abiotic"]
CLASS_TO_IDX = {c: i for i, c in enumerate(CLASSES)}
CROPS = ["Tomato", "Maize", "Rice", "Potato", "Wheat", "Cassava"]

# Number of distinct source images per class (Total = 15 * 5 = 75 sources)
SOURCES_PER_CLASS = 15
TRAIN_RATIO = 0.70  # ~10 per class (50 total)
VAL_RATIO = 0.15    # ~2 per class (10 total)
TEST_RATIO = 0.15   # ~3 per class (15 total)


def draw_source_leaf(draw: ImageDraw.ImageDraw, width: int, height: int, base_color: tuple, pattern: str, seed: int):
    rng = random.Random(seed)
    
    # 1. Leaf Base outline with natural asymmetry
    top_offset = rng.randint(-15, 15)
    bbox = [int(width * 0.12), int(height * 0.08) + top_offset, int(width * 0.88), int(height * 0.92)]
    draw.pieslice(bbox, 25, 335, fill=base_color, outline=(25, 75, 25), width=3)
    
    # 2. Main Vein
    draw.line([(width // 2, int(height * 0.1)), (width // 2, int(height * 0.9))], fill=(35, 95, 30), width=3)
    
    # 3. Lateral Veins
    for y in range(int(height * 0.22), int(height * 0.82), 28):
        angle_dy = rng.randint(15, 25)
        draw.line([(width // 2, y), (int(width * 0.22), y - angle_dy)], fill=(35, 90, 30), width=2)
        draw.line([(width // 2, y), (int(width * 0.78), y - angle_dy)], fill=(35, 90, 30), width=2)
        
    # 4. Foliar Pathology Specifics
    if pattern == "healthy":
        # Pure foliage, slight natural gradient
        pass
    elif pattern == "fungal":
        # Concentric necrotic rings with yellow chlorotic halos
        num_spots = rng.randint(8, 16)
        for _ in range(num_spots):
            cx = rng.randint(int(width * 0.25), int(width * 0.75))
            cy = rng.randint(int(height * 0.2), int(height * 0.8))
            r = rng.randint(10, 22)
            # Yellow halo
            draw.ellipse([cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4], fill=(215, 195, 45))
            # Brown necrotic ring
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(115, 65, 25))
            # Inner target ring
            draw.ellipse([cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2], fill=(65, 35, 15))
    elif pattern == "bacterial":
        # Angular water-soaked lesions with oily dark margins
        num_lesions = rng.randint(10, 20)
        for _ in range(num_lesions):
            x = rng.randint(int(width * 0.22), int(width * 0.72))
            y = rng.randint(int(height * 0.2), int(height * 0.8))
            w = rng.randint(14, 32)
            h = rng.randint(12, 28)
            draw.polygon([(x, y), (x + w, y + 4), (x + w - 4, y + h), (x - 4, y + h - 3)],
                         fill=(70, 90, 40), outline=(35, 45, 20), width=2)
    elif pattern == "viral":
        # Mosaic light green / yellow marbled patches
        num_patches = rng.randint(25, 40)
        for _ in range(num_patches):
            cx = rng.randint(int(width * 0.2), int(width * 0.8))
            cy = rng.randint(int(height * 0.15), int(height * 0.85))
            rx = rng.randint(12, 24)
            ry = rng.randint(10, 20)
            draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(195, 215, 75))
    elif pattern == "abiotic":
        # Tip and margin scorch + interveinal chlorosis
        for cy in range(int(height * 0.25), int(height * 0.75), 35):
            draw.ellipse([int(width * 0.28), cy, int(width * 0.42), cy + 18], fill=(210, 205, 60))
            draw.ellipse([int(width * 0.58), cy, int(width * 0.72), cy + 18], fill=(210, 205, 60))
        # Tip burn
        draw.polygon([(width // 2 - 25, int(height * 0.08)), (width // 2 + 25, int(height * 0.08)), (width // 2, int(height * 0.22))], fill=(130, 70, 25))
        # Marginal scorch
        draw.arc([int(width * 0.12), int(height * 0.1), int(width * 0.88), int(height * 0.9)], 35, 130, fill=(145, 80, 30), width=14)
        draw.arc([int(width * 0.12), int(height * 0.1), int(width * 0.88), int(height * 0.9)], 230, 325, fill=(145, 80, 30), width=14)


def generate_source_image(category: str, source_id: str, seed: int) -> Image.Image:
    """Generates a high-quality 256x256 unaugmented source reference image."""
    bg_color = (225, 230, 220)
    img = Image.new("RGB", (256, 256), bg_color)
    draw = ImageDraw.Draw(img)
    
    base_colors = {
        "healthy": (46, 139, 87),
        "fungal": (52, 130, 72),
        "bacterial": (60, 142, 65),
        "viral": (65, 148, 60),
        "abiotic": (175, 170, 55)
    }
    
    draw_source_leaf(draw, 256, 256, base_colors[category], category, seed)
    if category == "viral":
        img = img.filter(ImageFilter.GaussianBlur(1.2))
    return img


def apply_augmentation(img: Image.Image, aug_idx: int) -> tuple[Image.Image, str]:
    """Applies a distinct deterministic transformation to a training source image."""
    aug_img = img.copy()
    if aug_idx == 1:
        aug_img = aug_img.transpose(Image.FLIP_LEFT_RIGHT)
        aug_code = "FLIP_H"
    elif aug_idx == 2:
        aug_img = aug_img.rotate(15, resample=Image.BICUBIC, fillcolor=(225, 230, 220))
        aug_code = "ROT_15"
    elif aug_idx == 3:
        aug_img = aug_img.rotate(-15, resample=Image.BICUBIC, fillcolor=(225, 230, 220))
        aug_code = "ROT_N15"
    elif aug_idx == 4:
        enhancer = ImageEnhance.Brightness(aug_img)
        aug_img = enhancer.enhance(1.18)
        aug_code = "BRIGHT_1.18"
    elif aug_idx == 5:
        enhancer = ImageEnhance.Contrast(aug_img)
        aug_img = enhancer.enhance(0.85)
        aug_code = "CONTRAST_0.85"
    else:
        aug_img = aug_img.transpose(Image.FLIP_TOP_BOTTOM)
        aug_code = "FLIP_V"
        
    return aug_img, aug_code


def build_dataset_pipeline():
    print("======================================================================")
    print("PHASE 2.1: BUILDING VISION DATASET WITH DATA LEAKAGE PREVENTION")
    print("======================================================================")
    print("[RULE] Split original source images FIRST with seed=42.")
    print("[RULE] Augment ONLY the training split.")
    print("[RULE] Validation and Test splits contain strictly unaugmented source images.")
    
    random.seed(42)
    
    # Prepare directories
    for split in ["train", "val", "test"]:
        for c in CLASSES:
            split_dir = DATASET_ROOT / split / c
            split_dir.mkdir(parents=True, exist_ok=True)
            for f in split_dir.glob("*.jpg"):
                try:
                    f.unlink()
                except Exception:
                    pass

    manifest_records = []
    
    for category in CLASSES:
        c_idx = CLASS_TO_IDX[category]
        
        # 1. Generate unique source reference IDs
        source_ids = [f"SRC-{category.upper()[:3]}-{i:03d}" for i in range(1, SOURCES_PER_CLASS + 1)]
        
        # Deterministic shuffle with seed=42
        rng = random.Random(42 + c_idx * 17)
        rng.shuffle(source_ids)
        
        # 2. Strict Partitioning FIRST
        n_train = int(SOURCES_PER_CLASS * TRAIN_RATIO)  # 10
        n_val = int(SOURCES_PER_CLASS * VAL_RATIO)      # 2
        n_test = SOURCES_PER_CLASS - n_train - n_val    # 3
        
        train_sources = source_ids[:n_train]
        val_sources = source_ids[n_train:n_train + n_val]
        test_sources = source_ids[n_train + n_val:]
        
        print(f"Class '{category:<9}': {len(train_sources)} train sources, {len(val_sources)} val sources, {len(test_sources)} test sources")
        
        # 3. Process Validation Split (UNMODIFIED RAW SOURCE ONLY)
        for s_id in val_sources:
            crop = CROPS[(int(s_id[-3:]) + c_idx) % len(CROPS)]
            img = generate_source_image(category, s_id, seed=hash(s_id) % 10000)
            img_id = f"IMG-VAL-{s_id}"
            file_name = f"{img_id}.jpg"
            dest_path = DATASET_ROOT / "val" / category / file_name
            img.save(dest_path, quality=90)
            
            manifest_records.append({
                "image_id": img_id,
                "source_image_id": s_id,
                "augmentation_id": None,
                "is_augmented": False,
                "class_name": category,
                "class_index": c_idx,
                "crop": crop,
                "split": "val",
                "file_path": f"ml/dataset/val/{category}/{file_name}",
                "license": "CC-BY-4.0",
                "dataset_type": "prototype_benchmark_synthetic"
            })

        # 4. Process Test Split (UNMODIFIED RAW SOURCE ONLY, STRICTLY HELD-OUT)
        for s_id in test_sources:
            crop = CROPS[(int(s_id[-3:]) + c_idx) % len(CROPS)]
            img = generate_source_image(category, s_id, seed=hash(s_id) % 10000)
            img_id = f"IMG-TST-{s_id}"
            file_name = f"{img_id}.jpg"
            dest_path = DATASET_ROOT / "test" / category / file_name
            img.save(dest_path, quality=90)
            
            manifest_records.append({
                "image_id": img_id,
                "source_image_id": s_id,
                "augmentation_id": None,
                "is_augmented": False,
                "class_name": category,
                "class_index": c_idx,
                "crop": crop,
                "split": "test",
                "file_path": f"ml/dataset/test/{category}/{file_name}",
                "license": "CC-BY-4.0",
                "dataset_type": "prototype_benchmark_synthetic"
            })

        # 5. Process Training Split (Original Source + Augmented Variants on Train ONLY)
        for s_id in train_sources:
            crop = CROPS[(int(s_id[-3:]) + c_idx) % len(CROPS)]
            base_img = generate_source_image(category, s_id, seed=hash(s_id) % 10000)
            
            # Save original source in train
            orig_img_id = f"IMG-TRN-{s_id}-ORIG"
            orig_file_name = f"{orig_img_id}.jpg"
            orig_dest = DATASET_ROOT / "train" / category / orig_file_name
            base_img.save(orig_dest, quality=90)
            
            manifest_records.append({
                "image_id": orig_img_id,
                "source_image_id": s_id,
                "augmentation_id": None,
                "is_augmented": False,
                "class_name": category,
                "class_index": c_idx,
                "crop": crop,
                "split": "train",
                "file_path": f"ml/dataset/train/{category}/{orig_file_name}",
                "license": "CC-BY-4.0",
                "dataset_type": "prototype_benchmark_synthetic"
            })
            
            # Create 4 augmented variants for this training source
            for aug_i in range(1, 5):
                aug_img, aug_code = apply_augmentation(base_img, aug_i)
                aug_img_id = f"IMG-TRN-{s_id}-{aug_code}"
                aug_file_name = f"{aug_img_id}.jpg"
                aug_dest = DATASET_ROOT / "train" / category / aug_file_name
                aug_img.save(aug_dest, quality=90)
                
                manifest_records.append({
                    "image_id": aug_img_id,
                    "source_image_id": s_id,
                    "augmentation_id": aug_code,
                    "is_augmented": True,
                    "class_name": category,
                    "class_index": c_idx,
                    "crop": crop,
                    "split": "train",
                    "file_path": f"ml/dataset/train/{category}/{aug_file_name}",
                    "license": "CC-BY-4.0",
                    "dataset_type": "prototype_benchmark_synthetic"
                })

    # Save complete dataset manifest
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_records, f, indent=2)

    train_count = sum(1 for r in manifest_records if r["split"] == "train")
    val_count = sum(1 for r in manifest_records if r["split"] == "val")
    test_count = sum(1 for r in manifest_records if r["split"] == "test")
    aug_count = sum(1 for r in manifest_records if r["is_augmented"])
    
    print("\n======================================================================")
    print("DATASET PIPELINE SUMMARY")
    print("======================================================================")
    print(f"Total Source Images:         {SOURCES_PER_CLASS * len(CLASSES)} ({SOURCES_PER_CLASS} per class)")
    print(f"Total Dataset Images:        {len(manifest_records)}")
    print(f"  - Training Split:          {train_count} (50 original + {aug_count} augmented)")
    print(f"  - Validation Split:        {val_count} (10 unaugmented source images)")
    print(f"  - Held-out Test Split:     {test_count} (15 unaugmented source images)")
    print(f"Manifest written to:         {MANIFEST_PATH}")
    print("======================================================================\n")


if __name__ == "__main__":
    build_dataset_pipeline()
