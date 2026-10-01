/**
 * Farmer Case Tracking & Resubmission Module (Phase 2.5).
 * Enables farmers to check observation status, view expert questions,
 * upload clarifying photos, and submit follow-up responses.
 */

const FarmerTrack = {
  currentCase: null,

  init() {
    this.bindEvents();
    // Check if case ID is in URL hash e.g. #track/CASE-2026-001
    this.checkUrlCaseId();
  },

  bindEvents() {
    const searchBtn = document.getElementById("btn-track-search");
    const input = document.getElementById("input-track-case-id");

    if (searchBtn && input) {
      searchBtn.addEventListener("click", () => {
        const caseId = input.value.trim();
        if (caseId) {
          this.trackCase(caseId);
        }
      });

      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          const caseId = input.value.trim();
          if (caseId) {
            this.trackCase(caseId);
          }
        }
      });
    }
  },

  checkUrlCaseId() {
    const hash = window.location.hash;
    if (hash.startsWith("#track/")) {
      const caseId = hash.replace("#track/", "").trim();
      const input = document.getElementById("input-track-case-id");
      if (input) input.value = caseId;
      this.trackCase(caseId);
    }
  },

  async trackCase(caseId) {
    const container = document.getElementById("track-result-container");
    if (!container) return;

    container.innerHTML = `
      <div style="padding:2rem; text-align:center; color:var(--text-muted);">
        <p>Loading observation status for <strong>${caseId}</strong>...</p>
      </div>
    `;
    container.style.display = "block";

    try {
      const res = await fetch(`/api/cases/${encodeURIComponent(caseId)}`);
      if (res.status === 404) {
        container.innerHTML = `
          <div class="alert alert-warning" style="margin-top:1rem;">
            <strong>Case Not Found:</strong> Could not find observation reference <code>${caseId}</code>. Please double-check the ID printed on your submission receipt.
          </div>
        `;
        return;
      }
      if (!res.ok) {
        throw new Error(`Server returned HTTP ${res.status}`);
      }

      const caseData = await res.json();
      this.currentCase = caseData;
      this.renderCaseDetails(caseData);
    } catch (err) {
      container.innerHTML = `
        <div class="alert alert-danger" style="margin-top:1rem;">
          <strong>Error loading case:</strong> ${err.message}. Please check your connection and try again.
        </div>
      `;
    }
  },

  renderCaseDetails(c) {
    const container = document.getElementById("track-result-container");
    if (!container) return;

    // Status mapping & progress steps
    const statusSteps = [
      { key: "Submitted", label: "1. Observation Submitted" },
      { key: "Under Review", label: "2. Under Expert Review" },
      { key: "Expert Validated", label: "3. Expert Validated" }
    ];

    const isMoreInfo = c.status === "More Information Required";
    const isValidated = c.status === "Expert Validated";
    const isUnderReview = c.status === "Under Review";

    let stepIndex = 0;
    if (isUnderReview || isMoreInfo) stepIndex = 1;
    if (isValidated) stepIndex = 2;

    let stepperHtml = `
      <div class="track-stepper" style="display:flex; justify-content:space-between; margin-bottom:1.5rem; position:relative;">
        <div class="track-step ${stepIndex >= 0 ? 'active' : ''}">
          <div class="step-circle">✓</div>
          <div class="step-label">Submitted</div>
        </div>
        <div class="track-step ${stepIndex >= 1 ? 'active' : ''} ${isMoreInfo ? 'needs-info' : ''}">
          <div class="step-circle">${isMoreInfo ? '⚠️' : (stepIndex >= 1 ? '✓' : '2')}</div>
          <div class="step-label">${isMoreInfo ? 'Action Needed' : 'Under Review'}</div>
        </div>
        <div class="track-step ${stepIndex >= 2 ? 'active' : ''}">
          <div class="step-circle">${stepIndex >= 2 ? '✓' : '3'}</div>
          <div class="step-label">Expert Validated</div>
        </div>
      </div>
    `;

    // Action banner for "More Information Required"
    let actionBannerHtml = "";
    if (isMoreInfo) {
      actionBannerHtml = `
        <div class="alert alert-warning" style="margin-bottom:1.5rem; border-left:5px solid #f57c00;">
          <div style="font-size:1.1rem; font-weight:700; margin-bottom:0.4rem;">
            ⚠️ Expert Extension Officer Requested Additional Information
          </div>
          <p style="margin-bottom:0.5rem;">
            <strong>Expert Note:</strong> <em>"${c.expert_comments || "Please provide clearer photos or describe when leaf spots first appeared."}"</em>
          </p>
          <p style="font-size:0.9rem; color:#616161;">
            To help our agronomists complete their diagnosis, please provide clarification or a new photo below:
          </p>
          <div style="margin-top:1rem; background:#fff; padding:1rem; border-radius:8px; border:1px solid #ffe082;">
            <h4 style="margin-bottom:0.5rem; color:#e65100;">Provide Clarification / Resubmit:</h4>
            <div class="form-group">
              <label class="form-label">Your Response / Clarifying Notes:</label>
              <textarea id="resubmit-notes" class="form-control" rows="3" placeholder="Describe symptoms, when changes occurred, or answer the expert's question..."></textarea>
            </div>
            <div class="form-group" style="margin-top:0.75rem;">
              <label class="form-label">Upload Additional Photo (Optional):</label>
              <input type="file" id="resubmit-image" accept="image/*" class="form-control">
            </div>
            <div id="resubmit-feedback" style="display:none; margin:0.75rem 0;"></div>
            <button id="btn-submit-resubmit" class="btn btn-primary" onclick="FarmerTrack.submitResubmission('${c.case_id}')">
              Submit Clarification & Update Case ➔
            </button>
          </div>
        </div>
      `;
    }

    // Expert Validated Banner
    let validatedBannerHtml = "";
    if (isValidated) {
      validatedBannerHtml = `
        <div class="alert alert-success" style="margin-bottom:1.5rem; border-left:5px solid #2e7d32;">
          <div style="font-size:1.15rem; font-weight:700; margin-bottom:0.3rem;">
            ✓ Expert Diagnosis Completed
          </div>
          <p><strong>Authoritative Diagnosis:</strong> <span class="badge badge-success" style="font-size:1rem;">${c.expert_validation}</span></p>
          <p style="margin-top:0.5rem;"><strong>Expert Agronomic Advice:</strong></p>
          <div style="background:#ffffff; padding:0.75rem 1rem; border-radius:6px; margin-top:0.3rem; border:1px solid #c8e6c9;">
            ${c.expert_comments ? c.expert_comments.replace(/\n/g, '<br>') : "No specific comments provided."}
          </div>
          <p style="margin-top:0.5rem; font-size:0.85rem; color:#616161;">
            Validated on: ${new Date(c.expert_review_time || c.updated_at).toLocaleString()}
          </p>
        </div>
      `;
    }

    // Images gallery
    let imagesHtml = "<p style='color:#757575;'>No images attached.</p>";
    if (c.images && c.images.length > 0) {
      imagesHtml = `
        <div style="display:flex; flex-wrap:wrap; gap:1rem; margin-top:0.5rem;">
          ${c.images.map(img => `
            <div style="width:140px; border:1px solid #e0e0e0; border-radius:6px; overflow:hidden; background:#fafafa;">
              <img src="${img.file_path}" alt="${img.image_type}" style="width:100%; height:110px; object-fit:cover;">
              <div style="padding:0.35rem 0.5rem; font-size:0.78rem;">
                <strong>${img.image_type.replace('_', ' ')}</strong><br>
                <span style="color:#2e7d32;">Quality: ${img.quality_score}/100</span>
              </div>
            </div>
          `).join('')}
        </div>
      `;
    }

    container.innerHTML = `
      <div class="card" style="margin-top:1.5rem;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:0.5rem; margin-bottom:1rem;">
          <div>
            <h2 style="color:var(--primary-dark); margin:0;">${c.case_id}</h2>
            <p style="color:var(--text-muted); font-size:0.9rem;">
              Submitted on ${new Date(c.submission_time).toLocaleString()} | Farmer ID: <code>${c.anonymous_farmer_id}</code>
            </p>
          </div>
          <div>
            <span class="badge badge-${c.priority.toLowerCase()}" style="font-size:0.9rem; padding:0.4rem 0.8rem;">
              ${c.priority} Priority
            </span>
            <span class="status-pill ${isValidated ? 'status-pill-online' : 'status-pill-offline'}" style="margin-left:0.5rem;">
              ${c.status}
            </span>
          </div>
        </div>

        ${stepperHtml}
        ${actionBannerHtml}
        ${validatedBannerHtml}

        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:1.25rem; margin-top:1.25rem;">
          <!-- Case Metadata -->
          <div style="background:#f9fbf9; padding:1rem; border-radius:8px; border:1px solid #e8f5e9;">
            <h4 style="color:var(--primary-dark); margin-bottom:0.75rem;">📋 Crop & Observation Details</h4>
            <p><strong>Crop:</strong> ${c.crop} ${c.variety ? `(${c.variety})` : ''}</p>
            <p><strong>Growth Stage:</strong> ${c.crop_stage}</p>
            <p><strong>Observed Symptoms:</strong> ${c.symptoms}</p>
            <p><strong>Reported Severity:</strong> ${c.severity}</p>
            <p><strong>First Noticed:</strong> ${new Date(c.first_symptom_time).toLocaleDateString()}</p>
            <p><strong>Location:</strong> ${c.location} (${c.latitude ? `${c.latitude}°, ${c.longitude}°` : 'Privacy Preserved'})</p>
          </div>

          <!-- Environmental Context -->
          <div style="background:#f9fbf9; padding:1rem; border-radius:8px; border:1px solid #e8f5e9;">
            <h4 style="color:var(--primary-dark); margin-bottom:0.75rem;">🌦️ Environmental Context</h4>
            <p><strong>Recent Rainfall:</strong> ${c.rainfall_recent || 'Unknown'}</p>
            <p><strong>Humidity Level:</strong> ${c.humidity_level || 'Unknown'}</p>
            <p><strong>Temperature Band:</strong> ${c.temperature_band || 'Unknown'}</p>
            <p><strong>Soil Moisture:</strong> ${c.soil_moisture_observation || 'Unknown'}</p>
            <p><strong>Field Condition:</strong> ${c.field_condition || 'Unknown'}</p>
            <p><strong>Irrigation Status:</strong> ${c.irrigation_status || 'Unknown'}</p>
            ${c.environmental_notes ? `<p><strong>Weather Notes:</strong> ${c.environmental_notes}</p>` : ''}
          </div>
        </div>

        <!-- Photos -->
        <div style="margin-top:1.25rem;">
          <h4 style="color:var(--primary-dark); margin-bottom:0.5rem;">📷 Attached Photographs</h4>
          ${imagesHtml}
        </div>

        <!-- Preliminary AI Hypothesis (Honest Disclosure) -->
        <div style="margin-top:1.25rem; background:#fffde7; padding:0.85rem 1rem; border-radius:8px; border:1px solid #fff59d;">
          <h5 style="color:#f57f17; margin-bottom:0.3rem;">🤖 Preliminary AI-Assisted Hypothesis</h5>
          <p style="font-size:0.92rem; margin:0;">
            Candidate Category: <strong>${c.ai_prediction || 'Pending classification'}</strong> 
            (Confidence: <strong>${c.ai_confidence ? c.ai_confidence.toFixed(1) + '%' : 'N/A'}</strong>)
          </p>
          <p style="font-size:0.8rem; color:#616161; margin-top:0.25rem;">
            <em>Notice: AI hypothesis is used solely for initial triage prioritization. Only human agronomist review is authoritative.</em>
          </p>
        </div>
      </div>
    `;
  },

  async submitResubmission(caseId) {
    const notesInput = document.getElementById("resubmit-notes");
    const imageInput = document.getElementById("resubmit-image");
    const feedbackBox = document.getElementById("resubmit-feedback");
    const submitBtn = document.getElementById("btn-submit-resubmit");

    if (!notesInput || !notesInput.value.trim()) {
      alert("Please enter clarifying notes before submitting.");
      return;
    }

    submitBtn.disabled = true;
    submitBtn.innerText = "Submitting clarification...";
    feedbackBox.style.display = "block";
    feedbackBox.innerHTML = "<small>Sending updated information to expert workstation...</small>";

    try {
      const formData = new FormData();
      formData.append("additional_notes", notesInput.value.trim());
      if (imageInput && imageInput.files && imageInput.files[0]) {
        formData.append("new_image", imageInput.files[0]);
      }

      const res = await fetch(`/api/cases/${encodeURIComponent(caseId)}/resubmit`, {
        method: "POST",
        body: formData
      });

      if (!res.ok) {
        throw new Error(`Server returned HTTP ${res.status}`);
      }

      const updatedCase = await res.json();
      feedbackBox.className = "alert alert-success";
      feedbackBox.innerHTML = "✓ Clarification submitted successfully! Your case is now under expert re-review.";

      setTimeout(() => {
        this.trackCase(caseId);
      }, 1500);
    } catch (err) {
      feedbackBox.className = "alert alert-danger";
      feedbackBox.innerHTML = `<strong>Error submitting clarification:</strong> ${err.message}`;
      submitBtn.disabled = false;
      submitBtn.innerText = "Try Submitting Again";
    }
  }
};

if (typeof window !== "undefined") {
  window.addEventListener("DOMContentLoaded", () => {
    FarmerTrack.init();
  });
}
