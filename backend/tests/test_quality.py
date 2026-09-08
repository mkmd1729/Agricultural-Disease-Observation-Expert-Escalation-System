"""
Unit tests for the Image Quality Analysis Engine.
"""

import sys
from pathlib import Path
import io

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from PIL import Image, ImageFilter, ImageDraw
from backend.app.image_quality import analyze_image_quality, calculate_laplacian_variance, compute_dhash, hamming_distance


def test_sharp_image_passes():
    """Sharp synthetic leaf should have high quality score and no blur warning."""
    img = Image.new("RGB", (300, 300), (220, 230, 215))
    draw = ImageDraw.Draw(img)
    draw.pieslice([40, 30, 260, 270], 30, 330, fill=(46, 139, 87), outline=(20, 70, 20), width=4)
    # sharp lines
    for i in range(10):
        draw.line([(50, 30 + i * 20), (250, 40 + i * 20)], fill=(20, 40, 20), width=3)
        
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    res = analyze_image_quality(buf.getvalue(), "sharp_test.jpg")
    
    assert res["is_usable"] is True
    assert res["quality_score"] >= 65.0
    assert not any("blurry" in w.lower() for w in res["warnings"])


def test_blurry_image_triggers_warning():
    """Blurred edge case image must trigger blur warning and guidance."""
    edge_blur_file = PROJECT_ROOT / "data" / "test_images" / "edge_case_blurry.jpg"
    if edge_blur_file.exists():
        raw_bytes = edge_blur_file.read_bytes()
    else:
        # Fallback to high gaussian blur
        img = Image.new("RGB", (300, 300), (220, 230, 215))
        draw = ImageDraw.Draw(img)
        draw.pieslice([40, 30, 260, 270], 30, 330, fill=(46, 139, 87))
        blurred = img.filter(ImageFilter.GaussianBlur(25))
        buf = io.BytesIO()
        blurred.save(buf, format="JPEG")
        raw_bytes = buf.getvalue()
    
    res = analyze_image_quality(raw_bytes, "blur_test.jpg")
    assert any("blurry" in w.lower() for w in res["warnings"])
    assert any("steady" in a.lower() for a in res["farmer_advice"])
    # Non-blocking rule: still usable
    assert res["is_usable"] is True


def test_dark_image_triggers_warning():
    """Dark/underexposed image (< 40 luminance) must trigger underexposure warning."""
    img = Image.new("RGB", (300, 300), (15, 20, 15))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 250, 250], fill=(20, 30, 20))
    
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    res = analyze_image_quality(buf.getvalue(), "dark_test.jpg")
    
    assert res["mean_luminance"] < 40.0
    assert any("underexposed" in w.lower() or "dark" in w.lower() for w in res["warnings"])
    assert any("lighting" in a.lower() or "daylight" in a.lower() for a in res["farmer_advice"])


def test_bright_image_triggers_warning():
    """Overexposed bright image (> 225 luminance) must trigger overexposure warning."""
    img = Image.new("RGB", (300, 300), (245, 245, 245))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 250, 250], fill=(240, 250, 240))
    
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    res = analyze_image_quality(buf.getvalue(), "bright_test.jpg")
    
    assert res["mean_luminance"] > 225.0
    assert any("bright" in w.lower() or "overexposed" in w.lower() for w in res["warnings"])


def test_duplicate_image_detection():
    """Identical image submitted twice must trigger perceptual duplicate warning."""
    img = Image.new("RGB", (200, 200), (50, 120, 60))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    raw = buf.getvalue()
    
    # First submission
    res1 = analyze_image_quality(raw, "img_first.jpg")
    assert res1["is_duplicate"] is False
    
    # Second submission of same/near-identical image
    res2 = analyze_image_quality(raw, "img_second.jpg")
    assert res2["is_duplicate"] is True
    assert any("similar" in w.lower() for w in res2["warnings"])
