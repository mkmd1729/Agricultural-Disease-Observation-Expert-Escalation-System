"""
Security, File Upload Validation, and Path Traversal Prevention Tests.
Verifies file size limits (10 MB), extension whitelisting, and input sanitization.
"""

import io
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app, validate_image_upload, MAX_FILE_SIZE_BYTES
from fastapi import HTTPException

client = TestClient(app)


def test_allowed_image_extensions():
    """Verifies that allowed extensions (.jpg, .jpeg, .png, .webp) pass validation."""
    valid_content = b"fake-valid-image-bytes"
    for ext in [".jpg", ".jpeg", ".png", ".webp", ".JPG", ".PNG"]:
        detected_ext = validate_image_upload(f"photo{ext}", valid_content)
        assert detected_ext in [".jpg", ".jpeg", ".png", ".webp"]


def test_disallowed_image_extensions():
    """Verifies that unauthorized extensions (.exe, .sh, .py, .pdf) are rejected with HTTP 400."""
    valid_content = b"some content"
    for bad_file in ["malware.exe", "script.sh", "code.py", "doc.pdf", "no_ext"]:
        with pytest.raises(HTTPException) as excinfo:
            validate_image_upload(bad_file, valid_content)
        assert excinfo.value.status_code == 400
        assert "Invalid image extension" in excinfo.value.detail


def test_oversized_file_rejected():
    """Verifies that image uploads exceeding MAX_FILE_SIZE_BYTES (10 MB) are rejected with HTTP 413."""
    # 10 MB + 1 byte
    oversized_content = b"0" * (MAX_FILE_SIZE_BYTES + 1)
    with pytest.raises(HTTPException) as excinfo:
        validate_image_upload("large_photo.jpg", oversized_content)
    assert excinfo.value.status_code == 413
    assert "exceeds maximum permitted file size" in excinfo.value.detail


def test_api_rejects_disallowed_extension_on_quality_check():
    """Verifies that /api/quality-check rejects unauthorized extensions via HTTP request."""
    fake_file = io.BytesIO(b"dummy script content")
    response = client.post(
        "/api/quality-check",
        files={"image": ("exploit.exe", fake_file, "application/octet-stream")}
    )
    assert response.status_code == 400
    assert "Invalid image extension" in response.json()["detail"]


def test_api_rejects_disallowed_extension_on_vision_predict():
    """Verifies that /api/vision-predict rejects unauthorized extensions via HTTP request."""
    fake_file = io.BytesIO(b"dummy script content")
    response = client.post(
        "/api/vision-predict",
        files={"image": ("backdoor.sh", fake_file, "application/x-sh")}
    )
    assert response.status_code == 400
    assert "Invalid image extension" in response.json()["detail"]


def test_path_traversal_sanitization():
    """Verifies that filenames containing directory traversal characters (../) are sanitized safely."""
    # Test submission with path traversal filename
    fake_image = io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 100)
    data = {
        "crop": "Tomato",
        "symptoms": "leaf_spots",
        "crop_stage": "Flowering",
        "location": "Delta Paddy Belt",
        "first_symptom_time": "2026-10-01T00:00:00Z",
        "severity": "Medium"
    }
    files = {
        "image_detail": ("../../../../etc/passwd.jpg", fake_image, "image/jpeg")
    }

    response = client.post("/api/cases", data=data, files=files)
    assert response.status_code == 201
    created_case = response.json()
    assert created_case["case_id"] is not None
    # Verify that image was saved safely under /uploads/ without directory escape
    for img in created_case["images"]:
        assert not img["file_path"].startswith("../")
        assert img["file_path"].startswith("/uploads/")
