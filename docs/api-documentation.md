# Comprehensive API Documentation
## Agricultural Disease Observation & Expert Escalation System

**API Version:** `1.0.0`  
**Base URL:** `http://localhost:8000` (or `https://<domain>` in production)  
**Specification Standard:** OpenAPI 3.0 / FastAPI REST  
**Interactive Documentation:** Swagger UI at `/docs`, ReDoc at `/redoc`

---

## 1. Overview & Security Standards

The Agricultural Disease Observation & Expert Escalation System provides a unified RESTful API serving three primary client roles:
1. **Farmers / Field Extension Agents:** Standardized case submissions, photo uploads, image quality checks, case status tracking, and follow-up resubmissions.
2. **Agricultural Extension Officers:** Case triage, multi-criteria filtering, operational KPI summaries, and regional outbreak surveillance.
3. **Domain Experts / Plant Pathologists:** Authoritative validation, diagnostic overrides, follow-up clarification requests, and agronomic management instructions.

### Security & Privacy Safeguards
* **Maximum File Upload Size:** Enforced at $10\text{ MB}$ (`10,485,760 bytes`). Requests exceeding this limit receive `HTTP 413 Content Too Large`.
* **File Whitelisting:** Strict extension checking allows only `.jpg`, `.jpeg`, `.png`, and `.webp`. Unauthorized extensions receive `HTTP 400 Bad Request`.
* **Path Traversal Protection:** User-supplied filenames are sanitized (`Path(filename).name`), and images are persisted using random UUIDs.
* **Location Privacy:** All geographic coordinates submitted by farmers are truncated and rounded to 2 decimal places ($\approx 1.1\text{ km}$ spatial precision). No household or exact farmstead coordinates are ever stored or returned.

---

## 2. Complete Endpoint Directory

| Method | Endpoint | Description | Phase |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Service liveness and operational health check | Phase 1 |
| `POST` | `/api/cases` | Submit multipart observation (form data + up to 3 images) | Phase 1 & 2 |
| `POST` | `/api/cases/json` | Submit programmatic JSON observation (batch seeding/testing) | Phase 1 |
| `GET` | `/api/cases` | List observations with multi-criteria filtering | Phase 1 |
| `GET` | `/api/cases/{case_id}` | Retrieve comprehensive case details, images, and review history | Phase 1 |
| `POST` | `/api/cases/{case_id}/review` | Submit authoritative expert diagnostic review | Phase 1 & 2 |
| `POST` | `/api/cases/{case_id}/resubmit` | Submit requested follow-up clarification notes and photos | Phase 2 |
| `POST` | `/api/vision-predict` | Direct visual inference using MobileNetV3-Small | Phase 2 |
| `GET` | `/api/vision/status` | Model status, architecture metadata, and class labels | Phase 2 |
| `POST` | `/api/quality-check` | Live interactive image quality analysis | Phase 1 |
| `GET` | `/api/edge-cases/1` | Edge Case 1 analysis for blurry/underexposed images | Phase 1 |
| `GET` | `/api/metrics/summary` | Global dashboard metrics, T_review, and before/after comparisons | Phase 1 & 2 |
| `GET` | `/api/analytics/regional` | Regional cluster analytics, risk matrix, and outbreak alerts | Phase 3 |
| `GET` | `/api/analytics/t-review` | Granular operational latency statistics (mean, median, min, max) | Phase 3 |
| `GET` | `/api/analytics/ai-monitoring` | Live confidence distribution, escalation rates, and benchmark data | Phase 3 |
| `GET` | `/api/i18n/languages` | Supported UI languages (English and Tamil) | Phase 3 |
| `GET` | `/api/i18n/{lang}` | Complete translation dictionary for specified language code | Phase 3 |

---

## 3. Granular Endpoint Specifications

### 3.1 Health Check
* **Method:** `GET`
* **Path:** `/api/health`
* **Response `200 OK`:**
```json
{
  "status": "healthy",
  "service": "agri-disease-observation",
  "version": "1.0.0",
  "timestamp": "2026-10-01T12:00:00.000000+00:00"
}
```

---

### 3.2 Submit Farmer Observation (Multipart)
* **Method:** `POST`
* **Path:** `/api/cases`
* **Content-Type:** `multipart/form-data`
* **Request Fields:**
  * `crop` (string, required): e.g. `"Tomato"`, `"Rice"`, `"Maize"`.
  * `symptoms` (string, required): Comma-separated strings or JSON array, e.g. `"leaf_spots, wilting"`.
  * `crop_stage` (string, required): `"Seedling"`, `"Vegetative"`, `"Tillering"`, `"Flowering"`, `"Fruiting"`, `"Mature"`.
  * `location` (string, required): Regional sector name, e.g. `"Delta Paddy Belt Sector B"`.
  * `first_symptom_time` (string, required): ISO 8601 string or `YYYY-MM-DD`.
  * `anonymous_farmer_id` (string, optional): Anonymized ID. Generated if omitted.
  * `variety` (string, optional): Crop cultivar/variety name.
  * `severity` (string, optional, default `"Medium"`): `"Low"`, `"Medium"`, `"High"`, `"Severe"`.
  * `latitude` (float, optional): Approximate GPS latitude (automatically rounded to 2 decimals).
  * `longitude` (float, optional): Approximate GPS longitude (automatically rounded to 2 decimals).
  * `farmer_notes` (string, optional): Qualitative observations by farmer.
  * `environmental_notes` (string, optional): Microclimate notes.
  * `rainfall_recent` (string, optional, default `"Unknown"`): `"None"`, `"Light"`, `"Moderate"`, `"High"`.
  * `humidity_level` (string, optional, default `"Unknown"`): `"Low"`, `"Normal"`, `"High"`.
  * `temperature_band` (string, optional, default `"Unknown"`): `"Cool (<20°C)"`, `"Warm (20-30°C)"`, `"Hot (>30°C)"`.
  * `recent_weather_event` (string, optional, default `"None"`): Weather anomaly description.
  * `irrigation_status` (string, optional, default `"Unknown"`): `"Rainfed"`, `"Drip"`, `"Flood"`, etc.
  * `soil_moisture_observation` (string, optional, default `"Unknown"`): `"Dry"`, `"Moist"`, `"Waterlogged"`.
  * `field_condition` (string, optional, default `"Unknown"`): Drainage status.
  * `image_whole` (binary file, optional): Whole plant perspective.
  * `image_affected` (binary file, optional): Affected area perspective.
  * `image_detail` (binary file, optional): Close-up leaf/lesion detail.
* **Validation Rules:**
  * Max file size: $10\text{ MB}$ per file (`HTTP 413` if exceeded).
  * Allowed extensions: `.jpg`, `.jpeg`, `.png`, `.webp` (`HTTP 400` if disallowed).
* **Response `201 Created`:** Returns `CaseOut` object with assigned `case_id`, `priority`, `ai_prediction`, and `ai_confidence`.

---

### 3.3 List Observations
* **Method:** `GET`
* **Path:** `/api/cases`
* **Query Parameters:**
  * `status` (string, optional): Filter by `"Submitted"`, `"Under Review"`, `"More Information Required"`, `"Expert Validated"`.
  * `priority` (string, optional): Filter by `"High"`, `"Medium"`, `"Low"`.
  * `crop` (string, optional): Substring match on crop name.
  * `location` (string, optional): Substring match on location name.
  * `low_confidence_only` (boolean, optional, default `false`): Filter cases where `ai_confidence < 60.0`.
* **Response `200 OK`:** Array of `CaseOut` items ordered by priority (High first), then submission timestamp descending.

---

### 3.4 Retrieve Single Case Detail
* **Method:** `GET`
* **Path:** `/api/cases/{case_id}`
* **Response `200 OK`:** Full `CaseOut` object including all nested `images` and `reviews`.
* **Response `404 Not Found`:** If `case_id` does not exist.

---

### 3.5 Submit Authoritative Expert Review
* **Method:** `POST`
* **Path:** `/api/cases/{case_id}/review`
* **Content-Type:** `application/json`
* **Request Schema (`ExpertReviewCreate`):**
```json
{
  "expert_category": "Early Blight (Alternaria solani)",
  "validation_status": "confirmed",
  "comments": "Target-like concentric brown rings evident. Apply copper fungicide 2g/L.",
  "urgency": "Urgent"
}
```
* **Status Mapping Rules:**
  * `"confirmed"` or `"rejected_ai"` $\rightarrow$ Case status becomes `"Expert Validated"`.
  * `"more_info_needed"` $\rightarrow$ Case status becomes `"More Information Required"`.
  * Other status $\rightarrow$ Case status becomes `"Under Review"`.
  * If `urgency == "Urgent"` $\rightarrow$ Case priority escalates to `"High"`.
  * **Strict Invariant:** Expert validation always overrides the preliminary AI hypothesis.

---

### 3.6 Farmer Case Follow-up Resubmission
* **Method:** `POST`
* **Path:** `/api/cases/{case_id}/resubmit`
* **Content-Type:** `multipart/form-data`
* **Request Fields:**
  * `additional_notes` (string, required): Farmer's response to expert inquiry.
  * `new_image` (binary file, optional): Follow-up photographic evidence.
* **Response `200 OK`:** Updated `CaseOut` object with status set to `"Under Review"` and notes appended.

---

### 3.7 MobileNetV3 Vision Category Inference
* **Method:** `POST`
* **Path:** `/api/vision-predict`
* **Content-Type:** `multipart/form-data`
* **Request:** `image` (binary file, required).
* **Response `200 OK`:**
```json
{
  "predicted_class": "fungal",
  "confidence": 87.4,
  "is_high_confidence": true,
  "requires_escalation": false,
  "class_probabilities": {
    "healthy": 0.021,
    "fungal": 0.874,
    "bacterial": 0.052,
    "viral": 0.031,
    "abiotic": 0.022
  },
  "disclaimer": "Preliminary visual category hypothesis (MobileNetV3 transfer learning) — not field validation."
}
```

---

### 3.8 Regional Outbreak Analytics
* **Method:** `GET`
* **Path:** `/api/analytics/regional`
* **Query Parameters:** `crop`, `region`, `severity`, `priority`, `status` (all optional).
* **Response `200 OK`:**
```json
{
  "disclaimer": "Prototype / simulated regional summary for decision support — not real-world disease outbreak surveillance.",
  "filters_applied": {
    "crop": "Tomato",
    "region": null,
    "severity": null,
    "priority": null,
    "status": null
  },
  "total_matching_cases": 14,
  "total_regions": 3,
  "active_alerts_count": 1,
  "active_alerts": [
    {
      "region": "Delta Paddy Belt Sector B",
      "risk_level": "Elevated Watch",
      "high_priority_count": 3,
      "total_cases": 6,
      "dominant_disease": "Fungal leaf blight",
      "message": "Cluster notification: 3 high-priority case(s) detected in Delta Paddy Belt Sector B...",
      "recommended_action": "Deploy extension field officer for in-person sample collection.",
      "disclaimer": "Simulated regional alert — prototype decision support."
    }
  ],
  "regions": [
    {
      "region_name": "Delta Paddy Belt Sector B",
      "approx_latitude": 10.82,
      "approx_longitude": 79.20,
      "total_cases": 6,
      "high_priority_count": 3,
      "validated_count": 2,
      "under_review_count": 3,
      "needing_info_count": 1,
      "dominant_disease": "Fungal leaf blight",
      "moisture_risk_count": 4,
      "risk_level": "Elevated Watch",
      "badge_class": "warning",
      "crops": ["Tomato"]
    }
  ]
}
```

---

### 3.9 Operational Latency ($T_{review}$) Analytics
* **Method:** `GET`
* **Path:** `/api/analytics/t-review`
* **Response `200 OK`:**
```json
{
  "disclaimer": "Simulated latency measured across prototype database records — illustrative operational metrics.",
  "baseline_assumption_hours": 120.0,
  "mvp_target_hours": 24.0,
  "total_validated_cases": 8,
  "overall_t_review": {
    "count": 8,
    "mean": 18.5,
    "median": 16.2,
    "min": 4.5,
    "max": 36.0
  },
  "overall_submission_to_review": {
    "count": 8,
    "mean": 12.1,
    "median": 10.5,
    "min": 2.0,
    "max": 22.0
  },
  "by_priority": {
    "High": {"count": 4, "mean": 8.2, "median": 7.5, "min": 4.5, "max": 14.0},
    "Medium": {"count": 3, "mean": 24.0, "median": 22.0, "min": 18.0, "max": 32.0},
    "Low": {"count": 1, "mean": 36.0, "median": 36.0, "min": 36.0, "max": 36.0}
  },
  "by_crop": {
    "Tomato": {"count": 4, "mean": 14.2, "median": 12.0},
    "Rice": {"count": 2, "mean": 20.1, "median": 20.1},
    "Potato": {"count": 2, "mean": 25.0, "median": 25.0}
  },
  "by_region": {
    "Delta Paddy Belt Sector B": {"count": 5, "mean": 15.0, "median": 14.0}
  }
}
```

---

### 3.10 AI Performance Monitoring & Calibration
* **Method:** `GET`
* **Path:** `/api/analytics/ai-monitoring`
* **Response `200 OK`:**
```json
{
  "disclaimer": "AI metrics reflect prototype decision-support performance and simulated triage. Expert review remains authoritative.",
  "total_cases_evaluated": 12,
  "cases_with_ai_confidence": 12,
  "confidence_distribution_buckets": {
    "<50%": 2,
    "50-59%": 4,
    "60-69%": 2,
    "70-79%": 2,
    "80-89%": 2,
    "90-100%": 0
  },
  "low_confidence_threshold": 60.0,
  "low_confidence_cases": 6,
  "escalation_rate_percent": 50.0,
  "expert_review_metrics": {
    "total_reviews": 8,
    "confirmed_ai_agreements": 5,
    "expert_overrides_rejections": 2,
    "more_information_requests": 1,
    "uncertain_reviews": 0,
    "agreement_rate_percent": 62.5,
    "override_rate_percent": 25.0
  },
  "model_benchmark": {
    "evaluation_type": "Phase 2.1 Held-Out Test Evaluation",
    "dataset_type": "prototype_benchmark_synthetic",
    "model_architecture": "MobileNetV3-Small",
    "total_test_samples": 15,
    "overall_accuracy": 100.0,
    "macro_f1": 100.0,
    "weighted_f1": 100.0
  }
}
```

---

### 3.11 Supported Languages Endpoint
* **Method:** `GET`
* **Path:** `/api/i18n/languages`
* **Response `200 OK`:**
```json
[
  {"code": "en", "name": "English", "nativeName": "English"},
  {"code": "ta", "name": "Tamil", "nativeName": "தமிழ்"}
]
```

---

### 3.12 Translation Dictionary Endpoint
* **Method:** `GET`
* **Path:** `/api/i18n/{lang}`
* **Parameters:** `lang` (`"en"` or `"ta"`). Any unknown language code falls back to English.
* **Response `200 OK`:** JSON key-value map containing all 135 translation tokens.
