/**
 * Extension Officer Dashboard Module: Triage, Metrics, Filtering, and Case Tracking.
 */

const OfficerDashboard = {
  cases: [],
  metrics: null,

  async init() {
    await this.fetchMetrics();
    await this.fetchCases();
    this.bindFilters();
  },

  async fetchMetrics() {
    try {
      const res = await fetch("/api/metrics/summary");
      this.metrics = await res.json();
      this.renderKPICards();
      this.renderCharts();
      this.renderComparisonTable();
    } catch (err) {
      console.error("Failed to load metrics:", err);
    }
  },

  async fetchCases() {
    try {
      const status = document.getElementById("filter-status")?.value || "";
      const priority = document.getElementById("filter-priority")?.value || "";
      const crop = document.getElementById("filter-crop")?.value || "";
      const lowConfOnly = document.getElementById("filter-lowconf")?.checked || false;

      let url = `/api/cases?`;
      if (status) url += `status=${encodeURIComponent(status)}&`;
      if (priority) url += `priority=${encodeURIComponent(priority)}&`;
      if (crop) url += `crop=${encodeURIComponent(crop)}&`;
      if (lowConfOnly) url += `low_confidence_only=true&`;

      const res = await fetch(url);
      this.cases = await res.json();
      this.renderCasesTable();
    } catch (err) {
      console.error("Failed to load cases:", err);
    }
  },

  bindFilters() {
    const filters = ["filter-status", "filter-priority", "filter-crop", "filter-lowconf"];
    filters.forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener("change", () => this.fetchCases());
      }
    });

    const refreshBtn = document.getElementById("btn-refresh-dashboard");
    if (refreshBtn) {
      refreshBtn.addEventListener("click", () => {
        this.fetchMetrics();
        this.fetchCases();
      });
    }
  },

  renderKPICards() {
    if (!this.metrics) return;
    const m = this.metrics;

    document.getElementById("kpi-total").innerText = m.total_observations;
    document.getElementById("kpi-pending").innerText = m.pending_reviews;
    document.getElementById("kpi-high-priority").innerText = m.high_priority_cases;
    document.getElementById("kpi-validated").innerText = m.expert_validated_cases;
    document.getElementById("kpi-low-conf").innerText = m.low_confidence_cases;
    
    const treviewEl = document.getElementById("kpi-treview");
    if (treviewEl) {
      treviewEl.innerText = m.avg_t_review_hours ? `${m.avg_t_review_hours}h` : "Pending";
    }
  },

  renderCharts() {
    if (!this.metrics) return;
    const m = this.metrics;

    // Cases by crop breakdown bar
    const cropChartEl = document.getElementById("chart-crop-breakdown");
    if (cropChartEl) {
      let cropHtml = '<div style="display:flex; flex-direction:column; gap:0.5rem;">';
      const crops = Object.entries(m.cases_by_crop);
      const maxCount = Math.max(...crops.map(c => c[1]), 1);
      crops.forEach(([crop, count]) => {
        const pct = (count / maxCount) * 100;
        cropHtml += `
          <div>
            <div style="display:flex; justify-content:space-between; font-size:0.85rem; margin-bottom:2px;">
              <span><strong>${crop}</strong></span>
              <span>${count} cases</span>
            </div>
            <div style="background:#e0e0e0; height:12px; border-radius:6px; overflow:hidden;">
              <div style="background:#2e7d32; width:${pct}%; height:100%;"></div>
            </div>
          </div>
        `;
      });
      cropHtml += "</div>";
      cropChartEl.innerHTML = cropHtml;
    }

    // Cases by symptom breakdown bar
    const symChartEl = document.getElementById("chart-symptom-breakdown");
    if (symChartEl) {
      let symHtml = '<div style="display:flex; flex-direction:column; gap:0.5rem;">';
      const syms = Object.entries(m.cases_by_symptom_category).slice(0, 5);
      const maxCount = Math.max(...syms.map(s => s[1]), 1);
      syms.forEach(([sym, count]) => {
        const cleanName = sym.replace(/_/g, " ");
        const pct = (count / maxCount) * 100;
        symHtml += `
          <div>
            <div style="display:flex; justify-content:space-between; font-size:0.85rem; margin-bottom:2px;">
              <span><strong>${cleanName}</strong></span>
              <span>${count} cases</span>
            </div>
            <div style="background:#e0e0e0; height:12px; border-radius:6px; overflow:hidden;">
              <div style="background:#f57c00; width:${pct}%; height:100%;"></div>
            </div>
          </div>
        `;
      });
      symHtml += "</div>";
      symChartEl.innerHTML = symHtml;
    }
  },

  renderComparisonTable() {
    if (!this.metrics || !this.metrics.comparison_table) return;
    const tableBody = document.getElementById("comparison-table-body");
    if (!tableBody) return;

    tableBody.innerHTML = this.metrics.comparison_table.map(row => `
      <tr>
        <td><strong>${row.metric}</strong></td>
        <td style="color:#757575;">${row.baseline}</td>
        <td style="color:#1b5e20; font-weight:600;">${row.mvp_target}</td>
        <td style="font-weight:700; color:#0d47a1;">${row.mvp_result}</td>
        <td><small style="color:#555;">${row.evaluation_label}</small></td>
      </tr>
    `).join("");
  },

  renderCasesTable() {
    const tbody = document.getElementById("cases-table-body");
    if (!tbody) return;

    if (this.cases.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:2rem; color:#757575;">No cases matching current filter criteria.</td></tr>`;
      return;
    }

    tbody.innerHTML = this.cases.map(c => {
      const pClass = c.priority.toLowerCase();
      const sBadge = c.status === "Expert Validated" ? "badge-validated" : (c.status.includes("Review") ? "badge-review" : "badge-medium");
      const confText = c.ai_confidence ? `${c.ai_confidence.toFixed(0)}%` : "-";
      const isLowConf = c.ai_confidence && c.ai_confidence < 60;
      
      return `
        <tr>
          <td><strong style="color:#1b5e20;">${c.case_id}</strong></td>
          <td>${c.crop} <small style="color:#757575;">(${c.crop_stage})</small></td>
          <td>${c.location}</td>
          <td>
            <span class="badge badge-${pClass}">${c.priority}</span>
            ${isLowConf ? '<span class="badge" style="background:#ffebee; color:#c62828; margin-left:4px;">Low Conf</span>' : ''}
          </td>
          <td><span class="badge ${sBadge}">${c.status}</span></td>
          <td>
            <div>${c.ai_prediction || "None"}</div>
            <small style="color:#757575;">Conf: ${confText}</small>
          </td>
          <td>
            <button class="btn btn-outline" style="padding:0.35rem 0.75rem; font-size:0.85rem;" onclick="OfficerDashboard.openCaseDetail('${c.case_id}')">
              Inspect
            </button>
          </td>
        </tr>
      `;
    }).join("");
  },

  openCaseDetail(caseId) {
    const c = this.cases.find(item => item.case_id === caseId);
    if (!c) return;

    const modal = document.getElementById("case-detail-modal");
    const content = document.getElementById("case-detail-content");
    if (!modal || !content) return;

    let imgHtml = "";
    if (c.images && c.images.length > 0) {
      imgHtml = `<div style="display:flex; gap:1rem; flex-wrap:wrap; margin-top:0.75rem;">` +
        c.images.map(img => `
          <div style="border:1px solid #ddd; border-radius:8px; padding:0.5rem; max-width:220px;">
            <img src="${img.file_path}" style="width:100%; height:140px; object-fit:cover; border-radius:4px;">
            <div style="margin-top:0.4rem; font-size:0.8rem;">
              <strong>Type:</strong> ${img.image_type}<br>
              <strong>Quality Score:</strong> ${img.quality_score}/100
            </div>
          </div>
        `).join("") + "</div>";
    } else {
      imgHtml = "<p style='color:#757575; font-size:0.9rem;'>No photographic evidence attached.</p>";
    }

    content.innerHTML = `
      <h2 style="color:#1b5e20; margin-bottom:0.5rem;">Case Details: ${c.case_id}</h2>
      <p style="color:#616161; font-size:0.9rem; margin-bottom:1rem;">Anonymous Farmer: ${c.anonymous_farmer_id} | Location: ${c.location} (Approx: ${c.latitude}° N, ${c.longitude}° E)</p>
      
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1rem;">
        <div style="background:#f9fbf9; padding:1rem; border-radius:8px; border:1px solid #e0e0e0;">
          <h4 style="color:#2e7d32; margin-bottom:0.5rem;">Observation Metadata</h4>
          <p><strong>Crop:</strong> ${c.crop} ${c.variety ? '(' + c.variety + ')' : ''}</p>
          <p><strong>Stage:</strong> ${c.crop_stage}</p>
          <p><strong>Symptoms:</strong> ${c.symptoms}</p>
          <p><strong>Severity:</strong> ${c.severity}</p>
          <p><strong>First Symptom Time:</strong> ${new Date(c.first_symptom_time).toLocaleString()}</p>
          <p><strong>Submission Time:</strong> ${new Date(c.submission_time).toLocaleString()}</p>
        </div>
        <div style="background:#fdfcf9; padding:1rem; border-radius:8px; border:1px solid #e0e0e0;">
          <h4 style="color:#f57c00; margin-bottom:0.5rem;">AI & Priority Evaluation</h4>
          <p><strong>Preliminary Hypothesis:</strong> ${c.ai_prediction || "None"}</p>
          <p><strong>Confidence:</strong> ${c.ai_confidence ? c.ai_confidence.toFixed(1) + '%' : 'N/A'}</p>
          <p><strong>Alternative:</strong> ${c.ai_alternative || "None"}</p>
          <p><strong>Assigned Priority:</strong> <span class="badge badge-${c.priority.toLowerCase()}">${c.priority}</span></p>
          <p><strong>Triage Rationale:</strong> <small>${c.priority_reason || "Routine"}</small></p>
        </div>
      </div>

      <h4 style="margin-top:1rem; color:#1b5e20;">Photographic Evidence</h4>
      ${imgHtml}

      <div style="margin-top:1.25rem; background:#f0f7f0; padding:1rem; border-radius:8px; border:1px solid #c8e6c9;">
        <h4 style="color:#1b5e20; margin-bottom:0.4rem;">Authoritative Expert Validation Status</h4>
        <p><strong>Current Status:</strong> <span class="badge ${c.status === 'Expert Validated' ? 'badge-validated' : 'badge-review'}">${c.status}</span></p>
        <p><strong>Validated Diagnosis:</strong> ${c.expert_validation || "Pending Expert Review"}</p>
        <p><strong>Expert Comments / Guidance:</strong> ${c.expert_comments || "None recorded yet."}</p>
        ${c.expert_review_time ? `<p><strong>Review Timestamp:</strong> ${new Date(c.expert_review_time).toLocaleString()}</p>` : ''}
      </div>
    `;

    modal.classList.add("active");
  },

  closeModal() {
    const modal = document.getElementById("case-detail-modal");
    if (modal) modal.classList.remove("active");
  }
};
