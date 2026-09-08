# Data Schema Specification

**Project:** Agricultural Disease Observation & Expert Escalation System  
**Database Engine:** SQLite 3.x (Zero-configuration local deployment)  
**ORM:** SQLAlchemy 2.0  

---

## 1. Entity Relationship Overview

```
+---------------------------+             +---------------------------+
|           cases           | 1         * |          images           |
|---------------------------|-------------|---------------------------|
| case_id (PK)              |             | image_id (PK)             |
| anonymous_farmer_id       |             | case_id (FK -> cases)     |
| crop                      |             | image_type                |
| variety                   |             | file_path                 |
| location                  |             | quality_score             |
| latitude (approx 2 dec)   |             | quality_warnings          |
| longitude (approx 2 dec)  |             | farmer_advice             |
| crop_stage                |             | source                    |
| symptoms                  |             | license                   |
| severity                  |             | created_at                |
| first_symptom_time        |             +---------------------------+
| submission_time           |
| ai_prediction             |             +---------------------------+
| ai_confidence             | 1         * |       expert_reviews      |
| ai_alternative            |-------------|---------------------------|
| priority                  |             | review_id (PK)            |
| priority_reason           |             | case_id (FK -> cases)     |
| status                    |             | expert_category           |
| expert_validation         |             | validation_status         |
| expert_comments           |             | comments                  |
| expert_review_time        |             | urgency                   |
| farmer_notes              |             | reviewed_at               |
| environmental_notes       |             +---------------------------+
| created_at                |
| updated_at                |             +---------------------------+
+---------------------------+             |         audit_logs        |
                                          |---------------------------|
                                          | id (PK autoincrement)     |
                                          | case_id (index)           |
                                          | action                    |
                                          | actor_role                |
                                          | details                   |
                                          | timestamp                 |
                                          +---------------------------+
```

---

## 2. Table Specifications

### 2.1 Table: `cases`
Primary record representing an individual standardized disease observation submitted by a farmer.

| Column | Type | Nullable | Constraints & Description |
| :--- | :--- | :--- | :--- |
| `case_id` | String(64) | No | Primary Key. Formatted as `CASE-2026-XXX`. |
| `anonymous_farmer_id` | String(64) | No | Indexed. Formatted as `FARMER-ANON-XXXX`. Zero PII. |
| `crop` | String(64) | No | Indexed. Crop type (Tomato, Maize, Rice, Potato, etc.). |
| `variety` | String(64) | Yes | Optional cultivar name. |
| `location` | String(128) | No | Indexed. Village or administrative sub-block. |
| `latitude` | Float | Yes | Approximate GPS coordinate rounded to 2 decimal places ($\approx 1.1\text{ km}$). |
| `longitude` | Float | Yes | Approximate GPS coordinate rounded to 2 decimal places ($\approx 1.1\text{ km}$). |
| `crop_stage` | String(64) | No | Seedling, Vegetative, Flowering, Fruiting, Mature. |
| `symptoms` | Text | No | Comma-separated list or JSON array of reported symptoms. |
| `severity` | String(32) | No | Default `Medium`. Options: `Low`, `Medium`, `Severe`. |
| `first_symptom_time` | DateTime | No | Date/time farmer first observed the symptom in the field. |
| `submission_time` | DateTime | No | Timestamp when the record was received by the API. |
| `ai_prediction` | String(128) | Yes | Preliminary AI hypothesis (e.g. `Fungal-like symptom`). |
| `ai_confidence` | Float | Yes | Calibrated model confidence percentage (0.0 to 100.0). |
| `ai_alternative` | String(128) | Yes | Next closest diagnostic candidate. |
| `priority` | String(32) | No | Triage score: `High`, `Medium`, `Low`. |
| `priority_reason` | Text | Yes | Explanatory rationale for the assigned priority. |
| `status` | String(64) | No | `Submitted`, `Under Review`, `More Information Required`, `Expert Validated`. |
| `expert_validation` | String(128) | Yes | Authoritative diagnosis supplied by human agronomist. |
| `expert_comments` | Text | Yes | Prescribed cultural/chemical controls and advisory notes. |
| `expert_review_time` | DateTime | Yes | Authoritative timestamp when expert completed review. |
| `farmer_notes` | Text | Yes | Qualitative farmer notes and follow-up responses. |
| `environmental_notes`| Text | Yes | Microclimate context (recent rainfall, hail, waterlogging). |
| `created_at` | DateTime | No | System timestamp. |
| `updated_at` | DateTime | No | Last modification timestamp. |

### 2.2 Table: `images`
Stores photographic evidence associated with each case, along with image quality diagnostics.

| Column | Type | Nullable | Constraints & Description |
| :--- | :--- | :--- | :--- |
| `image_id` | String(64) | No | Primary Key. Formatted as `IMG-XXXX-A`. |
| `case_id` | String(64) | No | Foreign Key references `cases.case_id`. Indexed. |
| `image_type` | String(32) | No | `whole_plant`, `affected_area`, or `leaf_detail`. |
| `file_path` | String(256) | No | Relative public URL (e.g. `/uploads/CASE-2026-001_whole.jpg`). |
| `quality_score` | Float | No | Synthetic quality rating (0.0 to 100.0). |
| `quality_warnings` | Text | Yes | JSON array of detected flaws (blur, dark, bright, duplicate). |
| `farmer_advice` | Text | Yes | JSON array of actionable photo guidance for the farmer. |
| `source` | String(128) | No | Data origin (e.g. `Project-created synthetic benchmark`). |
| `license` | String(128) | No | Open licensing designation (`CC-BY-4.0`). |
| `created_at` | DateTime | No | Timestamp of upload. |

### 2.3 Table: `expert_reviews`
Immutable history of expert reviews, enabling multi-expert consultation and audit compliance.

| Column | Type | Nullable | Constraints & Description |
| :--- | :--- | :--- | :--- |
| `review_id` | String(64) | No | Primary Key. Formatted as `REV-XXXX`. |
| `case_id` | String(64) | No | Foreign Key references `cases.case_id`. Indexed. |
| `expert_category` | String(64) | No | Pathogen category or confirmed disease name. |
| `validation_status` | String(64) | No | `confirmed`, `rejected_ai`, `more_info_needed`, `uncertain`. |
| `comments` | Text | Yes | Agronomic advisory notes and treatment directions. |
| `urgency` | String(32) | No | `Routine`, `Prompt`, `Urgent`. |
| `reviewed_at` | DateTime | No | Authoritative review timestamp. |

### 2.4 Table: `audit_logs`
Append-only log for full traceability of triage and validation events.

| Column | Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | No | Autoincrementing Primary Key. |
| `case_id` | String(64) | No | Associated case identifier. |
| `action` | String(64) | No | Action type (e.g. `CASE_CREATED`, `EXPERT_REVIEW_SUBMITTED`). |
| `actor_role` | String(64) | No | `Farmer`, `Extension Officer`, `Expert`, `System`. |
| `details` | Text | Yes | Description of payload or state transition. |
| `timestamp` | DateTime | No | UTC timestamp of event. |
