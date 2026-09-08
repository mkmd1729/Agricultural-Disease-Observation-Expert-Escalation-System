# Project Risk Register

**Project:** Agricultural Disease Observation & Expert Escalation System  
**Review:** Review 1 (~35% Scope)  

---

## Comprehensive Risk Analysis Matrix

| # | Risk Description | Type | Likelihood | Impact | Severity | Planned Mitigation Strategy | Review 1 Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **R1** | **Incorrect AI prediction leading to erroneous field treatment** | Social / Operational | Medium | High | **High** | Enforce human expert validation as strictly authoritative. Mark all AI suggestions as "Needs expert validation". | **Implemented** (Expert override authority strictly enforced) |
| **R2** | **Farmer over-relies on preliminary AI output** | Social | High | High | **High** | UI prominently highlights calibrated uncertainty. System refuses to display "Disease Confirmed" without expert signoff. | **Implemented** (Prominent disclaimers & uncertainty badges) |
| **R3** | **Poor image quality (blur, severe shadow) prevents diagnosis** | Operational | High | Medium | **Medium** | Built-in automated image checks (Laplacian variance, exposure thresholds) with actionable photo-taking advice. | **Implemented** (Real-time live feedback & non-blocking guidance) |
| **R4** | **Intermittent or absent internet connectivity in rural fields** | Operational | High | Medium | **Medium** | Lightweight data payload, local form caching, and deferred submission when offline. | **Planned for Review 2** (ServiceWorker local draft caching) |
| **R5** | **Privacy leakage of smallholder identity or home property** | Social | Low | High | **Medium** | Zero PII collected (no names, phones, emails). Spatial coordinates generalized to ~1.1 km ($\approx 2$ decimals). | **Implemented** (Anonymous farmer & case IDs, approximate coordinates) |
| **R6** | **Model bias across microclimates, soil types, and cultivars** | Technical / Social | High | Medium | **High** | Systematic error grouping by microclimate and stage; explicit documentation that dataset is not universally generalizable. | **Implemented** (Comprehensive error analysis & explicit limitations) |
| **R7** | **System maintenance burden overwhelmed by infrastructure complexity** | Operational | Medium | Medium | **Medium** | Zero-configuration SQLite database, unified FastAPI backend, minimal dependencies. | **Implemented** (Zero-maintenance lightweight stack) |
| **R8** | **False alarms triggering panic or unnecessary chemical spraying** | Environmental / Operational | Medium | High | **High** | AI suggestions cannot trigger chemical interventions without agricultural expert confirmation. | **Implemented** (Decision support only; agronomic advice reserved for experts) |
| **R9** | **Missed virulent disease or rapidly spreading contagion** | Environmental | Low | Critical | **High** | Automatic high-priority triage escalation for low-confidence instances ($< 60\%$) and severe symptoms. | **Implemented** (Automated priority escalation logic) |

---

## Risk Monitoring & Audit Protocol

1. **Audit Logs:** Every transition (Case created, AI prediction generated, Expert review submitted) is logged immutably in the `audit_logs` database table.
2. **Override Tracking:** Cases where an expert rejects or overrides an AI hypothesis are tracked automatically for post-hoc error analysis and model retraining.
3. **Continuous Review:** The risk register is re-evaluated at each milestone review as field validation data becomes available.
