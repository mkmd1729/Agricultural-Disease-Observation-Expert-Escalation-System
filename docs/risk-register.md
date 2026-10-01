# Project Risk Register & Tradeoff Analysis
## Agricultural Disease Observation & Expert Escalation System

**Stage:** Phase 3 Complete (100% End-to-End System)  
**Scope:** Standardized Observation, MobileNetV3 Transfer Learning, Hybrid Decision Support, Environmental Context, Offline PWA, Case Tracking, Regional Surveillance, Multilingual i18n, Web Speech Accessibility, and Production Security.

---

## 1. Comprehensive Risk Analysis Matrix

| # | Risk Description | Type | Likelihood | Impact | Severity | Planned Mitigation Strategy | Phase 3 Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **R1** | **Incorrect AI prediction leading to erroneous field treatment** | Social / Operational | Medium | High | **High** | Enforce human expert validation as strictly authoritative. Label all ML proposals as "Preliminary Decision Support Only". | **Implemented** (Expert override authority strictly enforced) |
| **R2** | **Farmer over-relies on preliminary AI output** | Social | High | High | **High** | UI prominently highlights calibrated uncertainty. System refuses to display "Disease Confirmed" without expert signoff. | **Implemented** (Prominent disclaimers & uncertainty badges) |
| **R3** | **Poor image quality (blur, severe shadow) prevents diagnosis** | Operational | High | Medium | **Medium** | Built-in automated image checks (Laplacian variance, exposure thresholds) with actionable photo-taking advice. | **Implemented** (Real-time live feedback & non-blocking guidance) |
| **R4** | **Intermittent or absent internet connectivity in rural fields** | Operational | High | High | **High** | Offline PWA shell caching (`sw.js`) and persistent IndexedDB observation queue with auto-sync upon reconnection. | **Implemented** (Offline-first PWA workflow) |
| **R5** | **Privacy leakage of smallholder identity or home property** | Social | Low | High | **Medium** | Zero PII collected (no names, phones, emails). Spatial coordinates generalized to ~1.1 km ($\approx 2$ decimals). | **Implemented** (Anonymous farmer & case IDs, approximate coordinates) |
| **R6** | **Model bias across microclimates, soil types, and cultivars** | Technical / Social | High | Medium | **High** | Systematic error grouping by microclimate and stage; explicit documentation that dataset is not universally generalizable. | **Implemented** (18-point error analysis & explicit limitations) |
| **R7** | **System maintenance burden overwhelmed by infrastructure complexity** | Operational | Medium | Medium | **Medium** | Zero-configuration SQLite database, unified FastAPI backend, minimal dependencies. | **Implemented** (Zero-maintenance lightweight stack) |
| **R8** | **False alarms triggering panic or unnecessary chemical spraying** | Environmental / Operational | Medium | High | **High** | AI suggestions cannot trigger chemical interventions without agricultural expert confirmation. | **Implemented** (Decision support only; agronomic advice reserved for experts) |
| **R9** | **Missed virulent disease or rapidly spreading contagion** | Environmental | Low | Critical | **High** | Automatic high-priority triage escalation for low-confidence instances ($< 60\%$) and severe symptoms. | **Implemented** (Automated priority escalation logic) |
| **R10** | **Duplicate sync submissions during network flakiness** | Operational | Medium | Medium | **Medium** | Idempotent client sync tracking (`client_sync_id`), server state verification, and duplicate rejection. | **Implemented** (Duplicate prevention in offline sync engine) |
| **R11** | **Farmer inquiry drop-off when agronomist requests more data** | Operational | High | Medium | **Medium** | Intuitive Case Tracking tab (`#view-track`) with status timeline stepper and one-click photo/notes resubmission form. | **Implemented** (Case Tracking & Resubmission workflow) |
| **R12** | **Speech recognition acoustic noise interference in field conditions** | Technical / Usability | High | Low | **Low** | Web Speech API errors trigger non-intrusive fallback notification; manual keyboard/touch input remains fully active; form inputs never cleared. | **Implemented** (Phase 3 Voice Assistant fallback architecture) |
| **R13** | **Linguistic or dialectal divergence between English and Tamil** | Social / Usability | Medium | Medium | **Medium** | 135-token centralized translation dictionary with strict key parity verified by automated unit tests; standard scientific and colloquial terms matched. | **Implemented** (Phase 3 Multilingual i18n subsystem) |
| **R14** | **Malicious or oversized file upload attempts (DoS / Path Traversal)** | Security | Medium | High | **High** | 10 MB strict file size ceiling (HTTP 413), extension whitelist (.jpg/.png/.webp with HTTP 400 rejection), path traversal sanitization, randomized UUIDs. | **Implemented** (Phase 3 Security & Validation engine) |
| **R15** | **Misinterpretation of prototype regional analytics as certified epidemiology** | Scientific / Operational | Medium | Medium | **Medium** | Prominent disclaimers across all regional dashboards explicitly stating data is prototype/simulated decision support, not real-world disease outbreak surveillance. | **Implemented** (Phase 3 Regional Surveillance disclaimers) |

---

## 2. Benefits vs. Costs & Risks Tradeoff Analysis

### 2.1 Benefits
* **Dramatic Reduction in Triage Latency:** $T_{review}$ compressed from an illustrative 120-hour baseline toward an MVP target of 24 hours.
* **Guaranteed Diagnostic Integrity:** Expert agronomists retain 100% authoritative control. AI acts solely as a prioritization and decision-support assistant.
* **Smallholder Field Accessibility:** Works seamlessly offline in remote areas without data signal. Multilingual English and Tamil support empowers local farming communities.
* **Privacy by Design:** Farmers can seek urgent agricultural help without fear of personal data exploitation, property boundary leaks, or commercial spam.

### 2.2 Costs & Inherent Risks
* **Risk of Model Over-Reliance:** Smallholders may prematurely trust preliminary suggestions before expert signoff. Continually mitigated via high-contrast disclaimers and refusal to recommend chemical inputs without expert authorization.
* **Acoustic Noise in Field Dictation:** Background wind and farm equipment can reduce speech recognition accuracy. Handled by treating voice dictation as an optional accessibility convenience rather than a mandatory interface.
* **Expert Workload Management:** While triage prioritization sorts urgent cases first, agricultural extension systems face chronic agronomist shortages. Decision support reduces inspection time per case, but cannot eliminate human reviewer bottlenecks.
