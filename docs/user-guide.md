# Agricultural Disease Observation & Escalation App — User Guide

**Project:** Agricultural Disease Observation & Expert Escalation System  
**Version:** Review 1 MVP  

---

## 1. Role 1: Smallholder Farmer

The Farmer module provides an intuitive, 5-step wizard designed for quick, accessible field reporting with large touch targets and minimal typing.

### Step-by-Step Reporting Workflow
1. **Step 1: Select Your Crop**
   * Tap the large visual card matching your crop (e.g. *Tomato*, *Maize*, *Rice*, *Potato*, *Wheat*, *Cassava*, *Soybean*).
   * Optionally type the specific variety or hybrid in the text box.
   * Tap **"Next: What do you see? →"**.
2. **Step 2: Describe Symptoms**
   * Tap all observed symptoms (e.g., *Leaf Spots*, *Yellowing*, *Wilting*, *Powdery Coating*, *Rust Pustules*).
   * Select overall symptom severity: **Low**, **Medium**, or **Severe**.
   * Pick the date when symptoms were first noticed in the field.
   * Tap **"Next: Take Photos →"**.
3. **Step 3: Capture Standardized Photographs**
   * Use the visual guidance cards to take up to 3 photographs:
     * **Photo 1 (Whole plant):** Stand back 1–2 meters to show the standing crop canopy and soil line.
     * **Photo 2 (Affected area):** Focus 30–50 cm away on the diseased branch or leaf cluster.
     * **Photo 3 (Close-up detail):** Optional high-detail shot showing spot margins and pustules.
   * Notice real-time instant quality feedback: if your photo is blurry or too dark, the app will advise you how to retake it immediately without blocking your submission.
   * Tap **"Next: Location & Growth Stage →"**.
4. **Step 4: Location & Growth Stage**
   * Select the vulnerable crop growth stage: *Seedling*, *Vegetative*, *Flowering*, *Fruiting*, or *Mature*.
   * Select your general village or agricultural district. *(Your exact home coordinates are never collected; coordinates are generalized to ~1.1 km for privacy).*
   * Optionally type brief field notes (e.g., recent heavy rain).
   * Tap **"Next: Review & Submit →"**.
5. **Step 5: Review & Submit**
   * Check your observation summary.
   * Tap **"Submit Observation for Expert Review ✓"**.
   * Note your unique **Case Reference ID** (e.g., `CASE-2026-001`). Extension officers and experts will triage your case immediately.

---

## 2. Role 2: Extension Officer

The Extension Officer Dashboard enables rapid triage across district smallholders, monitoring operational throughput, and identifying emergency outbreaks.

### Dashboard Operations
1. **Monitor Real-Time KPIs:**
   * **Total Observations:** Cumulative standardized submissions.
   * **Pending Triage:** Submissions awaiting expert review.
   * **High Priority:** Cases escalated due to severe symptoms, vulnerable flowering/fruiting stages, or low AI confidence.
   * **Average $T_{review}$:** Mean hours from first farmer symptom observation to authoritative expert validation.
2. **Filter & Prioritize Cases:**
   * Use the status dropdown to filter by `Submitted`, `Under Review`, or `More Information Required`.
   * Filter by priority (`High`, `Medium`, `Low`) to address urgent yield threats first.
   * Check **"Low Confidence (<60%) Only"** to inspect cases where the experimental AI could not establish a reliable hypothesis.
3. **Inspect Case Evidence:**
   * Click the **"Inspect"** button on any table row to open the complete evidence modal.
   * Review whole-plant context, close-up lesions, and image quality metrics.

---

## 3. Role 3: Agricultural Expert & Phytopathologist

The Expert Station provides the authoritative workstation where certified agronomists validate observations, override automated suggestions, and prescribe treatments.

### Validation Workflow
1. **Select a Case from the Queue:**
   * Click any case in the left sidebar. High-priority and pending cases are highlighted.
2. **Review Multi-Modal Field Evidence:**
   * Compare reported symptoms, growth stage, and environmental stressors against the photographic evidence.
   * Inspect the **Preliminary AI Hypothesis** and its calibrated confidence score.
3. **Apply Authoritative Expert Action:**
   * Choose the **Validation Decision**:
     * **Confirm Observation / Diagnosis:** You agree with the preliminary AI category.
     * **Reject / Override AI Suggestion:** You identify a different disorder (e.g., overriding a fungal blight hypothesis with nutrient deficiency).
     * **Request More Information:** You need the farmer to perform a diagnostic check (e.g. cutting stem to inspect vascular ooze).
     * **Mark as Uncertain:** Inconclusive foliar symptoms requiring laboratory testing.
   * Set **Urgency Level:** *Routine*, *Prompt*, or *Urgent*.
   * Type your **Authoritative Diagnosis** and **Agronomic Recommendations**.
   * Click **"Save Authoritative Expert Validation ✓"**.
   * The system immediately updates the authoritative case record, logs the review timestamp, and calculates the final $T_{review}$ metric.
