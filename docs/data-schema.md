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
