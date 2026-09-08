"""
Image Quality Engine for Agricultural Disease Observation.
Evaluates sharpness/blur, exposure, vegetation presence, and perceptual duplicates.
Provides actionable farmer-friendly guidance without blocking submissions.
"""

from typing import Tuple, List, Dict, Any
from PIL import Image, ImageOps, ImageStat, ImageFilter
import io
import math


# Recent hashes cache for duplicate detection
_SEEN_IMAGE_HASHES: Dict[str, str] = {}


def compute_dhash(img: Image.Image, hash_size: int = 8) -> str:
    """Computes a 64-bit difference hash (dHash) for perceptual duplicate detection."""
    # Resize to (hash_size + 1, hash_size) in grayscale
    resized = img.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    try:
        pixels = list(resized.get_flattened_data())
    except AttributeError:
        pixels = list(resized.getdata())
    
    # Compare adjacent pixels in each row
    bits = []
    for row in range(hash_size):
        row_offset = row * (hash_size + 1)
        for col in range(hash_size):
            left = pixels[row_offset + col]
            right = pixels[row_offset + col + 1]
            bits.append("1" if left > right else "0")
            
    # Convert bit array to hexadecimal string
    bit_string = "".join(bits)
    hex_str = f"{int(bit_string, 2):016x}"
    return hex_str


def hamming_distance(h1: str, h2: str) -> int:
    """Calculates Hamming distance between two hex hashes."""
    try:
        x = int(h1, 16) ^ int(h2, 16)
        return bin(x).count("1")
    except Exception:
        return 64


def calculate_laplacian_variance(img_gray: Image.Image) -> float:
    """
    Approximates Laplacian variance to measure sharpness/blur using Pillow.
    Applies Laplacian kernel and computes variance of resulting pixel values.
    """
    laplacian_kernel = ImageFilter.Kernel(
        (3, 3),
        [0, 1, 0,
         1, -4, 1,
         0, 1, 0],
        scale=1.0,
        offset=128
    )
    filtered = img_gray.filter(laplacian_kernel)
    stat = ImageStat.Stat(filtered)
    variance = stat.var[0]
    return float(variance)


def calculate_vegetation_ratio(img_rgb: Image.Image) -> float:
    """
    Heuristic to estimate green/crop presence.
    Checks fraction of pixels where green channel is prominent or within leaf-tone ranges.
    """
    sample = img_rgb.resize((100, 100))
    try:
        pixels = list(sample.get_flattened_data())
    except AttributeError:
        pixels = list(sample.getdata())
        
    total_pixels = len(pixels)
    if total_pixels == 0:
        return 0.0
        
    vegetation_count = 0
    for px in pixels:
        if isinstance(px, (tuple, list)) and len(px) >= 3:
            r, g, b = px[0], px[1], px[2]
            is_green = (g > r * 1.05 and g > b * 1.05) or (g > 70 and r > 50 and b < g and (r + g) > 2 * b)
            if is_green:
                vegetation_count += 1
            
    return round(vegetation_count / total_pixels, 3)


def analyze_image_quality(image_bytes: bytes, filename: str = "upload.jpg") -> Dict[str, Any]:
    """
    Comprehensive image quality evaluation.
    Checks:
    1. Blurry image (Laplacian variance < 100)
    2. Underexposure (mean luminance < 40)
    3. Overexposure (mean luminance > 225)
    4. Crop visibility (vegetation ratio < 0.10)
    5. Duplicate check (dHash distance <= 4 from previously submitted image)
    """
    warnings: List[str] = []
    farmer_advice: List[str] = []
    
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img = ImageOps.exif_transpose(img)
    except Exception as e:
        return {
            "quality_score": 0.0,
            "is_usable": False,
            "blur_score": 0.0,
            "mean_luminance": 0.0,
            "vegetation_ratio": 0.0,
            "is_duplicate": False,
            "warnings": [f"Unreadable image format or corrupt file: {str(e)}"],
            "farmer_advice": ["Please select a standard JPEG or PNG photo taken with your camera."]
        }
        
    img_rgb = img.convert("RGB")
    img_gray = img.convert("L")
    
    # 1. Blur Analysis
    blur_score = calculate_laplacian_variance(img_gray)
    if blur_score < 100.0:
        warnings.append("Image may be blurry")
        farmer_advice.append("Hold the phone steady and take another photo.")
        
    # 2. Exposure Analysis
    stat = ImageStat.Stat(img_gray)
    mean_luminance = float(stat.mean[0])
    
    if mean_luminance < 40.0:
        warnings.append("Image may be underexposed")
        farmer_advice.append("Move to better lighting.")
    elif mean_luminance > 225.0:
        warnings.append("Image may be overexposed")
        farmer_advice.append("Shield leaf from harsh direct glare.")
        
    # 3. Crop Visibility Heuristic
    veg_ratio = calculate_vegetation_ratio(img_rgb)
    if veg_ratio < 0.10:
        warnings.append("Low crop/plant visibility detected")
        farmer_advice.append("Take another photo closer to the affected plant parts.")
        
    # 4. Duplicate Check
    img_hash = compute_dhash(img)
    is_duplicate = False
    for prev_name, prev_hash in _SEEN_IMAGE_HASHES.items():
        if hamming_distance(img_hash, prev_hash) <= 4:
            is_duplicate = True
            warnings.append("This photo appears very similar to an earlier uploaded photograph.")
            farmer_advice.append("Consider taking a photograph from a different angle or distance.")
            break
            
    # Cache hash (keep latest 100)
    if len(_SEEN_IMAGE_HASHES) > 100:
        _SEEN_IMAGE_HASHES.pop(next(iter(_SEEN_IMAGE_HASHES)))
    _SEEN_IMAGE_HASHES[filename] = img_hash
    
    # Calculate synthetic overall quality score (0 to 100)
    score = 100.0
    if blur_score < 100.0:
        score -= min(40.0, (100.0 - blur_score) * 0.4)
    if mean_luminance < 40.0:
        score -= (40.0 - mean_luminance) * 0.75
    elif mean_luminance > 225.0:
        score -= (mean_luminance - 225.0) * 1.0
    if veg_ratio < 0.10:
        score -= 20.0
    if is_duplicate:
        score -= 10.0
        
    score = max(5.0, min(100.0, round(score, 1)))
    
    # If both blur and underexposure/darkness, cap at 20.0
    if blur_score < 100.0 and mean_luminance < 40.0:
        score = min(score, 20.0)
        
    is_usable = score >= 15.0
    
    return {
        "quality_score": score,
        "is_usable": is_usable,
        "blur_score": round(blur_score, 1),
        "mean_luminance": round(mean_luminance, 1),
        "vegetation_ratio": veg_ratio,
        "is_duplicate": is_duplicate,
        "warnings": warnings,
        "farmer_advice": farmer_advice
    }
