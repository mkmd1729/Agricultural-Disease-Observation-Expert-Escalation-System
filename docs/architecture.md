# System Architecture Specification

**Project:** Agricultural Disease Observation & Expert Escalation System  
**Review:** Review 1 (~35% Scope)  

---

## 1. Architectural Overview

The system provides a standardized vertical slice connecting smallholder farmers, extension officers, and expert plant pathologists. It enforces privacy preservation, real-time photographic quality checking, calibrated experimental AI assistance, and authoritative expert override.

---

## 2. ASCII Architecture Diagram

```
+-------------------------------------------------------------------------------------------------+
|                                        FARMER MOBILE / WEB UI                                   |
|  - 5-Step Intuitive Wizard (Crop -> Symptoms -> Visual Photos -> Location/Stage -> Submit)      |
|  - Real-time client & server-assisted photo quality feedback (Blur, Exposure, Crop Visibility)  |
|  - Zero PII collection (Anonymous Case ID: CASE-2026-001, Anonymous Farmer ID)                  |
+-------------------------------------------------------------------------------------------------+
                                                |
                                    HTTPS / REST POST /api/cases
                                                v
+-------------------------------------------------------------------------------------------------+
|                                      FASTAPI OBSERVATION ENGINE                                 |
|                                                                                                 |
|   +--------------------------+    +--------------------------+    +--------------------------+  |
|   |   Image Quality Engine   |    |  Experimental AI Engine  |    | Priority Scoring Engine  |  |
|   |  - Laplacian Sharpness   |    |  - Non-authoritative     |    |  - Severity weight       |  |
|   |  - Exposure (40 - 225)   |--->|  - Calibrated Confidence |--->|  - Growth Stage risk     |  |
|   |  - Vegetation Ratio      |    |  - Conf < 60% Escalation |    |  - <60% Conf Escalation  |  |
|   |  - Duplicate dHash Check |    |  - Transparent disclaimer|    |  - Contagion indicator   |  |
|   +--------------------------+    +--------------------------+    +--------------------------+  |
+-------------------------------------------------------------------------------------------------+
                                                |
                                                v
+-------------------------------------------------------------------------------------------------+
|                                       SQLITE CASE DATABASE                                      |
|  - Cases (Observation metadata, AI hypotheses, Authoritative expert validation, Status)         |
|  - Images (Local file paths, quality scores, warnings, actionable guidance)                     |
|  - ExpertReviews (Diagnosis, Agreement status, Urgency, Comments, Timestamps)                   |
|  - AuditLogs (Immutable tracking of all state transitions and user actions)                     |
+-------------------------------------------------------------------------------------------------+
                               |                                                 |
                               v                                                 v
+-----------------------------------------------+ +-----------------------------------------------+
|          EXTENSION OFFICER DASHBOARD          | |          EXPERT VALIDATION WORKSTATION        |
|  - Operational KPI summary cards              | |  - Side-by-side evidence inspection           |
|  - T_review distribution & metrics            | |  - Image inspection with quality scores       |
|  - Crop, Location, and Symptom charts         | |  - Authoritative validation or AI override    |
|  - Real-time priority & status filters        | |  - Treatment guidance & urgency assignment    |
+-----------------------------------------------+ +-----------------------------------------------+
                               \                                                 /
                                v                                               v
+-------------------------------------------------------------------------------------------------+
|                               METRICS & SYSTEMATIC ERROR ANALYSIS                               |
|  - T_review calculation: timestamp(useful expert review) - timestamp(first symptom reported)   |
|  - AI vs Expert agreement rate, False Positives, False Negatives, Quality Failure logs          |
|  - Transparent distinction between Baseline Assumptions and Prototype Measurements            |
+-------------------------------------------------------------------------------------------------+
```

---

## 3. Mermaid Flow Diagram

```mermaid
flowchart TD
    subgraph FarmerModule["Farmer Reporting Interface"]
        F1["Farmer Notices Symptom"] --> F2["Opens 5-Step Wizard"]
        F2 --> F3["Selects Crop Card"]
        F3 --> F4["Selects Visual Symptoms & Severity"]
        F4 --> F5["Uploads 3 Guided Photos"]
        F5 --> F6["Selects Village Location & Growth Stage"]
        F6 --> F7["Submits Observation"]
    end

    subgraph BackendAPI["FastAPI Processing Pipeline"]
        F7 --> API["POST /api/cases"]
        API --> IQ["Image Quality Analysis<br/>(Laplacian Variance, Exposure, dHash)"]
        IQ --> AI["Experimental AI Assistance<br/>(Calibrated Confidence & Candidate Category)"]
        AI --> PRIO["Decision-Support Priority Engine<br/>(High / Medium / Low)"]
        PRIO --> DB[("SQLite Database<br/>Cases, Images, Reviews, AuditLogs")]
    end

    subgraph TriageWorkflows["Extension & Expert Workflows"]
        DB --> OD["Extension Officer Dashboard<br/>(Triage Queue, Filters, KPIs)"]
        DB --> EW["Expert Validation Workstation"]
        EW --> VAL["Authoritative Expert Action<br/>(Confirm, Reject AI, Request Info)"]
        VAL --> DB
        VAL --> MET["Primary Metric Engine<br/>T_review = T_expert - T_first_symptom"]
    end

    classDef farmer fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef api fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    classDef expert fill:#fff3e0,stroke:#f57c00,stroke-width:2px;
    class F1,F2,F3,F4,F5,F6,F7 farmer;
    class API,IQ,AI,PRIO,DB api;
    class OD,EW,VAL,MET expert;
```

---

## 4. Privacy & Security Architecture

1. **Anonymous Identifiers:** Farmers are identified via generated tokens (e.g., `FARMER-ANON-8812`). No names, phone numbers, or email addresses are stored.
2. **Spatial Anonymization:** Geocoordinates are truncated to 2 decimal places ($\approx 1.1\text{ km}$ precision), preventing domestic identification while preserving regional microclimate context.
3. **Local File Storage:** Image uploads are stripped of EXIF domestic metadata and saved with hashed filenames in the local `./data/uploads/` sandbox.
