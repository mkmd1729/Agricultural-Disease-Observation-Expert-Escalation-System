"""
Generates ethical, synthetic, non-identifiable plant pathology reference images
for the MVP dataset, visual capture guidance, and quality testing.
Also generates data/metadata.csv.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import random
import csv

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "ml" / "dataset"
GUIDANCE_DIR = BASE_DIR / "frontend" / "public" / "guidance"
DATA_DIR = BASE_DIR / "data"

for d in [
    DATASET_DIR / "healthy",
    DATASET_DIR / "bacterial",
    DATASET_DIR / "fungal",
    DATASET_DIR / "viral",
    DATASET_DIR / "abiotic",
    GUIDANCE_DIR,
    DATA_DIR
]:
    d.mkdir(parents=True, exist_ok=True)


def draw_leaf_base(draw: ImageDraw.ImageDraw, width: int, height: int, base_color: tuple):
    """Draws an elliptical leaf with center vein and side veins."""
    # Leaf body
    bbox = [int(width * 0.15), int(height * 0.1), int(width * 0.85), int(height * 0.9)]
    draw.pieslice(bbox, 30, 330, fill=base_color, outline=(20, 70, 20), width=3)
    
    # Center vein
    draw.line([(width // 2, int(height * 0.12)), (width // 2, int(height * 0.88))], fill=(40, 100, 30), width=3)
    # Side veins
    for y in range(int(height * 0.25), int(height * 0.8), int(height * 0.12)):
        draw.line([(width // 2, y), (int(width * 0.25), y - 20)], fill=(40, 95, 30), width=2)
        draw.line([(width // 2, y), (int(width * 0.75), y - 20)], fill=(40, 95, 30), width=2)


def create_healthy_image(path: Path):
    img = Image.new("RGB", (400, 400), (220, 230, 215))
    draw = ImageDraw.Draw(img)
    draw_leaf_base(draw, 400, 400, (46, 139, 87))  # SeaGreen
    img.save(path, quality=90)


def create_fungal_image(path: Path):
    img = Image.new("RGB", (400, 400), (220, 225, 215))
    draw = ImageDraw.Draw(img)
    draw_leaf_base(draw, 400, 400, (50, 130, 70))
    # Concentric brown necrotic spots with yellow halo
    random.seed(42)
    for _ in range(12):
        cx = random.randint(120, 280)
        cy = random.randint(100, 300)
        r = random.randint(12, 28)
        # Yellow halo
        draw.ellipse([cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4], fill=(210, 190, 50))
        # Brown necrotic center
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(110, 60, 25))
        # Inner target ring
        draw.ellipse([cx - r//2, cy - r//2, cx + r//2, cy + r//2], fill=(70, 35, 15))
    img.save(path, quality=90)


def create_bacterial_image(path: Path):
    img = Image.new("RGB", (400, 400), (220, 225, 215))
    draw = ImageDraw.Draw(img)
    draw_leaf_base(draw, 400, 400, (60, 140, 65))
    # Angular water-soaked lesions with dark borders
    random.seed(99)
    for _ in range(15):
        x1 = random.randint(130, 260)
        y1 = random.randint(110, 300)
        w = random.randint(15, 35)
        h = random.randint(15, 30)
        draw.polygon([(x1, y1), (x1 + w, y1 + 5), (x1 + w - 5, y1 + h), (x1 - 5, y1 + h - 5)], fill=(75, 95, 45), outline=(40, 50, 25), width=2)
    img.save(path, quality=90)


def create_viral_image(path: Path):
    img = Image.new("RGB", (400, 400), (220, 225, 215))
    draw = ImageDraw.Draw(img)
    draw_leaf_base(draw, 400, 400, (60, 145, 60))
    # Mosaic light green / yellow marbling patches
    random.seed(123)
    for _ in range(35):
        cx = random.randint(100, 300)
        cy = random.randint(80, 320)
        rx = random.randint(10, 25)
        ry = random.randint(10, 25)
        draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(190, 210, 70))
    img = img.filter(ImageFilter.GaussianBlur(1.5))
    img.save(path, quality=90)


def create_abiotic_image(path: Path):
    img = Image.new("RGB", (400, 400), (225, 220, 210))
    draw = ImageDraw.Draw(img)
    # Severe marginal chlorosis and tip scorch
    draw_leaf_base(draw, 400, 400, (180, 175, 50))  # chlorotic pale yellow
    # Tip scorch
    draw.polygon([(180, 40), (220, 40), (200, 120)], fill=(130, 75, 30))
    # Leaf margin scorch
    draw.arc([60, 40, 340, 360], 40, 140, fill=(140, 80, 35), width=18)
    draw.arc([60, 40, 340, 360], 220, 320, fill=(140, 80, 35), width=18)
    img.save(path, quality=90)


def create_poor_quality_images():
    """Generates blurry, dark, and bright images for edge case testing."""
    edge_dir = DATA_DIR / "test_images"
    edge_dir.mkdir(exist_ok=True)
    
    # 1. Blurry & underexposed image (triggers both blur and underexposure warnings)
    img_blur = Image.new("RGB", (400, 400), (25, 30, 25))
    draw = ImageDraw.Draw(img_blur)
    draw_leaf_base(draw, 400, 400, (30, 50, 30))
    img_blur = img_blur.filter(ImageFilter.GaussianBlur(radius=25))
    img_blur.save(edge_dir / "edge_case_blurry.jpg", quality=80)
    
    # 2. Underexposed / Dark image
    img_dark = Image.new("RGB", (400, 400), (20, 25, 20))
    draw = ImageDraw.Draw(img_dark)
    draw_leaf_base(draw, 400, 400, (25, 45, 25))
    img_dark.save(edge_dir / "edge_case_dark.jpg", quality=80)
    
    # 3. Overexposed / Bright image
    img_bright = Image.new("RGB", (400, 400), (245, 245, 245))
    draw = ImageDraw.Draw(img_bright)
    draw_leaf_base(draw, 400, 400, (235, 245, 230))
    img_bright.save(edge_dir / "edge_case_overexposed.jpg", quality=80)

    # 4. Non-crop / No vegetation
    img_nocrop = Image.new("RGB", (400, 400), (160, 130, 110))
    draw = ImageDraw.Draw(img_nocrop)
    draw.rectangle([50, 50, 350, 350], fill=(180, 150, 130))
    img_nocrop.save(edge_dir / "edge_case_noncrop.jpg", quality=80)


def create_visual_guidance_cards():
    """Creates clear visual photo guidance illustrations for the farmer UI."""
    # Photo 1: Whole Plant Guide
    img1 = Image.new("RGB", (320, 240), (240, 248, 240))
    d1 = ImageDraw.Draw(img1)
    d1.rectangle([0, 0, 319, 239], outline=(46, 139, 87), width=3)
    # Draw soil ground
    d1.rectangle([0, 180, 320, 240], fill=(139, 90, 43))
    # Plant stem & canopy
    d1.line([(160, 190), (160, 70)], fill=(34, 110, 34), width=6)
    d1.ellipse([110, 40, 210, 120], fill=(46, 139, 87))
    d1.ellipse([70, 70, 150, 150], fill=(46, 139, 87))
    d1.ellipse([170, 70, 250, 150], fill=(46, 139, 87))
    d1.text((30, 10), "PHOTO 1: WHOLE PLANT", fill=(20, 80, 30))
    d1.text((30, 210), "Show overall standing plant", fill=(255, 255, 255))
    img1.save(GUIDANCE_DIR / "photo1_whole_plant.jpg", quality=90)

    # Photo 2: Affected Area Guide
    img2 = Image.new("RGB", (320, 240), (248, 245, 240))
    d2 = ImageDraw.Draw(img2)
    d2.rectangle([0, 0, 319, 239], outline=(200, 120, 30), width=3)
    draw_leaf_base(d2, 320, 240, (55, 140, 60))
    # Red focus box around leaf lesion
    d2.ellipse([140, 80, 190, 130], fill=(120, 60, 20), outline=(230, 50, 50), width=3)
    d2.text((20, 10), "PHOTO 2: AFFECTED AREA", fill=(140, 60, 10))
    d2.text((20, 210), "Focus on diseased zone / branch", fill=(100, 50, 20))
    img2.save(GUIDANCE_DIR / "photo2_affected_area.jpg", quality=90)

    # Photo 3: Leaf Detail Guide
    img3 = Image.new("RGB", (320, 240), (245, 240, 248))
    d3 = ImageDraw.Draw(img3)
    d3.rectangle([0, 0, 319, 239], outline=(80, 80, 160), width=3)
    draw_leaf_base(d3, 320, 240, (65, 150, 70))
    # High detail spots
    for cx, cy in [(140, 90), (165, 120), (135, 140), (180, 95)]:
        d3.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(90, 45, 20), outline=(220, 190, 40), width=2)
    d3.text((20, 10), "PHOTO 3: CLOSE-UP DETAIL", fill=(40, 40, 120))
    d3.text((20, 210), "Clear sharp texture of spots/pustules", fill=(40, 40, 120))
    img3.save(GUIDANCE_DIR / "photo3_leaf_detail.jpg", quality=90)


def generate_dataset_and_metadata():
    categories = {
        "healthy": [("Tomato", "Vegetative"), ("Maize", "Flowering"), ("Rice", "Tillering")],
        "fungal": [("Tomato", "Flowering"), ("Potato", "Tuberization"), ("Wheat", "Grain filling")],
        "bacterial": [("Tomato", "Fruiting"), ("Rice", "Vegetative"), ("Cassava", "Mature")],
        "viral": [("Tomato", "Vegetative"), ("Cassava", "Flowering"), ("Papaya", "Fruiting")],
        "abiotic": [("Maize", "Seedling"), ("Tomato", "Fruiting"), ("Wheat", "Tillering")]
    }
    
    metadata_rows = []
    
    for cat, items in categories.items():
        cat_dir = DATASET_DIR / cat
        for i, (crop, stage) in enumerate(items, 1):
            img_id = f"REF-{cat.upper()[:3]}-{i:03d}"
            filename = f"{img_id}.jpg"
            file_path = cat_dir / filename
            
            if cat == "healthy":
                create_healthy_image(file_path)
                symptom = "Normal green foliar coloration"
                validation = "Expert Confirmed Healthy"
                conf = 0.92
            elif cat == "fungal":
                create_fungal_image(file_path)
                symptom = "Concentric brown spots with chlorotic halo"
                validation = "Fungal leaf spot (Alternaria spp.)"
                conf = 0.84
            elif cat == "bacterial":
                create_bacterial_image(file_path)
                symptom = "Angular water-soaked leaf lesions"
                validation = "Bacterial leaf blight (Xanthomonas)"
                conf = 0.81
            elif cat == "viral":
                create_viral_image(file_path)
                symptom = "Yellow mosaic mottle and leaf puckering"
                validation = "Mosaic virus complex"
                conf = 0.79
            else:
                create_abiotic_image(file_path)
                symptom = "Marginal leaf scorch and potassium chlorosis"
                validation = "Abiotic nutrient deficiency / heat scorch"
                conf = 0.76

            metadata_rows.append({
                "image_id": img_id,
                "crop": crop,
                "symptom_category": cat,
                "symptom_description": symptom,
                "crop_stage": stage,
                "approximate_location": "Research Station Zone A (Simulated)",
                "source": "Project-created ethical synthetic benchmark",
                "license": "CC-BY-4.0 (Non-identifiable synthetic crop asset)",
                "expert_validation_status": validation,
                "confidence": conf,
                "notes": "Ethical prototype reference image. Contains zero PII, zero human faces, zero private property."
            })

    # Write CSV
    csv_file = DATA_DIR / "metadata.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "image_id", "crop", "symptom_category", "symptom_description",
            "crop_stage", "approximate_location", "source", "license",
            "expert_validation_status", "confidence", "notes"
        ])
        writer.writeheader()
        writer.writerows(metadata_rows)
        
    print(f"Generated {len(metadata_rows)} dataset reference images and metadata.csv successfully.")


if __name__ == "__main__":
    generate_dataset_and_metadata()
    create_poor_quality_images()
    create_visual_guidance_cards()
    print("All ethical synthetic assets and visual guidance cards generated.")
