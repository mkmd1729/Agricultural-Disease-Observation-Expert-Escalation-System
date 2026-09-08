# Agricultural Disease Observation and Expert Escalation System

[![Review 1 Scope](https://img.shields.io/badge/Review%201%20Scope-~35%25%20Completed-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)]()

> A robust, reproducible, and farmer-friendly MVP designed for agricultural extension teams to enable early crop symptom reporting, automated photographic quality analysis, transparent AI decision support, and rapid authoritative expert escalation.

---

## 1. Problem Statement

Agricultural extension teams worldwide face a persistent operational challenge:
* **Late Reporting:** Smallholders frequently wait until crop damage is extensive before seeking assistance.
* **Inconsistent Photography:** Field photos sent via consumer messaging apps are frequently blurry, dark, or lack whole-plant context.
* **Missing Critical Metadata:** Crucial agronomic context (crop growth stage, date of onset, regional weather) is rarely recorded.
* **Delayed Interventions:** Agronomists spend over 60% of their triage time asking basic clarifying questions, delaying timely disease control.

---

## 2. Solution Overview

This system provides a standardized vertical slice:
1. **Farmer-Friendly Reporting Wizard:** 5-step intuitive flow with large touch targets, visual symptom cards, and zero agricultural jargon.
2. **Standardized Photo Guidance & Real-Time Quality Check:** Guided 3-tier photo upload (Whole plant, Affected branch, Close-up detail) with automated checks for blur, underexposure, overexposure, and non-crop images.
3. **Calibrated Experimental AI Assistance:** Non-diagnostic candidate hypothesis generation with explicit confidence scoring.
4. **Automated Triage Escalation:** Automatic promotion to **High Priority** when confidence is $< 60\%$ or during vulnerable flowering/fruiting stages.
5. **Authoritative Expert Validation Station:** Phytopathologists inspect evidence and validate or override AI hypotheses.
6. **Primary Performance Metric:** Dynamic calculation of **Time from first symptom to useful expert review** ($T_{review}$).

---

## 3. Architecture

### System Flow
```
Farmer Mobile UI (5-Step Wizard)
  │
  ▼
FastAPI Observation Engine (POST /api/cases)
  ├── Image Quality Engine (Laplacian Variance, Exposure, dHash)
  ├── Experimental AI Assistant (Calibrated Confidence & Candidate Category)
  └── Multi-Factor Priority Engine (Severity, Growth Stage, <60% Escalation)
  │
  ▼
SQLite Database (cases, images, expert_reviews, audit_logs)
  ├── Extension Officer Dashboard (Triage queue, KPIs, Charts)
  └── Expert Validation Workstation (Authoritative review & Treatment advice)
  │
  ▼
Metrics & Error Analysis (T_review = T_expert - T_first_symptom)
```

For full Mermaid and ASCII diagrams, refer to [`docs/architecture.md`](docs/architecture.md).

---

## 4. Technology Stack

* **Backend:** Python 3.13, FastAPI, Uvicorn, Pydantic v2
* **Database:** SQLite 3.x with SQLAlchemy 2.0 (Zero-configuration local persistence)
* **Image Processing & ML:** Pillow (PIL), Laplacian gradient variance, perceptual difference hashing (dHash), heuristic agronomic classifier
* **Frontend:** Responsive Single-Page Application (HTML5, Vanilla JavaScript, High-Contrast CSS)
* **Testing:** Pytest, HTTPX

---

## 5. Quick Start & Setup

### Prerequisites
* Python 3.10+ (tested on Python 3.13)
* Windows, macOS, or Linux

### Installation & Execution

1. **Clone or Navigate to Repository:**
   ```bash
   cd agri-disease-observation
   ```

2. **Create & Activate Virtual Environment:**
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Seed Synthetic Demo Cases:**
   ```bash
   python scripts/seed_demo_data.py
   ```

5. **Start Application Server:**
   ```bash
   python run_server.py
   ```

6. **Open in Browser:**
   ```text
   http://127.0.0.1:8000
   ```

---

## 6. Demonstration Walkthrough

The web interface provides 4 synchronized tabs:
* **🌾 Farmer Report:** Walk through the 5-step wizard, attach a sample photo from `data/test_images/`, observe the real-time quality notice, and submit.
* **📊 Officer Dashboard:** View real-time KPI cards, $T_{review}$ distribution, filter by crop or priority, and inspect case details.
* **🔬 Expert Station:** Select any case from the queue, inspect whole-plant vs detail images, and submit an authoritative diagnosis.
* **⚡ Edge Cases:** Test the 3 required failure scenarios in one click:
  1. *Poor Image (Blurry/Dark):* Triggers actionable advice without blocking submission.
  2. *Low Confidence (<60%):* Refuses to claim a diagnosis and escalates to High Priority.
  3. *AI/Expert Conflict:* Human expert decision overrides the AI proposal; mismatch recorded for error analysis.

---

## 7. Dataset & Ethics

* **Source:** Project-created ethical synthetic foliar assets (`ml/dataset/`) and simulated observations.
* **Licensing:** Creative Commons Attribution 4.0 (`CC-BY-4.0`).
* **Privacy:** Strictly zero personally identifiable information (PII). No human faces, private houses, or vehicle plates. Geocoordinates are generalized to ~1.1 km ($\approx 2$ decimal places).
* **Metadata:** Fully cataloged in [`data/metadata.csv`](data/metadata.csv).

---

## 8. Evaluation & Experimental Results

To reproduce the benchmark evaluation across all test cases:
```bash
python ml/evaluate.py
```

### Measured Results vs. Baseline Assumptions

> [!NOTE]
> Baseline figures represent **illustrative/simulated assumptions** for prototype benchmarking, not validated historical field measurements.

| Metric | Baseline Assumption | MVP Target | Measured Prototype Result | Result Status |
| :--- | :--- | :--- | :--- | :--- |
| **Time to Expert Review ($T_{review}$)** | 120.0 hours | $\le 24.0$ hours | **45.7 hours** | Measured from prototype DB |
| **Submission to Review Time** | 48.0 hours | $\le 12.0$ hours | **8.4 hours** | Measured from prototype DB |
| **Complete Standardized Reports** | 35.0% | $\ge 85.0\%$ | **100.0%** | Measured from prototype DB |
| **Usable Photographic Evidence** | 40.0% | $\ge 85.0\%$ | **100.0%** | Measured from prototype DB |
| **Follow-up / Re-contact Rate** | 65.0% | $\le 15.0\%$ | **16.7%** | Measured from prototype DB |
| **AI / Expert Agreement Rate** | N/A | $\ge 70.0\%$ | **83.3%** | Measured from prototype DB |

---

## 9. Automated Testing

Run the comprehensive automated test suite:
```bash
pytest
```
Run the 15-step formal acceptance test suite:
```bash
python scripts/run_acceptance_tests.py
```

---

## 10. Review 1 Status & Scope Boundaries

* **Completed (~35% Scope):** End-to-end vertical slice, farmer 5-step wizard, image quality analysis, priority engine, expert workstation, dynamic $T_{review}$ metric, 3 edge cases, full documentation suite.
* **Pending for Review 2 & 3:** Convolutional deep learning model (MobileNetV3), offline ServiceWorker draft synchronization, multilingual vernacular audio.
