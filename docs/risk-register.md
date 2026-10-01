# Project Risk Register & Tradeoff Analysis

**Project:** Agricultural Disease Observation & Expert Escalation System  
**Stage:** Phase 2 Complete (~70% Scope: Hybrid Vision ML, Offline Workflow, Environmental Context & Case Tracking)  

---

## 1. Comprehensive Risk Analysis Matrix

| # | Risk Description | Type | Likelihood | Impact | Severity | Planned Mitigation Strategy | Phase 2 Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **R1** | **Incorrect AI prediction leading to erroneous field treatment** | Social / Operational | Medium | High | **High** | Enforce human expert validation as strictly authoritative. Label all ML proposals as "Preliminary Decision Support Only". | **Implemented** (Expert override authority strictly enforced) |
| **R2** | **Farmer over-relies on preliminary AI output** | Social | High | High | **High** | UI prominently highlights calibrated uncertainty. System refuses to display "Disease Confirmed" without expert signoff. | **Implemented** (Prominent disclaimers & uncertainty badges) |
| **R3** | **Poor image quality (blur, severe shadow) prevents diagnosis** | Operational | High | Medium | **Medium** | Built-in automated image checks (Laplacian variance, exposure thresholds) with actionable photo-taking advice. | **Implemented** (Real-time live feedback & non-blocking guidance) |
| **R4** | **Intermittent or absent internet connectivity in rural fields** | Operational | High | High | **High** | Offline PWA shell caching (`sw.js`) and persistent IndexedDB observation queue with auto-sync upon reconnection. | **Implemented** (Phase 2.4 Offline-first workflow) |
| **R5** | **Privacy leakage of smallholder identity or home property** | Social | Low | High | **Medium** | Zero PII collected (no names, phones, emails). Spatial coordinates generalized to ~1.1 km ($\approx 2$ decimals). | **Implemented** (Anonymous farmer & case IDs, approximate coordinates) |
| **R6** | **Model bias across microclimates, soil types, and cultivars** | Technical / Social | High | Medium | **High** | Systematic error grouping by microclimate and stage; explicit documentation that dataset is not universally generalizable. | **Implemented** (Comprehensive error analysis & explicit limitations) |
| **R7** | **System maintenance burden overwhelmed by infrastructure complexity** | Operational | Medium | Medium | **Medium** | Zero-configuration SQLite database, unified FastAPI backend, minimal dependencies. | **Implemented** (Zero-maintenance lightweight stack) |
| **R8** | **False alarms triggering panic or unnecessary chemical spraying** | Environmental / Operational | Medium | High | **High** | AI suggestions cannot trigger chemical interventions without agricultural expert confirmation. | **Implemented** (Decision support only; agronomic advice reserved for experts) |
| **R9** | **Missed virulent disease or rapidly spreading contagion** | Environmental | Low | Critical | **High** | Automatic high-priority triage escalation for low-confidence instances ($< 60\%$) and severe symptoms. | **Implemented** (Automated priority escalation logic) |
| **R10** | **Duplicate sync submissions during network flakiness** | Operational | Medium | Medium | **Medium** | Idempotent client sync tracking (`client_sync_id`), server state verification, and duplicate rejection. | **Implemented** (Phase 2.4 & 2.7 duplicate prevention) |
| **R11** | **Farmer inquiry drop-off when agronomist requests more data** | Operational | High | Medium | **Medium** | Intuitive Case Tracking tab (`#view-track`) with status timeline stepper and one-click photo/notes resubmission form. | **Implemented** (Phase 2.5 Case Tracking workflow) |

---

## 2. Benefits vs. Costs & Risks Tradeoff Analysis

### 2.1 Benefits
* **Dramatic Reduction in Triage Latency:** $T_{review}$ compressed from an illustrative 120-hour baseline down to ~8.4 hours from submission (and ~45.7 hours from symptom onset on prototype benchmarks).
* **Guaranteed Diagnostic Integrity:** Expert agronomists retain 100% authoritative control. AI acts solely as a prioritization and decision-support assistant.
* **Smallholder Field Accessibility:** Works seamlessly offline in remote areas without data signal. Preserves battery and storage with lightweight models (~6.2 MB) and fast CPU execution (~10.5 ms).
* **Privacy by Design:** Farmers can seek urgent agricultural help without fear of personal data exploitation, property boundary leaks, or commercial spam.

### 2.2 Costs & Inherent Risks
* **Risk of Model Over-Reliance:** Smallholders may prematurely trust preliminary suggestions before expert signoff. Continually mitigated via high-contrast disclaimers and refusal to recommend chemical inputs without expert authorization.
* **Compute Footprint on Mobile Devices:** Running full neural vision models client-side can drain older rural phones. Mitigated in Phase 2 by keeping PyTorch inference on the server/edge backend while the client handles lightweight preprocessing and offline queueing.
* **Expert Workload Management:** While triage prioritization sorts urgent cases first, agricultural extension systems face chronic agronomist shortages. Decision support reduces inspection time per case, but cannot eliminate human reviewer bottlenecks.
