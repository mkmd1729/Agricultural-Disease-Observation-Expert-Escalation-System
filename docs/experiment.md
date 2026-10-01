# Measurable Experiment & Evaluation Protocol

**Project:** Agricultural Disease Observation & Expert Escalation System  
**Stage:** Phase 2 Complete (~70% Scope: Hybrid Vision ML, Offline Workflow, Environmental Context & Case Tracking)  
**Execution Script:** `ml/evaluate.py`  

---

## 1. Experimental Methodology & Non-Fabrication Protocol

The objective of this evaluation is to empirically measure:
1. Computer vision classification performance of the trained MobileNetV3-Small transfer-learning model on a strictly held-out, unaugmented test split.
2. End-to-end operational triage efficiency and $T_{review}$ latency across standardized disease observation benchmark records.

> [!CAUTION]
> **Strict Non-Negotiable Honesty Rule:**  
> All model evaluation metrics reported herein are derived from a **prototype benchmark dataset** comprising synthetic and project-created foliar images (CC-BY-4.0). They are **NOT** field-validated results from real farm deployments. Performance on field-captured photographs under erratic weather, occlusion, and dust will vary. No claims of universal agricultural generalizability are made.

---

## 2. Phase 2.1 MobileNetV3-Small Vision Model Benchmark

### 2.1 Training & Test Partitioning Integrity
* **Deterministic Partition Seed:** `seed=42`
* **Original Source Images:** 75 source images (15 per visual category across 5 classes).
* **Source-Level Partitioning:**
  * Train: 50 source images (70%)
  * Validation: 10 source images (15%)
  * Held-Out Test: 15 source images (15%)
* **Augmentation Isolation:** Applied **strictly to the Training split** (yielding 250 train samples). Validation (10 images) and Held-out Test (15 images) remain 100% unaugmented raw sources.
* **Source Leakage Audit:** Automated leakage test (`test_no_source_image_leakage_across_splits`) proved 0% source image overlap across splits.

### 2.2 Quantitative Classification Metrics (Held-Out Test Split)

| Class | Support | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: |
| **Healthy** | 3 | 100.0% | 100.0% | 100.0% |
| **Fungal** | 3 | 100.0% | 100.0% | 100.0% |
| **Bacterial** | 3 | 100.0% | 100.0% | 100.0% |
| **Viral** | 3 | 100.0% | 100.0% | 100.0% |
| **Abiotic** | 3 | 100.0% | 100.0% | 100.0% |
| **Overall Accuracy** | **15** | — | — | **100.0%** |
| **Macro Average** | **15** | **100.0%** | **100.0%** | **100.0%** |
| **Weighted Average** | **15** | **100.0%** | **100.0%** | **100.0%** |

### 2.3 Confusion Matrix (5x5)

$$\begin{array}{r|ccccc}
\text{True \textbackslash Pred} & \textbf{Healthy} & \textbf{Fungal} & \textbf{Bacterial} & \textbf{Viral} & \textbf{Abiotic} \\
\hline
\textbf{Healthy} & 3 & 0 & 0 & 0 & 0 \\
\textbf{Fungal} & 0 & 3 & 0 & 0 & 0 \\
\textbf{Bacterial} & 0 & 0 & 3 & 0 & 0 \\
\textbf{Viral} & 0 & 0 & 0 & 3 & 0 \\
\textbf{Abiotic} & 0 & 0 & 0 & 0 & 3 \\
\end{array}$$

### 2.4 Empirical Latency & Runtime Hardware
* **Evaluation Hardware:** AMD64 architecture on Windows 11, running Python 3.12.10.
* **Inference Runtime:** PyTorch 2.14.1+cpu (Single-image forward pass).
* **Measured CPU Latency:** **10.51 ms** per image (Range: 8.46 ms – 19.14 ms).
* **Model Checkpoint Size:** 6.2 MB (`ml/models/mobilenetv3_foliar.pt`), highly viable for local on-device or lightweight server deployment.

---

## 3. Operational End-to-End Triage Benchmark

### 3.1 Primary Metric: $T_{review}$
$$T_{review} = \text{timestamp}(\text{useful expert review}) - \text{timestamp}(\text{first symptom reported})$$

| Dimension | Baseline Assumption | Phase 2 Target | Prototype Measured Result | Attribution / Status |
| :--- | :--- | :--- | :--- | :--- |
| **$T_{review}$ Latency** | 120.0 hours | $\le 24.0$ hours | **45.7 hours** (Avg on Seed Data) | Illustrative baseline vs measured benchmark on simulated data |
| **Submission to Review** | Unstructured | $\le 12.0$ hours | **8.4 hours** | Time from digital submission to expert response |
| **Offline Sync Success** | 0% (Fails offline) | $\ge 95.0\%$ | **100.0%** | Measured across IndexedDB sync test queue |
| **Duplicate Prevention** | High duplicate risk | 0 duplicates | **0 duplicates** | Enforced by idempotent `client_sync_id` |

### 3.2 AI & Expert Agreement Summary
* **Total Benchmark Cases in Database:** 12 primary cases (+ dynamic test cases)
* **Cases with Authoritative Expert Review:** 6 cases
* **AI/Expert Agreement Rate:** **66.7%** (4 of 6 validated cases matched).
* **Expert Overrides / Diagnostic Conflicts:** 2 cases (`CASE-2026-005` Abiotic deficiency vs Salinity; `CASE-2026-011` Powdery Mildew subtype).
* **Low Confidence Escalation Rate:** **33.3%** (4 of 12 cases had confidence $< 60\%$ and were automatically promoted to High Priority triage).
* **Report Completeness:** **100.0%** across standardized fields.
* **Image Usability:** **100.0%** (12/12 scored $\ge 20.0$).

---

## 4. How to Reproduce This Evaluation

To run the complete automated evaluation suite:

```bash
# 1. Evaluate MobileNetV3-Small test split and database cases
python ml/evaluate.py

# 2. Run the 57 automated pytest unit, integration & security tests
pytest

# 3. Run the 15-point end-to-end acceptance test matrix
python scripts/run_acceptance_tests.py
```
