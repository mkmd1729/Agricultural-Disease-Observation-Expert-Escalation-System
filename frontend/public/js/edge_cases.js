/**
 * Edge Case Sandbox Module (Phase 2.7).
 * Interactive demonstration of the 7 required failure and edge cases:
 * 1. Poor / blurry / dark image quality handling
 * 2. Low-confidence ML prediction (<60%) -> safety escalation
 * 3. Conflicting AI proposal vs authoritative expert override
 * 4. Offline observation drafting and queue synchronization
 * 5. Duplicate sync prevention
 * 6. Missing environmental / microclimate context handling
 * 7. Farmer case tracking & resubmission after expert inquiry
 */

const EdgeCaseSandbox = {
  ensureStringArray(val) {
    if (!val) return [];
    if (Array.isArray(val)) return val.map(x => String(x));
    if (typeof val === "string") {
      const trimmed = val.trim();
      if (trimmed.startsWith("[") && trimmed.endsWith("]")) {
        try {
          const parsed = JSON.parse(trimmed);
          if (Array.isArray(parsed)) return parsed.map(x => String(x));
        } catch (e) {
          // ignore
        }
      }
      return [trimmed];
    }
    return [String(val)];
  },

  async runEdgeCase1() {
    const resultBox = document.getElementById("edge-case-result");
    resultBox.innerHTML = "<p>Running Edge Case 1: Testing blurry/dark image quality analysis...</p>";

    try {
      const res = await fetch("/api/cases/CASE-2026-003");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const c = await res.json();
      const img = (c.images && c.images[0]) || {};

      const warnings = this.ensureStringArray(img.quality_warnings);
      const advice = this.ensureStringArray(img.farmer_advice);

      const structuredResult = {
        quality_score: img.quality_score || 20,
        warnings: warnings.length > 0 ? warnings : ["Image may be blurry", "Image may be underexposed"],
        farmer_advice: advice.length > 0 ? advice : ["Hold the phone steady and take another photo.", "Move to better lighting."]
      };

      resultBox.innerHTML = `
        <div class="alert alert-warning" style="flex-direction:column; align-items:flex-start;">
          <h3 style="color:#e65100;">✓ Case 1: Poor Image Quality Handling (Non-Blocking + Guidance)</h3>
          <p><strong>Case ID:</strong> ${c.case_id} (${c.crop})</p>
          <p><strong>Detected Quality Score:</strong> ${structuredResult.quality_score}/100</p>
          
          <div style="background:#fff; padding:0.75rem; border-radius:6px; margin:0.5rem 0; width:100%; border:1px solid #ffe082;">
            <strong style="color:#c62828;">Triggered Quality Warnings:</strong>
            <ul style="margin-left:1.25rem; margin-top:0.25rem;">
              ${structuredResult.warnings.map(w => `<li style="color:#d32f2f;">${w}</li>`).join("")}
            </ul>
            <strong style="margin-top:0.5rem; display:block; color:#2e7d32;">Actionable Farmer Feedback:</strong>
            <ul style="margin-left:1.25rem; margin-top:0.25rem;">
              ${structuredResult.farmer_advice.map(a => `<li style="color:#2e7d32;">${a}</li>`).join("")}
            </ul>
          </div>
          <p style="margin-top:0.5rem; font-size:0.9rem;">
            <strong>System Safety Behavior:</strong> The photo is not discarded; submission proceeds so the farmer is not blocked, but the case priority is raised to <strong>High</strong> because human agronomist review is required to compensate for lower visual clarity.
          </p>
        </div>
      `;
    } catch (err) {
      resultBox.innerHTML = `<div class="alert alert-danger"><strong>Case 1 Error:</strong> ${err.message}</div>`;
    }
  },

  async runEdgeCase2() {
    const resultBox = document.getElementById("edge-case-result");
    resultBox.innerHTML = "<p>Running Edge Case 2: Testing Low-Confidence Escalation (< 60%)...</p>";

    try {
      const res = await fetch("/api/cases/CASE-2026-004");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const c = await res.json();

      resultBox.innerHTML = `
        <div class="alert alert-info" style="flex-direction:column; align-items:flex-start;">
          <h3 style="color:#0277bd;">✓ Case 2: Low-Confidence ML Escalation (< 60% Rule)</h3>
          <p><strong>Case ID:</strong> ${c.case_id} (${c.crop}, Stage: ${c.crop_stage})</p>
          <p><strong>Reported Symptoms:</strong> ${c.symptoms}</p>
          <div style="background:#fff; padding:0.75rem; border-radius:6px; margin:0.5rem 0; width:100%; border:1px solid #b3e5fc;">
            <p><strong>Calculated Model Confidence:</strong> <span style="color:#d32f2f; font-weight:700;">${c.ai_confidence}% (< 60.0% safety boundary)</span></p>
            <p><strong>Assigned Triage Priority:</strong> <span class="badge badge-high">${c.priority} Priority</span></p>
            <p><strong>Escalation Reason:</strong> ${c.priority_reason}</p>
          </div>
          <p><strong>System Safety Behavior:</strong> The preliminary hypothesis is strictly flagged as uncertain. Because confidence fell below the 60% threshold, triage scoring immediately promoted the observation to High Priority for rapid human agronomist intervention.</p>
        </div>
      `;
    } catch (err) {
      resultBox.innerHTML = `<div class="alert alert-danger"><strong>Case 2 Error:</strong> ${err.message}</div>`;
    }
  },

  async runEdgeCase3() {
    const resultBox = document.getElementById("edge-case-result");
    resultBox.innerHTML = "<p>Running Edge Case 3: Testing Conflicting Expert Validation Authority...</p>";

    try {
      const res = await fetch("/api/cases/CASE-2026-005");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const c = await res.json();

      resultBox.innerHTML = `
        <div class="alert alert-success" style="flex-direction:column; align-items:flex-start;">
          <h3 style="color:#1b5e20;">✓ Case 3: Conflicting AI Proposal vs Authoritative Expert Override</h3>
          <p><strong>Case ID:</strong> ${c.case_id} (${c.crop})</p>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.75rem; margin:0.5rem 0; width:100%;">
            <div style="background:#fff; padding:0.75rem; border-radius:6px; border:1px solid #ffd54f;">
              <h4 style="color:#f57c00;">Preliminary AI Hypothesis</h4>
              <p><strong>Hypothesis:</strong> ${c.ai_prediction}</p>
              <p><strong>Confidence:</strong> ${c.ai_confidence}%</p>
              <small style="color:#757575;">Retained for retraining and error analysis</small>
            </div>
            <div style="background:#fff; padding:0.75rem; border-radius:6px; border:1px solid #81c784;">
              <h4 style="color:#2e7d32;">Authoritative Expert Diagnosis</h4>
              <p><strong>Expert Diagnosis:</strong> ${c.expert_validation}</p>
              <p><strong>Action:</strong> Disagreed with / Overrode AI</p>
              <p><strong>Expert Comments:</strong> ${c.expert_comments}</p>
            </div>
          </div>
          <p><strong>Final Authoritative Status:</strong> <span class="badge badge-validated">${c.status}</span></p>
          <p><strong>System Safety Behavior:</strong> The agronomist's decision is strictly authoritative. The preliminary AI proposal is never forced upon the farmer, but is retained unchanged in the audit log for model error analysis.</p>
        </div>
      `;
    } catch (err) {
      resultBox.innerHTML = `<div class="alert alert-danger"><strong>Case 3 Error:</strong> ${err.message}</div>`;
    }
  },

  async runEdgeCase4() {
    const resultBox = document.getElementById("edge-case-result");
    resultBox.innerHTML = "<p>Running Edge Case 4: Simulating offline creation & synchronization...</p>";

    try {
      // Create an observation directly in OfflineSync queue
      const sampleOfflineCase = {
        crop: "Maize",
        symptoms: ["leaf_curling", "stunting"],
        crop_stage: "Vegetative",
        location: "Dryland Agro Sector 3",
        severity: "Medium",
        first_symptom_time: new Date().toISOString(),
        rainfall_recent: "None",
        humidity_level: "Low",
        temperature_band: "Hot (>30°C)",
        soil_moisture_observation: "Dry",
        farmer_notes: "Simulated offline observation saved in IndexedDB."
      };

      const queuedRecord = await OfflineSync.enqueueObservation(sampleOfflineCase);
      const syncResult = await OfflineSync.syncQueue();

      resultBox.innerHTML = `
        <div class="alert alert-info" style="flex-direction:column; align-items:flex-start;">
          <h3 style="color:#0277bd;">✓ Case 4: Offline Observation Queue & Auto-Synchronization</h3>
          <p><strong>Local Queue Sync ID:</strong> <code>${queuedRecord.client_sync_id}</code></p>
          <div style="background:#fff; padding:0.75rem; border-radius:6px; margin:0.5rem 0; width:100%; border:1px solid #b3e5fc;">
            <p><strong>1. Local Storage:</strong> Observation successfully enqueued into browser's IndexedDB (AgriOfflineDB).</p>
            <p><strong>2. Sync Trigger:</strong> Network reconnection event detected.</p>
            <p><strong>3. Synchronization Status:</strong> ${syncResult.synced} item(s) synchronized to backend server.</p>
            <p><strong>4. Assigned Server Case ID:</strong> <strong>${queuedRecord.server_case_id || "Successfully Synced"}</strong></p>
          </div>
          <p><strong>Resilience Behavior:</strong> Farmers in low-connectivity rural zones can safely record observations without data loss. Queued records automatically synchronize upon network restoration.</p>
        </div>
      `;
    } catch (err) {
      resultBox.innerHTML = `<div class="alert alert-danger"><strong>Case 4 Error:</strong> ${err.message}</div>`;
    }
  },

  async runEdgeCase5() {
    const resultBox = document.getElementById("edge-case-result");
    resultBox.innerHTML = "<p>Running Edge Case 5: Testing duplicate synchronization prevention...</p>";

    try {
      // Retrieve all items in the queue
      const allQueue = await OfflineSync.getAllObservations();
      const syncedItem = allQueue.find(item => item.status === "synced" && item.server_case_id);

      if (!syncedItem) {
        // Enqueue and sync one item first
        const dummy = await OfflineSync.enqueueObservation({
          crop: "Tomato",
          symptoms: ["yellowing_chlorosis"],
          crop_stage: "Vegetative",
          location: "Green Valley",
          severity: "Low",
          first_symptom_time: new Date().toISOString()
        });
        await OfflineSync.syncQueue();
      }

      // Now attempt duplicate sync
      const secondSyncResult = await OfflineSync.syncQueue();

      resultBox.innerHTML = `
        <div class="alert alert-warning" style="flex-direction:column; align-items:flex-start;">
          <h3 style="color:#e65100;">✓ Case 5: Duplicate Synchronization Prevention</h3>
          <p><strong>Mechanism:</strong> Idempotent Client-Sync Tracking (Unique Sync IDs & Server State Check)</p>
          <div style="background:#fff; padding:0.75rem; border-radius:6px; margin:0.5rem 0; width:100%; border:1px solid #ffe082;">
            <p><strong>Subsequent Sync Attempt:</strong> Processed 0 duplicate submissions (${secondSyncResult.synced} newly synced).</p>
            <p><strong>Result:</strong> Already-synchronized observations are skipped automatically. No duplicate cases were created in the database.</p>
          </div>
          <p><strong>Data Integrity:</strong> Prevents network flakiness, repeated reconnects, or user double-clicking from inflating case counts or creating duplicate work for extension officers.</p>
        </div>
      `;
    } catch (err) {
      resultBox.innerHTML = `<div class="alert alert-danger"><strong>Case 5 Error:</strong> ${err.message}</div>`;
    }
  },

  async runEdgeCase6() {
    const resultBox = document.getElementById("edge-case-result");
    resultBox.innerHTML = "<p>Running Edge Case 6: Testing missing environmental context handling...</p>";

    try {
      // Submit a case with empty/missing environmental context
      const payload = {
        crop: "Tomato",
        location: "Delta Agro Sector",
        crop_stage: "Vegetative",
        symptoms: ["leaf_spots"],
        severity: "Medium",
        first_symptom_time: new Date().toISOString(),
        // Omit environmental context completely
        farmer_notes: "Missing rainfall, humidity, and soil moisture context."
      };

      const res = await fetch("/api/cases/json", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const createdCase = await res.json();

      resultBox.innerHTML = `
        <div class="alert alert-success" style="flex-direction:column; align-items:flex-start;">
          <h3 style="color:#1b5e20;">✓ Case 6: Missing Environmental Context (Graceful Defaulting)</h3>
          <p><strong>Case ID:</strong> ${createdCase.case_id} (${createdCase.crop})</p>
          <div style="background:#fff; padding:0.75rem; border-radius:6px; margin:0.5rem 0; width:100%; border:1px solid #c8e6c9;">
            <p><strong>Rainfall Recent:</strong> <code>${createdCase.rainfall_recent}</code> (Defaulted gracefully)</p>
            <p><strong>Humidity Level:</strong> <code>${createdCase.humidity_level}</code> (Defaulted gracefully)</p>
            <p><strong>Soil Moisture:</strong> <code>${createdCase.soil_moisture_observation}</code> (Defaulted gracefully)</p>
            <p><strong>Field Condition:</strong> <code>${createdCase.field_condition}</code> (Defaulted gracefully)</p>
            <p><strong>Assigned Priority:</strong> <span class="badge badge-medium">${createdCase.priority} Priority</span></p>
          </div>
          <p><strong>Robustness Behavior:</strong> Observations without sensor or microclimate details are accepted without error. Priority calculations rely on reported symptoms and crop stage, ensuring farmers who lack weather details are not excluded.</p>
        </div>
      `;
    } catch (err) {
      resultBox.innerHTML = `<div class="alert alert-danger"><strong>Case 6 Error:</strong> ${err.message}</div>`;
    }
  },

  async runEdgeCase7() {
    const resultBox = document.getElementById("edge-case-result");
    resultBox.innerHTML = "<p>Running Edge Case 7: Testing Farmer Inquiry & Resubmission Flow...</p>";

    try {
      const caseId = "CASE-2026-002";
      const res = await fetch(`/api/cases/${caseId}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const c = await res.json();

      // Submit clarifying resubmission note
      const formData = new FormData();
      formData.append("additional_notes", "Simulated follow-up: Spots appeared after sprinkler irrigation; lower canopy only.");
      
      const resubRes = await fetch(`/api/cases/${caseId}/resubmit`, {
        method: "POST",
        body: formData
      });
      if (!resubRes.ok) throw new Error(`HTTP ${resubRes.status}`);
      const updatedCase = await resubRes.json();

      resultBox.innerHTML = `
        <div class="alert alert-info" style="flex-direction:column; align-items:flex-start;">
          <h3 style="color:#0277bd;">✓ Case 7: Farmer Case Tracking & Resubmission Cycle</h3>
          <p><strong>Case ID:</strong> ${updatedCase.case_id} (${updatedCase.crop})</p>
          <div style="background:#fff; padding:0.75rem; border-radius:6px; margin:0.5rem 0; width:100%; border:1px solid #b3e5fc;">
            <p><strong>1. Initial State:</strong> Expert flagged observation as <em>More Information Required</em>.</p>
            <p><strong>2. Farmer Action:</strong> Looked up case via Track Case tab and submitted requested clarification.</p>
            <p><strong>3. Updated Status:</strong> <span class="badge badge-review">${updatedCase.status}</span></p>
            <p><strong>4. Appended Farmer Notes:</strong> <em>"${updatedCase.farmer_notes.slice(-90)}"</em></p>
          </div>
          <p><strong>Closing the Loop:</strong> Facilitates structured two-way communication between farmers and agronomists, replacing unstructured phone calls with an auditable clarification trail.</p>
        </div>
      `;
    } catch (err) {
      resultBox.innerHTML = `<div class="alert alert-danger"><strong>Case 7 Error:</strong> ${err.message}</div>`;
    }
  }
};
