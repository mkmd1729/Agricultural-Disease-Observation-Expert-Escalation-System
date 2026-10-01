"""
Unit and Integration Tests for Phase 3 Regional Outbreak Analytics,
T_review Latency Calculations, and AI Performance Monitoring.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_regional_analytics_endpoint():
    """Verifies that GET /api/analytics/regional returns structured regional epidemiology data."""
    response = client.get("/api/analytics/regional")
    assert response.status_code == 200
    data = response.json()

    assert "disclaimer" in data
    assert "Prototype" in data["disclaimer"] or "simulated" in data["disclaimer"]
    assert "total_matching_cases" in data
    assert "regions" in data
    assert "active_alerts" in data
    assert isinstance(data["regions"], list)
    assert isinstance(data["active_alerts"], list)

    if len(data["regions"]) > 0:
        reg = data["regions"][0]
        assert "region_name" in reg
        assert "total_cases" in reg
        assert "high_priority_count" in reg
        assert "dominant_disease" in reg
        assert "moisture_risk_count" in reg
        assert "risk_level" in reg
        assert "crops" in reg


def test_regional_analytics_filtering():
    """Verifies multi-criteria filtering by crop, priority, and severity."""
    # Filter by crop
    res_crop = client.get("/api/analytics/regional?crop=Tomato")
    assert res_crop.status_code == 200
    data_crop = res_crop.json()
    assert data_crop["filters_applied"]["crop"] == "Tomato"

    # Filter by priority
    res_prio = client.get("/api/analytics/regional?priority=High")
    assert res_prio.status_code == 200
    data_prio = res_prio.json()
    assert data_prio["filters_applied"]["priority"] == "High"

    # Filter by severity
    res_sev = client.get("/api/analytics/regional?severity=Severe")
    assert res_sev.status_code == 200
    data_sev = res_sev.json()
    assert data_sev["filters_applied"]["severity"] == "Severe"


def test_location_privacy_preservation():
    """Verifies that regional coordinates are rounded/approximate and do not leak high-precision GPS."""
    response = client.get("/api/analytics/regional")
    assert response.status_code == 200
    data = response.json()

    for reg in data["regions"]:
        lat = reg.get("approx_latitude")
        lon = reg.get("approx_longitude")
        if lat is not None:
            # Lat should have at most 2 decimal places
            lat_str = str(lat)
            if "." in lat_str:
                decimals = len(lat_str.split(".")[1])
                assert decimals <= 2, f"Latitude {lat} has {decimals} decimals, expected at most 2 for privacy."
        if lon is not None:
            lon_str = str(lon)
            if "." in lon_str:
                decimals = len(lon_str.split(".")[1])
                assert decimals <= 2, f"Longitude {lon} has {decimals} decimals, expected at most 2 for privacy."


def test_t_review_analytics():
    """Verifies T_review operational latency statistics (mean, median, min, max, by priority, by crop)."""
    response = client.get("/api/analytics/t-review")
    assert response.status_code == 200
    data = response.json()

    assert "baseline_assumption_hours" in data
    assert data["baseline_assumption_hours"] == 120.0
    assert "mvp_target_hours" in data
    assert data["mvp_target_hours"] == 24.0
    assert "overall_t_review" in data
    assert "overall_submission_to_review" in data
    assert "by_priority" in data
    assert "by_crop" in data
    assert "by_region" in data

    overall = data["overall_t_review"]
    assert "count" in overall
    assert "mean" in overall
    assert "median" in overall
    assert "min" in overall
    assert "max" in overall

    # High priority latency breakdown should exist
    assert "High" in data["by_priority"]


def test_ai_monitoring_analytics():
    """Verifies live AI confidence distribution histogram and benchmark evaluation loading."""
    response = client.get("/api/analytics/ai-monitoring")
    assert response.status_code == 200
    data = response.json()

    assert "confidence_distribution_buckets" in data
    buckets = data["confidence_distribution_buckets"]
    for b in ["<50%", "50-59%", "60-69%", "70-79%", "80-89%", "90-100%"]:
        assert b in buckets, f"Missing bucket: {b}"

    assert "low_confidence_threshold" in data
    assert data["low_confidence_threshold"] == 60.0
    assert "escalation_rate_percent" in data

    assert "expert_review_metrics" in data
    exp = data["expert_review_metrics"]
    assert "total_reviews" in exp
    assert "confirmed_ai_agreements" in exp
    assert "expert_overrides_rejections" in exp

    assert "model_benchmark" in data
    bmk = data["model_benchmark"]
    assert bmk.get("model_architecture") == "MobileNetV3-Small"
