# Systematic Error Analysis & Failure Patterns

**Project:** Agricultural Disease Observation & Expert Escalation System  
**Review:** Review 1 (~35% Scope)  

---

## 1. Explicit Dataset Limitation Notice

> [!WARNING]
> **CRITICAL LIMITATION:**  
> **The current prototype dataset is insufficient to establish generalizable performance across diverse agricultural microclimates.**  
> Microclimate-specific generalization cannot yet be established because the prototype dataset is small and composed of synthetic reference examples. All performance figures represent a prototype simulation, not field-validated agronomic accuracy.

---

## 2. Systematic Error Groupings

To prevent recurring diagnostic failures, the system categorizes observed classification discrepancies across six distinct dimensions:

### 2.1 By Crop Type
* **Tomato:** High representation in prototype dataset. Fungal early blight and powdery mildew show distinct concentric and surface morphologies, yielding higher base confidence (72%–85%).
* **Cassava:** Low sample representation. Mixed foliar symptoms (mottling vs leaf curling) can cause confusion between viral mosaic and mite feeding injury.
* **Potato vs. Tomato:** Shared Solanaceae family symptoms (e.g. *Phytophthora* or *Alternaria* blights) require careful stem inspection that cannot be resolved without a close-up photo.

### 2.2 By Symptom Morphology
* **Concentric Rings / Distinct Pustules:** High classifier agreement ($> 80\%$). Distinctive morphological boundaries facilitate reliable candidate categorization.
* **General Chlorosis & Wilting:** High error and ambiguity rate (Confidence drops to 51%–54%). Wilting may be caused by vascular bacterial wilt, root-zone fungal damping off, or simply acute drought stress. The system correctly triggers **Low-Confidence High-Priority Escalation** for these cases.
* **Water-Soaked Margins:** Bacterial vs. fungal leaf spot overlap. Requires expert confirmation.

### 2.3 By Crop Growth Stage
* **Seedling Stage:** High vulnerability and high error propensity. Early seedling damping-off presents similar symptoms regardless of whether the causal agent is *Pythium*, *Rhizoctonia*, or waterlogging.
* **Flowering & Fruiting Stage:** Pathological symptoms are more morphologically defined on mature foliage, but agronomic urgency is highest because yield loss is imminent.

### 2.4 By Microclimate & Environmental Context
* **High Humidity / Rainy Basins (e.g. Delta Paddy Belt):** Fungal spores proliferate rapidly; water droplets on leaves can mimic bacterial ooze or create lens reflections that artificially degrade image quality scores.
* **Arid / Saline Drylands (e.g. Eastern Dryland Sub-basin):** Fertilizer salt burn and heat scorch closely mimic fungal leaf blights, leading to false-positive pathogen hypotheses.
* **Demonstrated Failure Case (`CASE-2026-005`):** The AI hypothesized fungal/abiotic salinity scorch (68% confidence), but the human expert correctly diagnosed severe Nitrogen deficiency based on the diagnostic V-shaped midrib chlorosis pattern. The expert override was recorded immutably.

### 2.5 By Photographic Quality & Exposure
* **Blurry Images (Laplacian Variance $< 100.0$):** High-frequency edge information is lost; fine spot halos and fungal mycelia cannot be resolved, forcing the confidence score downward.
* **Low Light / Heavy Canopy Shadow (Luminance $< 40.0$):** Dark shadows conceal color contrast between necrotic centers and chlorotic halos, degrading model confidence and triggering farmer guidance prompts.

### 2.6 By Confidence Distribution
* **High Confidence ($\ge 75\%$):** Distinct symptoms (e.g., powdery mildew, concentric rings) on clear, well-lit photos.
* **Low Confidence ($< 60\%$):** Triggered in 4 out of 12 benchmark cases (33.3%). Directly activates the safety escalation protocol to route cases to high-priority expert triage.

---

## 3. Prototype Failure Summary

| Error Pattern ID | Diagnostic Failure Pattern | Observed Trigger | Review 1 Safety Response |
| :--- | :--- | :--- | :--- |
| **ERR-01** | Low-light evening photograph | Mean luminance $< 40.0$ | Automated farmer advice + confidence degradation |
| **ERR-02** | Acute wilting ambiguity | Seedling stage drooping | Calibrated conf $< 60\%$ $\to$ Escalation to High Priority |
| **ERR-03** | Abiotic deficiency vs Blight confusion | V-shaped yellowing on maize | Expert overrides AI $\to$ Override logged for retraining |
| **ERR-04** | Camera motion blur | Laplacian variance $< 100.0$ | Non-blocking warning: "Hold phone steady and refocus" |
