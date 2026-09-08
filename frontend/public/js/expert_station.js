/**
 * Expert Validation Workstation Module.
 * Authoritative diagnostic validation, AI proposal override,
 * and follow-up inquiry handling.
 */

const ExpertStation = {
  cases: [],
  selectedCase: null,

  async init() {
    await this.fetchPendingCases();
    this.bindEvents();
  },

  async fetchPendingCases() {
    try {
      const res = await fetch("/api/cases");
      const allCases = await res.json();
      // Prioritize pending reviews and high-priority cases
      this.cases = allCases;
      this.renderCaseQueue();
      if (this.cases.length > 0 && !this.selectedCase) {
        this.selectCase(this.cases[0].case_id);
      }
    } catch (err) {
      console.error("Failed to load expert queue:", err);
    }
  },

  bindEvents() {
    const queueList = document.getElementById("expert-queue-list");
    if (queueList) {
      queueList.addEventListener("click", (e) => {
        const item = e.target.closest(".queue-item");
        if (item) {
          const cid = item.dataset.caseId;
          this.selectCase(cid);
        }
      });
    }

    const form = document.getElementById("expert-review-form");
    if (form) {
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        this.submitValidation();
      });
    }
  },

  renderCaseQueue() {
    const queueList = document.getElementById("expert-queue-list");
    if (!queueList) return;

    queueList.innerHTML = this.cases.map(c => {
      const isSelected = this.selectedCase && this.selectedCase.case_id === c.case_id;
      const pClass = c.priority.toLowerCase();
      const statusBadge = c.status === "Expert Validated" ? "badge-validated" : "badge-review";

      return `
        <div class="queue-item ${isSelected ? 'active' : ''}" data-case-id="${c.case_id}" 
             style="padding:0.75rem 1rem; border-bottom:1px solid #e0e0e0; cursor:pointer; background:${isSelected ? '#e8f5e9' : '#fff'}; transition:background 0.2s;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong>${c.case_id}</strong>
            <span class="badge badge-${pClass}">${c.priority}</span>
          </div>
          <div style="font-size:0.85rem; color:#424242; margin-top:2px;">
            ${c.crop} - ${c.symptoms}
          </div>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px; font-size:0.8rem;">
            <span class="badge ${statusBadge}">${c.status}</span>
            <small style="color:#757575;">Conf: ${c.ai_confidence ? c.ai_confidence.toFixed(0) + '%' : '-'}</small>
          </div>
        </div>
      `;
    }).join("");
  },

  selectCase(caseId) {
    this.selectedCase = this.cases.find(c => c.case_id === caseId) || null;
    this.renderCaseQueue();
    this.renderInspectionPanel();
  },

  renderInspectionPanel() {
    const panel = document.getElementById("expert-inspection-panel");
    if (!panel || !this.selectedCase) return;

    const c = this.selectedCase;
    const isLowConf = c.ai_confidence && c.ai_confidence < 60;

    // Photos
    let photosHtml = "";
    if (c.images && c.images.length > 0) {
      photosHtml = `<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:0.75rem; margin-top:0.5rem;">` +
        c.images.map(img => {
          const warnings = Array.isArray(img.quality_warnings)
            ? img.quality_warnings
            : (typeof img.quality_warnings === "string" && img.quality_warnings.trim().startsWith("["))
              ? (function() { try { return JSON.parse(img.quality_warnings); } catch(e) { return [img.quality_warnings]; } })()
              : (img.quality_warnings ? [img.quality_warnings] : []);
          const wHtml = warnings.length > 0 ? `<div style="color:#c62828; font-size:0.75rem; margin-top:2px;">⚠ ${warnings.join(", ")}</div>` : "";
          return `
            <div style="border:1px solid #dcded9; border-radius:6px; padding:0.4rem; background:#fafafa;">
              <img src="${img.file_path}" style="width:100%; height:130px; object-fit:cover; border-radius:4px;">
              <div style="font-size:0.75rem; margin-top:4px;">
                <strong>${img.image_type}</strong> | Score: ${img.quality_score}/100
                ${wHtml}
              </div>
            </div>
          `;
        }).join("") + "</div>";
    } else {
      photosHtml = "<p style='color:#757575; font-size:0.85rem;'>No photographs attached to this observation.</p>";
    }

    // Pre-populate form values if already reviewed
    const diagInput = document.getElementById("expert-diagnosis-input");
    const commentsInput = document.getElementById("expert-comments-input");
    const statusSelect = document.getElementById("expert-action-select");
    const urgencySelect = document.getElementById("expert-urgency-select");

    if (diagInput) diagInput.value = c.expert_validation || c.ai_prediction || "";
    if (commentsInput) commentsInput.value = c.expert_comments || "";
    if (statusSelect) {
      if (c.status === "Expert Validated") statusSelect.value = "confirmed";
      else if (c.status === "More Information Required") statusSelect.value = "more_info_needed";
      else statusSelect.value = "confirmed";
    }

    panel.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:1rem; border-bottom:1px solid #e0e0e0; padding-bottom:0.75rem;">
        <div>
          <h2 style="color:#1b5e20; font-size:1.35rem;">Reviewing Case: ${c.case_id}</h2>
          <small style="color:#616161;">Reported by: ${c.anonymous_farmer_id} | Location: ${c.location} (Approx: ${c.latitude}° N, ${c.longitude}° E)</small>
        </div>
        <div>
          <span class="badge badge-${c.priority.toLowerCase()}" style="font-size:0.9rem; padding:0.4rem 0.8rem;">
            ${c.priority} Priority
          </span>
        </div>
      </div>

      <!-- Side-by-side: Evidence vs AI Hypothesis -->
      <div style="display:grid; grid-template-columns:1.2fr 1fr; gap:1rem; margin-bottom:1.25rem;">
        <div style="background:#fdfcf9; border:1px solid #e0e0e0; border-radius:8px; padding:1rem;">
          <h4 style="color:#2e7d32; margin-bottom:0.4rem; font-size:1rem;">Field Evidence & Symptoms</h4>
          <p style="font-size:0.9rem;"><strong>Crop & Stage:</strong> ${c.crop} (${c.crop_stage})</p>
          <p style="font-size:0.9rem;"><strong>Reported Symptoms:</strong> ${c.symptoms}</p>
          <p style="font-size:0.9rem;"><strong>Severity:</strong> ${c.severity}</p>
          <p style="font-size:0.9rem;"><strong>First Noticed:</strong> ${new Date(c.first_symptom_time).toLocaleString()}</p>
          <p style="font-size:0.9rem;"><strong>Farmer Notes:</strong> ${c.farmer_notes || "None"}</p>
          <p style="font-size:0.9rem;"><strong>Environmental Stress:</strong> ${c.environmental_notes || "None"}</p>
        </div>

        <div style="background:#f4fbf4; border:1px solid #c8e6c9; border-radius:8px; padding:1rem;">
          <h4 style="color:#1b5e20; margin-bottom:0.4rem; font-size:1rem;">Experimental AI Proposal</h4>
          <p style="font-size:0.9rem;"><strong>Hypothesis:</strong> ${c.ai_prediction || "Unclassified"}</p>
          <p style="font-size:0.9rem;"><strong>Calculated Confidence:</strong> 
            <span style="font-weight:700; color:${isLowConf ? '#d32f2f' : '#2e7d32'};">
              ${c.ai_confidence ? c.ai_confidence.toFixed(1) + '%' : 'Pending'}
            </span>
            ${isLowConf ? '<span style="color:#d32f2f; font-size:0.8rem;"> (Low Confidence Escalation)</span>' : ''}
          </p>
          <p style="font-size:0.9rem;"><strong>Alternative Considered:</strong> ${c.ai_alternative || "None"}</p>
          <div class="alert alert-info" style="margin-top:0.6rem; padding:0.4rem 0.6rem; font-size:0.8rem;">
            <em>Experimental assistance feature only. Expert validation is authoritative.</em>
          </div>
        </div>
      </div>

      <!-- Attached Photos with quality feedback -->
      <h4 style="color:#1b5e20; margin-bottom:0.3rem;">Visual Evidence</h4>
      ${photosHtml}
    `;
  },

  async submitValidation() {
    if (!this.selectedCase) return;

    const actionSelect = document.getElementById("expert-action-select");
    const diagInput = document.getElementById("expert-diagnosis-input");
    const commentsInput = document.getElementById("expert-comments-input");
    const urgencySelect = document.getElementById("expert-urgency-select");
    const statusBox = document.getElementById("expert-feedback-box");

    const payload = {
      expert_category: diagInput.value.trim() || "Expert Reviewed",
      validation_status: actionSelect.value,
      comments: commentsInput.value.trim(),
      urgency: urgencySelect.value
    };

    try {
      const res = await fetch(`/api/cases/${this.selectedCase.case_id}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const updatedCase = await res.json();

      statusBox.style.display = "block";
      statusBox.innerHTML = `
        <div class="alert alert-success">
          ✓ Expert validation recorded for <strong>${updatedCase.case_id}</strong>! 
          Status updated to: <strong>${updatedCase.status}</strong>.
        </div>
      `;

      // Update locally
      const idx = this.cases.findIndex(c => c.case_id === updatedCase.case_id);
      if (idx !== -1) this.cases[idx] = updatedCase;
      this.selectedCase = updatedCase;
      this.renderCaseQueue();
      this.renderInspectionPanel();

      // Refresh officer metrics in background
      if (typeof OfficerDashboard !== "undefined") {
        OfficerDashboard.fetchMetrics();
        OfficerDashboard.fetchCases();
      }
    } catch (err) {
      statusBox.style.display = "block";
      statusBox.innerHTML = `<div class="alert alert-danger">Failed to save review: ${err.message}</div>`;
    }
  }
};
