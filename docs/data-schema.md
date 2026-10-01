# Data Schema Specification

**Project:** Agricultural Disease Observation & Expert Escalation System  
**Stage:** Phase 2 Complete (~70% Scope)  
**Database Engine:** SQLite 3.x (Zero-configuration local deployment)  
**ORM:** SQLAlchemy 2.0 (with Pydantic v2 validation)  

---

## 1. Entity Relationship Overview

```
+-----------------------------------+             +---------------------------+
|               cases               | 1         * |          images           |
|-----------------------------------|-------------|---------------------------|
| case_id (PK)                      |             | image_id (PK)             |
| anonymous_farmer_id               |             | case_id (FK -> cases)     |
| crop                              |             | image_type                |
| variety                           |             | file_path                 |
| location                          |             | quality_score             |
| latitude (approx 2 decimals)      |             | quality_warnings          |
| longitude (approx 2 decimals)     |             | farmer_advice             |
| crop_stage                        |             | source                    |
| symptoms                          |             | license                   |
| severity                          |             | created_at                |
| first_symptom_time                |             +---------------------------+
| submission_time                   |
| ai_prediction                     |             +---------------------------+
| ai_confidence                     | 1         * |       expert_reviews      |
| ai_alternative                    |-------------|---------------------------|
| priority                          |             | review_id (PK)            |
| priority_reason                   |             | case_id (FK -> cases)     |
| status                            |             | expert_category           |
| expert_validation                 |             | validation_status         |
| expert_comments                   |             | comments                  |
| expert_review_time                |             | urgency                   |
| farmer_notes                      |             | reviewed_at               |
| environmental_notes               |             +---------------------------+
| rainfall_recent          [NEW P2] |
| humidity_level           [NEW P2] |             +---------------------------+
| temperature_band         [NEW P2] |             |         audit_logs        |
| recent_weather_event     [NEW P2] |             |---------------------------|
| irrigation_status        [NEW P2] |             | id (PK autoincrement)     |
| soil_moisture_observation[NEW P2] |             | case_id (index)           |
| field_condition          [NEW P2] |             | action                    |
| created_at                        |             | actor_role                |
| updated_at                        |             | details                   |
+-----------------------------------+             | timestamp                 |
                                                  +---------------------------+
```

---

## 2. Server Table Specifications

### 2.1 Table: `cases`
Primary record representing an individual standardized disease observation submitted by a farmer or field agent.

| Column | Type | Nullable | Constraints & Description |
| :--- | :--- | :--- | :--- |
| `case_id` | String(64) | No | Primary Key. Formatted as `CASE-2026-XXX`. |
| `anonymous_farmer_id` | String(64) | No | Indexed. Formatted as `FARMER-ANON-XXXX`. Zero PII. |
| `crop` | String(64) | No | Indexed. Crop type (Tomato, Maize, Rice, Potato, etc.). |
| `variety` | String(64) | Yes | Optional cultivar or hybrid name. |
| `location` | String(128) | No | Indexed. Village or administrative sub-block. |
| `latitude` | Float | Yes | Approximate GPS coordinate rounded to 2 decimal places ($\approx 1.1\text{ km}$). |
| `longitude` | Float | Yes | Approximate GPS coordinate rounded to 2 decimal places ($\approx 1.1\text{ km}$). |
| `crop_stage` | String(64) | No | Seedling, Vegetative, Flowering, Fruiting, Mature. |
| `symptoms` | Text | No | Comma-separated list or JSON array of reported symptoms. |
| `severity` | String(32) | No | Default `Medium`. Options: `Low`, `Medium`, `Severe`. |
| `first_symptom_time` | DateTime | No | Date/time farmer first observed the symptom in the field. |
| `submission_time` | DateTime | No | Timestamp when the record was received by the API. |
| `ai_prediction` | String(128) | Yes | Preliminary AI hypothesis (e.g. `Fungal foliar symptom`). |
| `ai_confidence` | Float | Yes | Calibrated model confidence percentage (0.0 to 100.0). |
| `ai_alternative` | String(128) | Yes | Next closest diagnostic candidate. |
| `priority` | String(32) | No | Triage score: `High`, `Medium`, `Low`. |
| `priority_reason` | Text | Yes | Explanatory rationale for the assigned priority. |
| `status` | String(64) | No | `Submitted`, `Under Review`, `More Information Required`, `Expert Validated`. |
| `expert_validation` | String(128) | Yes | Authoritative diagnosis supplied by human agronomist. |
| `expert_comments` | Text | Yes | Prescribed cultural/chemical controls and advisory notes. |
| `expert_review_time` | DateTime | Yes | Authoritative timestamp when expert completed review. |
| `farmer_notes` | Text | Yes | Qualitative farmer notes and follow-up responses. |
| `environmental_notes`| Text | Yes | Free-text weather notes. |
| `rainfall_recent` | String(64) | Yes | **Phase 2.3:** `None`, `Light`, `Moderate`, `High`, `Unknown`. |
| `humidity_level` | String(64) | Yes | **Phase 2.3:** `Low`, `Normal`, `High`, `Unknown`. |
| `temperature_band` | String(64) | Yes | **Phase 2.3:** `Cool (<20°C)`, `Warm (20-30°C)`, `Hot (>30°C)`, `Unknown`. |
| `recent_weather_event` | String(128)| Yes| **Phase 2.3:** `None`, `Hailstorm`, `Flood`, `Monsoon downpour`. |
| `irrigation_status` | String(64) | Yes | **Phase 2.3:** `Rainfed`, `Canal Irrigated`, `Drip / Sprinkler`, `Borewell`. |
| `soil_moisture_observation` | String(64)| Yes| **Phase 2.3:** `Dry`, `Moist`, `Waterlogged`, `Unknown`. |
| `field_condition` | String(64) | Yes | **Phase 2.3:** `Well Drained`, `Moderate Drainage`, `Poor Drainage`. |
| `created_at` | DateTime | No | System creation timestamp. |
| `updated_at` | DateTime | No | Last modification timestamp. |

### 2.2 Table: `images`
Stores photographic evidence associated with each case, along with image quality diagnostics.

| Column | Type | Nullable | Constraints & Description |
| :--- | :--- | :--- | :--- |
| `image_id` | String(64) | No | Primary Key. Formatted as `IMG-XXXX-A`. |
| `case_id` | String(64) | No | Foreign Key references `cases.case_id`. Indexed. |
| `image_type` | String(32) | No | `whole_plant`, `affected_area`, `leaf_detail`, or `resubmitted_detail`. |
| `file_path` | String(256) | No | Relative public URL (e.g. `/uploads/CASE-2026-001_leaf_detail_xxx.jpg`). |
| `quality_score` | Float | No | Synthetic quality rating (0.0 to 100.0). |
| `quality_warnings` | Text | Yes | JSON array of detected flaws (`blurry`, `dark`, `bright`, `duplicate`). |
| `farmer_advice` | Text | Yes | JSON array of actionable photo guidance for the farmer. |
| `source` | String(128) | No | Data origin (e.g. `Farmer Upload`, `Synthetic Demonstration Dataset`). |
| `license` | String(128) | No | Open licensing designation (`CC-BY-4.0`). |
| `created_at` | DateTime | No | Timestamp of upload. |

### 2.3 Table: `expert_reviews`
Records authoritative plant pathology reviews and validation history.

| Column | Type | Nullable | Constraints & Description |
| :--- | :--- | :--- | :--- |
| `review_id` | String(64) | No | Primary Key. Formatted as `REV-XXXX`. |
| `case_id` | String(64) | No | Foreign Key references `cases.case_id`. Indexed. |
| `expert_category` | String(128) | No | Confirmed diagnosis name (e.g. `Early Blight (Alternaria solani)`). |
| `validation_status` | String(32) | No | `confirmed`, `rejected_ai`, `more_info_needed`, `uncertain`. |
| `comments` | Text | Yes | Expert agronomist recommendations, dosage, cultural controls. |
| `urgency` | String(32) | No | `Routine`, `Prompt`, `Urgent`. |
| `reviewed_at` | DateTime | No | Exact timestamp when expert submitted review. |

### 2.4 Table: `audit_logs`
Immutable audit log tracking all case creation, priority elevation, and status transition events.

| Column | Type | Nullable | Constraints & Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | No | Primary Key (Autoincrement). |
| `case_id` | String(64) | No | Indexed case reference. |
| `action` | String(64) | No | `CASE_CREATED`, `CASE_RESUBMITTED`, `EXPERT_REVIEW_SUBMITTED`. |
| `actor_role` | String(32) | No | `Farmer`, `Officer`, `Expert`, `System`. |
| `details` | Text | Yes | Human-readable event description and AI match status. |
| `timestamp` | DateTime | No | Timestamp of the event. |

---

## 3. Client-Side Offline Schema (IndexedDB: `AgriOfflineDB`)

In Phase 2.4, the client runs a local IndexedDB schema for offline resilience:

### Store: `queue`
- **KeyPath:** `client_sync_id` (String: `OFFLINE-<timestamp>-<hash>`)
- **Indexes:** `status`, `created_at`
- **Record Structure:**
  ```json
  {
    "client_sync_id": "OFFLINE-1727788000-A9F2B",
    "data": { "crop": "Tomato", "symptoms": ["leaf_spots"], ... },
    "status": "queued",
    "created_at": "2026-10-01T10:00:00Z",
    "retry_count": 0,
    "last_error": null,
    "server_case_id": null
  }
  ```

### Store: `drafts`
- **KeyPath:** `id` (String: `current_draft`)
- **Record Structure:** Stores incomplete observation wizard form state across browser restarts.

---

## 4. Migration Strategy
All Phase 2 schema modifications were applied using non-destructive SQLite migrations (`ALTER TABLE cases ADD COLUMN ...`) executed automatically inside `init_db()`. Existing Phase 1 records remain 100% intact.

---

## 5. Phase 3 Analytical, Internationalization & Security Schemas

### 5.1 Security & File Upload Constraints
* **Uploads Directory:** Files stored on filesystem under `/uploads/` using randomized filenames: `{case_id}_{image_type}_{uuid}.{ext}`.
* **Maximum File Size:** 10 MB (`10,485,760 bytes`). Files exceeding this trigger `HTTP 413 Content Too Large`.
* **Extension Whitelist:** `.jpg`, `.jpeg`, `.png`, `.webp`. Disallowed extensions trigger `HTTP 400 Bad Request`.
* **Path Traversal Guard:** `Path(filename).name` sanitization removes directory traversal sequences (`../`).
* **Spatial Truncation:** `latitude` and `longitude` are rounded to 2 decimal places ($\approx 1.1\text{ km}$ precision) before storage to prevent farmstead deanonymization.

### 5.2 Regional Outbreak Analytics (`GET /api/analytics/regional`)
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

### 5.3 Operational Latency ($T_{review}$) Schema (`GET /api/analytics/t-review`)
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
    "Tomato": {"count": 4, "mean": 14.2, "median": 12.0}
  },
  "by_region": {
    "Delta Paddy Belt Sector B": {"count": 5, "mean": 15.0, "median": 14.0}
  }
}
```

### 5.4 AI Performance Monitoring Schema (`GET /api/analytics/ai-monitoring`)
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

### 5.5 Multilingual Internationalization Schemas
* **`GET /api/i18n/languages`:**
```json
[
  {"code": "en", "name": "English", "nativeName": "English"},
  {"code": "ta", "name": "Tamil", "nativeName": "தமிழ்"}
]
```
* **`GET /api/i18n/{lang}`:**
```json
{
  "app_title": "string",
  "nav_farmer": "string",
  "nav_tracking": "string",
  "nav_officer": "string",
  "nav_expert": "string",
  "nav_regional": "string",
  "... 135 total key-value translation tokens with 100% parity across en and ta ...": "string"
}
```

