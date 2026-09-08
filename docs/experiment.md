# Measurable Experiment & Evaluation Protocol

**Project:** Agricultural Disease Observation & Expert Escalation System  
**Evaluation Scope:** Review 1 Prototype (~35% Scope)  
**Execution Script:** `ml/evaluate.py`  

---

## 1. Experimental Methodology

The objective of this experiment is to measure the end-to-end performance of the standardized disease observation pipeline across 12 synthetic benchmark cases.

> [!CAUTION]
> **Non-Negotiable Honesty Rule Disclaimer:**  
> The results recorded here represent a **prototype/simulated evaluation** on synthetic test data. They are **NOT** field-validated measurements from actual agricultural extension deployments. The current dataset is intentionally small and insufficient to establish universal generalizability.

### Experimental Variables
* **Input Features:** Crop type, reported symptoms, growth stage, environmental notes, and 3-tier guided photos.
* **Evaluation Dimensions:**
  1. Primary Metric: Time from first symptom to useful expert review ($T_{review}$).
  2. Image Quality Gate: Usability rate, sharpness blur detection, underexposure, and duplicate detection.
  3. AI Calibrated Confidence: Escalation rate for low-confidence instances ($< 60\%$).
  4. Diagnostic Concordance: Agreement rate between experimental AI proposals and authoritative human expert diagnoses.

---

## 2. Benchmark Cases Evaluation Record

| Case ID | Crop | Stage | AI Hypothesis | Conf% | Expert Diagnosis | Agreement Status | Priority |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `CASE-2026-001` | Tomato | Flowering | Fungal-like symptom | 74.0% | *Pending Review* | Pending | High |
| `CASE-2026-002` | Tomato | Fruiting | Fungal-like symptom | 72.0% | Early Blight (*Alternaria*) | **MATCH (Agreed)** | Medium |
| `CASE-2026-003` | Potato | Vegetative | Fungal-like symptom | 58.0% | *Pending Review* | Pending | **High (Low Conf)** |
| `CASE-2026-004` | Rice | Seedling | Wilting symptom | 51.0% | *Pending Review* | Pending | **High (Low Conf)** |
| `CASE-2026-005` | Maize | Vegetative | Abiotic Salinity Scorch | 68.0% | Nitrogen Deficiency | **OVERRIDE (Conflict)**| Medium |
| `CASE-2026-006` | Rice | Tillering | Bacterial-like symptom | 76.0% | Bacterial Blight (*Xanthomonas*) | **MATCH (Agreed)** | High |
| `CASE-2026-007` | Cassava | Vegetative | Viral-like (Mosaic) | 80.0% | Cassava Mosaic Geminivirus | **MATCH (Agreed)** | Medium |
| `CASE-2026-008` | Wheat | Tillering | Healthy crop appearance | 88.0% | Healthy Stand | **MATCH (Agreed)** | Low |
| `CASE-2026-009` | Potato | Flowering | Wilting symptom | 54.0% | *More Info Needed* | Follow-up | **High (Low Conf)** |
| `CASE-2026-010` | Tomato | Fruiting | Fungal-like symptom | 57.0% | *Pending Review* | Pending | **High (Low Conf)** |
| `CASE-2026-011` | Tomato | Flowering | Fungal (Powdery Mildew)| 85.0% | Powdery Mildew (*Oidium*) | **MATCH (Agreed)** | High |
| `CASE-2026-012` | Rice | Tillering | Fungal-like (Rust) | 82.0% | *Under Review* | Resubmitted | Medium |

---

## 3. Quantitative Evaluation Metrics

### 3.1 Primary Metric: $T_{review}$
$$T_{review} = \text{timestamp}(\text{useful expert review}) - \text{timestamp}(\text{first symptom reported})$$

* **Baseline Assumption (Illustrative):** 120.0 hours
* **MVP Target:** $\le 24.0$ hours
* **Measured Prototype Result (Across 6 Validated Cases):** **45.7 hours**
* **Average Submission to Review Time:** 8.4 hours  
*(The remaining delay is primarily the farmer observation lag before submitting the case, demonstrating that structured mobile entry dramatically compresses triage time once reported).*

### 3.2 Report Completeness & Image Usability
* **Standardized Report Completeness:** **100.0%** (12/12 cases contained crop, symptoms, stage, location, and photos).
* **Photographic Usability Rate:** **100.0%** (12/12 images scored $\ge 20.0$ usability threshold).
* **Detected Image Flaws:**
  * Blurry Image Warnings: 1 instance (detected via Laplacian variance $< 100.0$).
  * Underexposed (Dark) Warnings: 1 instance (detected via mean luminance $< 40.0$).
* **Expert Re-Contact Rate:** **16.7%** (1 of 6 reviewed cases required follow-up streaming test).

### 3.3 AI Concordance & Calibration
* **Cases with Authoritative Expert Validation:** 6 cases
* **AI/Expert Agreement Rate:** **83.3%** (5 of 6 validated cases matched).
* **Expert Overrides / Diagnostic Conflicts:** 1 case (`CASE-2026-005` where AI hypothesized salinity scorch but expert diagnosed nitrogen deficiency).
* **Low Confidence Escalation Rate:** **33.3%** (4 of 12 cases had confidence $< 60\%$ and were automatically escalated to High Priority).
* **False Positives:** 0 (AI never diagnosed disease on healthy foliage).
* **False Negatives:** 0 (AI never diagnosed healthy on diseased foliage).

---

## 4. Reproducing This Experiment

To execute the automated evaluation suite directly against the local SQLite database:

```bash
python ml/evaluate.py
```
