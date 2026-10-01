# Comprehensive Testing Strategy & Error Boundary Documentation
## Agricultural Disease Observation & Expert Escalation System

---

## 1. Testing Philosophy & Quality Invariants

The testing strategy is designed around strict agricultural domain realities, safety-critical decision support invariants, and scientific software integrity:

1. **Non-Negotiable Expert Authority:** Tests verify that an agricultural expert's diagnostic decision unconditionally overrides any AI hypothesis. AI predictions are never mutated or deleted on the record, ensuring complete forensic traceability and auditability.
2. **Defensive Triage Escalation:** Any observation with AI confidence $< 60.0\%$ or occurring during a critical crop growth stage (e.g. Flowering, Seedling, Tillering) must be escalated to `"High"` priority triage.
3. **Zero Data Leakage:** Transfer learning and vision pipeline tests strictly verify that split partitioning occurs on source images *before* any augmentation is synthesized, preventing synthetic duplicate leakage across train, validation, and held-out test splits.
4. **Location Privacy Preservation:** Geolocation tests verify that latitude and longitude coordinates are rounded to at most 2 decimal places ($\approx 1.1\text{ km}$ precision), preventing farmstead deanonymization.
5. **Robust Error Boundaries & Accessibility Fallbacks:** Network dropouts, microphone permission denials, oversized uploads, and corrupt image binaries are tested to guarantee graceful degradation without application crashes or exposed stack traces.

---

## 2. Test Suite Architecture & Summary Table

The test suite contains **57 automated unit, integration, and regression tests** executed via `pytest`, plus **15 end-to-end acceptance criteria** executed via `scripts/run_acceptance_tests.py`.

| Test File | Focus Area | Test Count | Key Boundaries Tested |
| :--- | :--- | :--- | :--- |
| `backend/tests/test_api.py` | Core API & Case Lifecycle | 5 | Submission, case listing, retrieval, 404 handling, anonymous IDs |
| `backend/tests/test_edge_cases.py` | 7 System Edge Cases | 7 | Blur/underexposure, low confidence, expert override, abiotic confusion, sensor noise, drought/flood paradox, tracking loop |
| `backend/tests/test_expert_workstation.py` | Expert Workstation & Reviews | 4 | Authoritative overrides, urgency escalation, status state machine, audit log immutability |
| `backend/tests/test_hybrid_inference.py` | Hybrid Decision Engine | 6 | Vision + symptoms + environmental context, drought/waterlogging rules, confidence penalization |
| `backend/tests/test_multilingual_and_i18n.py` | English & Tamil i18n | 6 | Supported languages, dictionary completeness, 100% key parity, non-empty strings, domain keys, fallback |
| `backend/tests/test_priority.py` | Multi-Factor Triage Engine | 3 | High severity, critical growth stage escalation, low-confidence escalation trigger |
| `backend/tests/test_quality.py` | Computer Vision Image Quality | 5 | Laplacian blur score, luminance underexposure/overexposure, green vegetative coverage, advice generation |
| `backend/tests/test_regional_analytics.py` | Regional Outbreak & Latency | 5 | Regional clustering, multi-criteria filtering, location privacy (2 decimals), $T_{review}$ stats, AI performance metrics |
| `backend/tests/test_resubmit_flow.py` | Case Tracking & Follow-up | 4 | Follow-up inquiry status, farmer resubmission, status reset to Under Review, audit trails |
| `backend/tests/test_security_and_validation.py` | Security & Input Validation | 6 | 10 MB file size limit (HTTP 413), extension whitelist (.jpg/.png/.webp), rejection of .exe/.sh (HTTP 400), path traversal guard |
| `backend/tests/test_vision_model.py` | MobileNetV3 Transfer Learning | 5 | Architecture dimensions, raw logit output (no premature Softmax), batch shape `(N, 5)`, zero leakage across splits |
| `tests/test_end_to_end.py` | End-to-End Operational Loop | 1 | Complete farmer submit -> triage -> officer list -> expert override -> audit trail verification |

---

## 3. Granular Test Suite Specifications

### 3.1 Vision Model & Dataset Integrity (`test_vision_model.py`)
* `test_mobilenetv3_returns_raw_logits`: Validates that the model classifier outputs raw logits before any Softmax constraint. Verifies output tensor shape `(batch_size, 5)`.
* `test_dataset_zero_leakage`: Verifies deterministically that no `source_image_id` appears in more than one split (Train, Validation, Test).
* `test_evaluation_results_structure`: Verifies that held-out test evaluation artifacts (`evaluation_results.json`) contain valid accuracy, precision, recall, and confusion matrix structures.

### 3.2 Hybrid Inference Engine (`test_hybrid_inference.py`)
* `test_hybrid_decision_combines_vision_and_symptoms`: Verifies that visual category probabilities and structured symptom checklists are properly synthesized into preliminary hypotheses.
* `test_environmental_context_adjusts_hypothesis`: Verifies that heavy rainfall combined with water-soaked lesions elevates bacterial blight probability over abiotic scorch.
* `test_low_confidence_escalation_flag`: Verifies that confidence $< 60.0\%$ triggers the escalation flag for mandatory human review.

### 3.3 Security & Input Safeguards (`test_security_and_validation.py`)
* `test_allowed_image_extensions`: Validates that `.jpg`, `.jpeg`, `.png`, and `.webp` are accepted regardless of casing.
* `test_disallowed_image_extensions`: Asserts that `.exe`, `.sh`, `.py`, `.pdf`, or missing extensions are rejected with `HTTP 400 Bad Request`.
* `test_oversized_file_rejected`: Asserts that file payloads exceeding $10\text{ MB}$ (`MAX_FILE_SIZE_BYTES + 1`) trigger `HTTP 413 Content Too Large`.
* `test_path_traversal_sanitization`: Asserts that filenames like `../../../../etc/passwd.jpg` are stripped to `passwd.jpg` and saved under `/uploads/` using randomized UUIDs without directory traversal vulnerability.

### 3.4 Regional Outbreak & $T_{review}$ Analytics (`test_regional_analytics.py`)
* `test_regional_analytics_endpoint`: Validates cluster grouping by location, dominant pathogen identification, moisture risk aggregation, and active alert generation.
* `test_regional_analytics_filtering`: Validates multi-criteria filtering by crop, priority, and severity.
* `test_location_privacy_preservation`: Asserts that regional centroid coordinates do not leak high-precision GPS (strictly $\le 2$ decimal places).
* `test_t_review_analytics`: Validates calculation of $T_{review} = t_{expert} - t_{symptom}$ and $T_{sub\_review} = t_{expert} - t_{submission}$ across overall cases, priority tiers, and crop categories.
* `test_ai_monitoring_analytics`: Validates confidence histogram buckets (`<50%`, `50-59%`, `60-69%`, etc.), escalation rate calculation, and expert agreement/override metrics.

### 3.5 Multilingual Internationalization (`test_multilingual_and_i18n.py`)
* `test_supported_languages_endpoint`: Validates English (`en`) and Tamil (`ta`) presence.
* `test_strict_key_parity_between_english_and_tamil`: Asserts that every one of the 135 keys defined in English has an exact corresponding translation in Tamil ($en\_keys \setminus ta\_keys = \emptyset$ and $ta\_keys \setminus en\_keys = \emptyset$).
* `test_translation_strings_non_empty`: Verifies that no translation key has an empty string or whitespace-only value.
* `test_essential_domain_keys_present`: Asserts that critical crops, symptoms, growth stages, environmental context, and ethical disclaimers exist in both languages.

---

## 4. Acceptance Test Matrix (15/15 Criteria)

The automated script `scripts/run_acceptance_tests.py` validates the complete 15-point specification matrix:

| Acceptance Test | Requirement | Result |
| :--- | :--- | :--- |
| **Test 1** | Create farmer observation case | **PASS** |
| **Test 2** | Select crop (e.g. Tomato, Rice) | **PASS** |
| **Test 3** | Enter structured symptoms | **PASS** |
| **Test 4** | Enter crop growth stage | **PASS** |
| **Test 5** | Enter approximate location (privacy-protected) | **PASS** |
| **Test 6** | Upload project-created crop image | **PASS** |
| **Test 7** | Generate standardized anonymous case ID | **PASS** |
| **Test 8** | Run image quality and triage scoring logic | **PASS** |
| **Test 9** | Display case in officer dashboard | **PASS** |
| **Test 10** | Expert validates observation case | **PASS** |
| **Test 11** | Update authoritative case status | **PASS** |
| **Test 12** | Record expert review timestamp | **PASS** |
| **Test 13** | Calculate operational latency $T_{review}$ | **PASS** |
| **Test 14** | Execute $\ge 3$ edge case scenarios | **PASS** |
| **Test 15** | Generate and update experimental evaluation artifacts | **PASS** |

---

## 5. How to Execute Tests

### Running the Pytest Suite
```powershell
pytest
```
*Expected Result:* `57 passed, 2 warnings in ~8.5s`

### Running the Full Acceptance Test Suite
```powershell
python scripts/run_acceptance_tests.py
```
*Expected Result:* `ALL 15 ACCEPTANCE TESTS COMPLETED SUCCESSFULLY WITH 100% PASS RATE.`

### Re-seeding Demo Database
```powershell
python scripts/seed_demo_data.py
```
