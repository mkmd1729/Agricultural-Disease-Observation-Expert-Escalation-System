# Agricultural Disease Observation & Escalation App — User Guide

**Project:** Agricultural Disease Observation & Expert Escalation System  
**Stage:** Phase 2 Complete (~70% Scope: Hybrid Vision ML, Offline Workflow, Environmental Context & Case Tracking)  

---

## 1. Role 1: Smallholder Farmer

The Farmer module provides an intuitive, high-contrast, touch-optimized interface designed for quick, accessible field reporting with minimal typing, complete offline capability, and two-way inquiry tracking.

### 1.1 Step-by-Step Reporting Workflow
1. **Step 1: Select Your Crop**
   * Tap the large visual card matching your crop (*Tomato*, *Maize*, *Rice*, *Potato*, *Wheat*, *Cassava*, *Soybean*).
   * Tap **"Next: What do you see? →"**.
2. **Step 2: Describe Symptoms & Severity**
   * Tap observed symptoms (e.g. *Leaf Spots*, *Yellowing*, *Wilting*, *Powdery Coating*, *Rust Pustules*, *Bacterial Ooze*).
   * Select symptom severity: **Low**, **Medium**, or **Severe**.
   * Pick the date when symptoms were first noticed in the field.
   * Tap **"Next: Take Photos →"**.
3. **Step 3: Capture Standardized Photographs**
   * Follow the 3 visual guidance cards:
     * **Photo 1 (Whole plant):** Stand back 1–2 meters to show overall canopy architecture and soil line.
     * **Photo 2 (Affected area):** Focus 30–50 cm away on the diseased branch or leaf cluster.
     * **Photo 3 (Close-up detail):** Optional high-detail macro shot showing spot textures, margins, or pustules.
   * Real-time quality feedback will warn you if photos are blurry or dark, with actionable tips to steady the camera or move into better light without blocking your submission.
   * Tap **"Next: Location & Growth Stage →"**.
4. **Step 4: Location, Growth Stage & Environmental Context**
   * Select the crop growth stage: *Seedling*, *Vegetative*, *Flowering*, *Fruiting*, or *Mature*.
   * Select your general village or agricultural district. *(Exact home GPS is never stored; coordinates are rounded to ~1.1 km for privacy).*
   * **Environmental Context (Optional):** Select recent rainfall (*None*, *Light*, *Moderate*, *Heavy*), humidity level, temperature band, soil moisture/waterlogging condition, and irrigation method.
   * Add any freeform field notes (e.g., "Hailstorm occurred 2 days ago").
   * Tap **"Next: Review & Submit →"**.
5. **Step 5: Review & Submit**
   * Review your standardized observation summary.
   * Tap **"Submit Observation for Expert Review ✓"**.
   * Note your unique **Case Reference ID** (e.g., `CASE-2026-001`).

### 1.2 Offline-First Field Reporting
* **Automatic Offline Detection:** If you are working in a remote area without cellular or Wi-Fi connectivity, the header displays **🟠 Offline Mode**.
* **Local Queue Preservation:** When you tap submit, your observation and photos are safely stored in your browser's persistent IndexedDB storage (`AgriOfflineDB`). You receive a local tracking ID (`OFFLINE-...`).
* **Seamless Background Sync:** As soon as your device reconnects to a data network, the system automatically synchronizes your queued observations with the server, receives a standardized Case ID, and updates your tracking status.
* **Manual Sync:** Tap the **🔄 Sync Queue** button in the header anytime you wish to manually trigger synchronization.

### 1.3 Case Tracking & Resubmission Workflow
* Tap the **🔍 Track Case / Resubmit** tab in the main navigation.
* Enter your Case Reference ID (e.g., `CASE-2026-001`) and tap **Search Case ➔**.
* **Visual Status Stepper:**
  1. *Submitted:* Received and queued for triage.
  2. *Under Review / Action Needed:* Case is being reviewed by agronomists. If an expert requests clarification, an **Action Needed (⚠️)** badge appears with the expert's specific question.
  3. *Expert Validated:* Diagnosis is confirmed and actionable treatments are displayed.
* **Resubmitting Requested Information:**
  * When an expert asks for follow-up details (e.g., "Are whiteflies visible?"), a resubmission box appears on the tracking screen.
  * Type your answer in the response field.
  * Optionally attach an additional clarifying photograph.
  * Tap **Submit Clarification & Update Case ➔**. The case status instantly returns to **Under Review**.

---

## 2. Role 2: Agricultural Extension Officer

The Extension Officer Dashboard enables rapid triage across district smallholders, monitoring operational throughput, and identifying emergency outbreaks.

### Dashboard Operations
1. **Monitor Operational KPIs:**
   * **Total Observations:** Cumulative standardized submissions.
   * **Pending Triage:** Submissions currently awaiting expert review.
   * **High Priority:** Urgent cases escalated due to severe symptoms, flowering/fruiting vulnerability, or low ML confidence.
   * **Average $T_{review}$:** Mean hours from first farmer symptom observation to authoritative expert validation.
2. **Filter & Triage Cases:**
   * Filter by status (`Submitted`, `Under Review`, `More Information Required`, `Expert Validated`).
   * Filter by priority (`High`, `Medium`, `Low`).
   * Check **"Low Confidence (<60%) Only"** to inspect cases where the vision model or hybrid heuristics flagged diagnostic ambiguity.
3. **Inspect Evidence:**
   * Click **Inspect** on any case row to view whole-plant context, leaf close-ups, environmental context, and image quality metrics.

---

## 3. Role 3: Agricultural Expert & Phytopathologist

The Expert Station provides the authoritative workstation where certified plant pathologists validate observations, synthesize environmental evidence, override automated suggestions, and prescribe treatments.

### Validation Workflow
1. **Select a Case from the Queue:**
   * Click any case in the left sidebar. High-priority and pending cases are prominently highlighted.
2. **Review Unified 3-Column Evidence:**
   * **Column 1 (Field Evidence):** Crop, growth stage, reported symptoms, reported severity, and farmer notes.
   * **Column 2 (Environmental Context):** Recent rainfall, humidity level, temperature band, soil moisture/waterlogging, and irrigation type.
   * **Column 3 (Hybrid ML Decision Support):** MobileNetV3 predicted category, visual confidence score, and alternative diagnostic candidates. *(Clearly disclosed as non-authoritative).*
   * **Visual Evidence:** High-resolution photographs with automated blur and exposure quality ratings.
3. **Apply Authoritative Expert Action:**
   * Choose the **Validation Decision**:
     * **Confirm Observation / Diagnosis:** You agree with the preliminary AI category.
     * **Reject / Override AI Suggestion:** You identify a different disorder (e.g., overriding a fungal blight hypothesis with nitrogen deficiency).
     * **Request More Information:** You need the farmer to provide clarification or check for specific vector pests.
     * **Mark as Uncertain:** Inconclusive symptoms requiring lab sample testing.
   * Set **Urgency Level:** *Routine*, *Prompt*, or *Urgent*.
   * Enter your **Authoritative Expert Diagnosis** and **Agronomic Recommendations**.
   * Click **"Save Authoritative Expert Validation ✓"**.
   * The system immediately updates the authoritative case record, logs the review timestamp, and calculates the final $T_{review}$ metric.
