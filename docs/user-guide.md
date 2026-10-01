# Agricultural Disease Observation & Escalation App — User Guide

**Project:** Agricultural Disease Observation & Expert Escalation System  
**Stage:** Phase 3 Complete (100% End-to-End System)  
**Supported Languages:** English, Tamil (தமிழ்)  
**Accessibility:** Touch-optimized UI, Web Speech TTS & Dictation, Offline PWA  

---

## 1. Role 1: Smallholder Farmer

The Farmer module provides an intuitive, high-contrast, touch-optimized interface designed for quick, accessible field reporting with minimal typing, complete offline capability, voice assistance, and two-way inquiry tracking.

### 1.1 Step-by-Step Reporting Workflow
1. **Step 1: Select Your Crop**
   * Tap the large visual card matching your crop (*Tomato*, *Maize*, *Rice*, *Potato*, *Wheat*, *Cassava*, *Soybean*).
   * Tap **"Next Step →"**.
2. **Step 2: Describe Symptoms & Severity**
   * Tap observed symptoms (e.g. *Leaf Spots*, *Yellowing*, *Wilting*, *Powdery Coating*, *Rust Pustules*, *Bacterial Ooze*).
   * Select symptom severity: **Low**, **Medium**, **High**, or **Severe**.
   * Pick the date when symptoms were first noticed in the field.
   * Tap **"Next Step →"**.
3. **Step 3: Environmental Context & Field Notes**
   * Select the crop growth stage: *Seedling*, *Vegetative*, *Flowering*, *Fruiting*, or *Mature*.
   * Select your general village or agricultural district. *(Exact home GPS is never stored; coordinates are rounded to ~1.1 km for privacy).*
   * **Environmental Context (Optional):** Select recent rainfall (*None*, *Light*, *Moderate*, *Heavy*), humidity level, temperature band, soil moisture/waterlogging condition, and irrigation method.
   * Add any freeform field notes (e.g., "Hailstorm occurred 2 days ago"). You can also tap **🎤 Voice Dictation** to speak notes directly.
   * Tap **"Next Step →"**.
4. **Step 4: Capture Standardized Photographs**
   * Follow the 3 visual guidance cards:
     * **Photo 1 (Whole plant):** Stand back 1–2 meters to show overall canopy architecture and soil line.
     * **Photo 2 (Affected area):** Focus 30–50 cm away on the diseased branch or leaf cluster.
     * **Photo 3 (Close-up detail):** Optional high-detail macro shot showing spot textures, margins, or pustules.
   * Real-time quality feedback will warn you if photos are blurry or dark, with actionable tips to steady the camera or move into better light without blocking your submission.
   * Tap **"Next Step →"**.
5. **Step 5: Review & Submit**
   * Review your standardized observation summary.
   * Tap **"Submit Observation for Expert Review ✓"**.
   * Note your unique **Case Reference ID** (e.g., `CASE-2026-001`).

### 1.2 Multilingual Switching (English & Tamil)
* In the top-right header, select your language from the **🌐 Lang:** dropdown:
  * **English (English)**
  * **Tamil (தமிழ்)**
* All wizard steps, symptom cards, crop names, environmental terms, status tags, and buttons immediately translate into your chosen language.
* **Form Preservation Guarantee:** Any notes or selections you have already entered are **strictly preserved** and will not be cleared when you switch languages.

### 1.3 Voice & Audio Assistance (TTS & Dictation)
* **Read Aloud (🔊):** Tap the **"Read Aloud"** button in the header at any time. The system will read the current step instructions and field labels aloud in Tamil (`ta-IN`) or English (`en-IN`).
* **Voice Dictation (🎤):** In Step 3 (or the Case Resubmission box), tap the **"🎤 Voice Dictation"** button next to the notes field. Speak your observations in Tamil or English; your spoken words will be transcribed directly into the text field.
* **Stop Audio (⏹):** Tap the **"Stop"** button in the header anytime to silence speech or halt listening.
* **Fallback Guarantee:** If your browser does not support Web Speech or microphone access is denied, a non-intrusive status pill notifies you while regular keyboard and touch typing remain 100% active.

### 1.4 Offline-First Field Reporting
* **Automatic Offline Detection:** If you are working in a remote field without cellular or Wi-Fi connectivity, the header displays **🟠 Offline Mode Active**.
* **Local Queue Preservation:** When you tap submit, your observation and photos are safely stored in your browser's persistent IndexedDB storage (`AgriOfflineDB`). You receive a local tracking ID (`OFFLINE-...`).
* **Seamless Background Sync:** As soon as your device reconnects to a data network, the system automatically synchronizes your queued observations with the server, receives a standardized Case ID, and updates your tracking status.
* **Manual Sync:** Tap the **🔄 Sync** button in the header anytime you wish to manually trigger synchronization.

### 1.5 Case Tracking & Resubmission Workflow
* Tap the **🔍 Track Case / Resubmit** tab in the main navigation.
* Enter your Case Reference ID (e.g., `CASE-2026-001`) and tap **Check Status**.
* **Visual Status Stepper:**
  1. *Submitted:* Received and queued for triage.
  2. *Under Review / Action Needed:* Case is being reviewed by agronomists. If an expert requests clarification, an **Action Needed (⚠️)** badge appears with the expert's specific question.
  3. *Expert Validated:* Diagnosis is confirmed and actionable treatments are displayed.
* **Resubmitting Requested Information:**
  * When an expert asks for follow-up details (e.g., "Please cut the lower stem and check for bacterial streaming"), a resubmission box appears on the tracking screen.
  * Type your answer (or use voice dictation) in the response field.
  * Optionally attach an additional clarifying photograph.
  * Tap **Submit Follow-up Information ➔**. The case status instantly returns to **Under Review**.

---

## 2. Role 2: Agricultural Extension Officer

The Extension Officer Dashboard enables rapid triage across district smallholders, monitoring operational throughput, and identifying emergency outbreaks.

### 2.1 Dashboard Operations
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

## 3. Role 3: Regional Outbreak Surveillance & Latency Analytics

Extension officers and agricultural directors can tap the **🗺️ Regional Analytics** tab in the main navigation to access district-wide epidemiological tracking:

### 3.1 Regional Outbreak Risk Matrix
* View aggregated cluster patterns broken down by agricultural region/sector.
* **High Priority Counts & Moisture Risk:** Identifies microclimate anomalies (e.g., waterlogged soils, continuous rain) driving fungal or bacterial surges.
* **Outbreak Watch Levels:**
  * 🟢 **Normal Observation:** Baseline surveillance.
  * 🔵 **Moderate Attention:** Isolated single severe case.
  * 🟠 **Elevated Watch:** $\ge 2$ high-priority cases or elevated moisture risk.
  * 🔴 **Outbreak Alert:** $\ge 4$ high-priority cases of the same pathogen family.
* **Active Alert Banners:** Displays localized warning cards with immediate recommended field extension interventions.

### 3.2 Granular $T_{review}$ Operational Latency
* **Mean & Median $T_{review}$:** Measures hours elapsed from symptom onset in the field to expert validation.
* **Submission-to-Review Turnaround:** Platform operational latency.
* **Breakdowns:** Detailed tables analyzing response latency by priority tier (`High`, `Medium`, `Low`) and by crop type.

### 3.3 AI Performance Monitoring & Calibration
* **Live Confidence Distribution:** Histogram bars showing distribution across confidence buckets (`<50%`, `50-59%`, `60-69%`, etc.).
* **Escalation Rate:** Percentage of cases triggering the $<60\%$ safety boundary.
* **Expert Agreement vs Override Rates:** Measures alignment between preliminary AI proposals and authoritative expert decisions.
* **MobileNetV3 Held-Out Benchmark Metrics:** Displays transfer-learning accuracy, macro F1, and weighted F1 on the unaugmented test split.

---

## 4. Role 4: Agricultural Expert & Phytopathologist

The Expert Station provides the authoritative workstation where certified plant pathologists validate observations, synthesize environmental evidence, override automated suggestions, and prescribe treatments.

### 4.1 Validation Workflow
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
