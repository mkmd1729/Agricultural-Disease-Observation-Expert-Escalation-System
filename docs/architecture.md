# System Architecture Specification
## Agricultural Disease Observation & Expert Escalation System

**Stage:** Phase 3 Complete (100% End-to-End System)  
**Scope:** Standardized Observation, MobileNetV3 Transfer Learning, Hybrid Decision Support, Environmental Context, Offline PWA, Case Tracking, Regional Surveillance, Multilingual i18n, Web Speech Accessibility, and Production Security.

---

## 1. Architectural Overview

The Agricultural Disease Observation & Expert Escalation System connects smallholder farmers, agricultural extension officers, and expert plant pathologists into a coordinated, closed-loop decision support network. The architecture provides:

1. **Standardized Observation & Photographic Quality Engine:** Structured 5-step wizard with real-time OpenCV blur (Laplacian variance), exposure (mean luminance), and vegetative coverage analysis with actionable farmer advice.
2. **Real Computer Vision Service:** MobileNetV3-Small transfer learning running on CPU, classifying foliar conditions into five core classes (Healthy, Fungal, Bacterial, Viral, Abiotic) with zero cross-split data leakage.
3. **Hybrid Decision Support Engine:** Combines visual classification probabilities ($w_{\text{vis}} = 0.55$) with structured symptom checklists ($w_{\text{sym}} = 0.45$), crop growth stage vulnerability, and microclimate context to generate calibrated preliminary hypotheses.
4. **Environmental & Microclimate Context:** Captures recent rainfall, humidity, soil moisture, irrigation type, and weather events to resolve diagnostic paradoxes (e.g. drought vs waterlogging wilt).
5. **Authoritative Human-in-the-Loop Expert Governance:** Plant pathologists retain exclusive diagnostic authority. Expert overrides unconditionally supersede AI hypotheses while preserving immutable audit logs.
6. **Offline-First PWA:** Service worker cached application shell, IndexedDB queue storage (`AgriOfflineDB`), idempotent sync tracking, and network status state machines.
7. **Farmer Case Tracking & Resubmission Loop:** Transparent case status tracking and clarification workflow allowing farmers to answer expert inquiries and upload follow-up photos.
8. **Multilingual Internationalization (English & Tamil):** Centralized 135-token translation dictionary with strict key parity and input preservation across language switches.
9. **Web Speech Voice Accessibility:** Text-to-Speech (TTS) and Speech-to-Text (STT) dictation in Tamil (`ta-IN`) and Indian English (`en-IN`) with transparent fallbacks.
10. **Regional Outbreak Analytics & $T_{review}$ Monitoring:** Spatial clustering, risk matrix generation, outbreak alerts, operational latency tracking ($T_{review}$), and live AI confidence monitoring.
11. **Production Security Safeguards:** 10 MB file size limit, extension whitelisting, path traversal sanitization, and approximate coordinate rounding ($\le 2$ decimals).

---

## 2. Comprehensive System Architecture Diagram

```
+---------------------------------------------------------------------------------------------------------+
|                                         FARMER INTERFACE (PWA)                                          |
|  - 5-Step Intuitive Reporting Wizard (Touch-first, Photographic Guidance)                               |
|  - Multilingual Switcher: English (en) / Tamil (ta) with Form Input Preservation                        |
|  - Web Speech Voice Assistant: TTS Read Aloud & STT Dictation (ta-IN / en-IN)                            |
|  - Case Tracking & Resubmission Station (Status Stepper, Clarification Upload, Expert Notes)           |
|  - Service Worker Cache (sw.js) for Offline Shell & Asset Persistence                                  |
|  - Client-Side IndexedDB Storage (AgriOfflineDB: drafts & queued observations)                         |
|  - Online / Offline State Machine with Auto-Sync & Idempotent Sync Tracking                            |
+---------------------------------------------------------------------------------------------------------+
                                                  |
                                   HTTPS / REST API (or Offline Queue)
                                                  v
+---------------------------------------------------------------------------------------------------------+
|                                       FASTAPI BACKEND SERVICE                                           |
|                                                                                                         |
|   +--------------------------+    +--------------------------+    +----------------------------------+  |
|   |   Image Quality Engine   |    |  MobileNetV3 Vision Svc  |    |  Hybrid Decision Support Engine  |  |
|   |  - Laplacian Variance    |    |  - MobileNetV3-Small     |    |  - Concordance Reinforcement     |  |
|   |  - Exposure Bounds       |--->|  - Raw Logits & Softmax  |--->|  - Conflict Penalty (<60%)       |  |
|   |  - Vegetation Ratio      |    |  - 5 Foliar Classes      |    |  - Environmental Modulation      |  |
|   |  - Security & 10MB Limit |    |  - Zero Data Leakage     |    |  - "Preliminary Hypothesis" Only |  |
|   +--------------------------+    +--------------------------+    +----------------------------------+  |
|                                                                                   |                     |
|                                                                                   v                     |
|   +----------------------------------------------------------+    +----------------------------------+  |
|   |                Relational Persistence Layer              |    |     Priority Scoring Engine      |  |
|   |  - cases (Symptoms, Stage, Environmental Context, Prio)  |<---|  - Symptom Severity              |  |
|   |  - images (Sanitized Paths, Quality Scores, Advice)      |    |  - Crop Stage Vulnerability      |  |
|   |  - expert_reviews (Diagnosis, Urgency, Status)           |    |  - Low Confidence Escalation     |  |
|   |  - audit_logs (Immutable audit trail of transitions)     |    |  - Microclimate Stress Factor    |  |
|   +----------------------------------------------------------+    +----------------------------------+  |
+---------------------------------------------------------------------------------------------------------+
        |                                        |                                        |
        v                                        v                                        v
+-----------------------+      +-----------------------------------+      +-------------------------------+
|   OFFICER DASHBOARD   |      |   REGIONAL OUTBREAK ANALYTICS     |      |       EXPERT WORKSTATION      |
| - Multi-Criteria      |      | - Cluster Risk Matrix             |      | - 3-Column Case Inspection    |
|   Triage Filter       |      | - Spatial Moisture Risk           |      | - Visual vs Symptom Review    |
| - Real-Time Priority  |      | - Outbreak Watch Alert Badges     |      | - Authoritative Override      |
|   Sorting             |      | - Granular T_review Breakdown     |      | - Request More Information    |
| - KPI Summary Cards   |      | - AI Confidence Histogram         |      | - Agronomic Treatment Advice  |
+-----------------------+      +-----------------------------------+      +-------------------------------+
```

---

## 3. Component Interaction Sequence

```mermaid
sequenceDiagram
    autonumber
    actor Farmer as Farmer / Field Agent
    participant PWA as Offline PWA Client
    participant API as FastAPI Backend
    participant QC as OpenCV Quality Engine
    participant ML as MobileNetV3 + Hybrid
    participant DB as SQLite / PostgreSQL
    actor Officer as Extension Officer
    actor Expert as Plant Pathologist

    Farmer->>PWA: Enter crop, symptoms, stage, microclimate
    Farmer->>PWA: Upload photo evidence
    PWA->>QC: Check blur, exposure, vegetation
    QC-->>PWA: Quality Score & Actionable Advice
    Farmer->>PWA: Submit Observation (Online or Offline Queue)
    PWA->>API: POST /api/cases (Validated, Coordinates Rounded to 2 Decimals)
    API->>ML: MobileNetV3 visual inference + hybrid rules
    ML-->>API: Preliminary Hypothesis (Confidence %)
    API->>DB: Persist Case & assign Priority
    Officer->>API: GET /api/analytics/regional (Surveillance Matrix)
    Expert->>API: GET /api/cases?priority=High
    Expert->>API: POST /api/cases/{id}/review (Authoritative Diagnosis)
    API->>DB: Update authoritative status -> Expert Validated; Record T_review
    Farmer->>PWA: Track Case / Resubmit -> View Expert Instructions
```

---

## 4. Key Architectural Invariants

1. **Non-Negotiable Expert Authority:** The AI model is an advisory assistant; the human expert decision is authoritative and final.
2. **Mandatory Low-Confidence Escalation:** Observations with AI confidence $< 60.0\%$ automatically escalate to `High Priority` triage.
3. **Location Privacy Preservation:** GPS coordinates are rounded to at most 2 decimal places ($\approx 1.1\text{ km}$ area precision).
4. **Zero Data Leakage:** Source images are deterministically partitioned before augmentation.
5. **Multilingual Key Parity:** English and Tamil dictionaries maintain 100% token parity.
