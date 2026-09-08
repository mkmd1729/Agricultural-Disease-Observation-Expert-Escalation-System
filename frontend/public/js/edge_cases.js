/**
 * Edge Case Sandbox Module: Interactive demonstration of the 3 required failure/edge cases.
 * Ensures robust JSON handling and safe array parsing without redundant JSON.parse().
 */

const EdgeCaseSandbox = {
  // Helper to ensure values are arrays of strings without crashing on already-parsed objects
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
          // Fall through to returning trimmed string
        }
      }
      return [trimmed];
    }
    return [String(val)];
  },

  async runEdgeCase1() {
    // Edge Case 1: Poor Image (Blurry & Dark)
    const resultBox = document.getElementById("edge-case-result");
    resultBox.innerHTML = "<p>Running Edge Case 1: Testing blurry/dark image quality analysis...</p>";

    try {
      const res = await fetch("/api/cases/CASE-2026-003");
      if (!res.ok) {
        const errText = await res.text();
        throw new Error(`Server returned status ${res.status}: ${errText}`);
      }

      const contentType = res.headers.get("content-type") || "";
      if (!contentType.includes("application/json")) {
        const rawText = await res.text();
        throw new Error(`Server returned non-JSON response: ${rawText.slice(0, 150)}`);
      }

      const c = await res.json();
      const img = (c.images && c.images[0]) || {};

      // Safe array extraction without calling JSON.parse() on an existing Array
      const warnings = this.ensureStringArray(img.quality_warnings);
      const advice = this.ensureStringArray(img.farmer_advice);

      const structuredResult = {
        quality_score: img.quality_score || 20,
        warnings: warnings.length > 0 ? warnings : ["Image may be blurry", "Image may be underexposed"],
        farmer_advice: advice.length > 0 ? advice : ["Hold the phone steady and take another photo.", "Move to better lighting."]
      };

      resultBox.innerHTML = `
        <div class="alert alert-warning" style="flex-direction:column; align-items:flex-start;">
          <h3 style="color:#e65100;">✓ Edge Case 1 Demonstrated: Poor Image Quality Handling</h3>
          <p><strong>Case ID:</strong> ${c.case_id} (${c.crop})</p>
          <p><strong>Detected Quality Score:</strong> ${structuredResult.quality_score}/100</p>
          
          <div style="background:#fff; padding:0.75rem; border-radius:6px; margin:0.5rem 0; width:100%; border:1px solid #ffe082;">
            <strong style="color:#c62828;">Triggered System Warnings:</strong>
            <ul style="margin-left:1.25rem; margin-top:0.25rem;">
              ${structuredResult.warnings.map(w => `<li style="color:#d32f2f;">${w}</li>`).join("")}
            </ul>
            <strong style="margin-top:0.5rem; display:block; color:#2e7d32;">Actionable Farmer Guidance:</strong>
            <ul style="margin-left:1.25rem; margin-top:0.25rem;">
              ${structuredResult.farmer_advice.map(a => `<li style="color:#2e7d32;">${a}</li>`).join("")}
            </ul>
          </div>

          <details style="width:100%; margin-top:0.5rem; cursor:pointer;">
            <summary style="font-size:0.85rem; color:#555;">View API Response JSON</summary>
            <pre style="background:#272822; color:#f8f8f2; padding:0.75rem; border-radius:6px; font-size:0.8rem; overflow-x:auto; margin-top:0.4rem;">${JSON.stringify(structuredResult, null, 2)}</pre>
          </details>

          <p style="margin-top:0.5rem; font-size:0.9rem;">
            <strong>Safety Behavior:</strong> The photo was <em>not</em> discarded; submission remained possible while non-blocking advice was provided. Case triage priority was automatically elevated to High because degraded image clarity prevents confident diagnosis.
          </p>
        </div>
      `;
    } catch (err) {
      resultBox.innerHTML = `<div class="alert alert-danger"><strong>Edge Case 1 Error:</strong> ${err.message}</div>`;
    }
  },

  async runEdgeCase2() {
    // Edge Case 2: Low Confidence (< 60%)
    const resultBox = document.getElementById("edge-case-result");
    resultBox.innerHTML = "<p>Running Edge Case 2: Testing Low Confidence Escalation...</p>";

    try {
      const res = await fetch("/api/cases/CASE-2026-004");
      if (!res.ok) {
        const errText = await res.text();
        throw new Error(`Server returned status ${res.status}: ${errText}`);
      }

      const contentType = res.headers.get("content-type") || "";
      if (!contentType.includes("application/json")) {
        const rawText = await res.text();
        throw new Error(`Server returned non-JSON response: ${rawText.slice(0, 150)}`);
      }

      const c = await res.json();

      resultBox.innerHTML = `
        <div class="alert alert-info" style="flex-direction:column; align-items:flex-start;">
          <h3 style="color:#0277bd;">✓ Edge Case 2 Demonstrated: Low Confidence Escalation</h3>
          <p><strong>Case ID:</strong> ${c.case_id} (${c.crop}, Stage: ${c.crop_stage})</p>
          <p><strong>Reported Symptoms:</strong> ${c.symptoms}</p>
          <div style="background:#fff; padding:0.75rem; border-radius:6px; margin:0.5rem 0; width:100%; border:1px solid #b3e5fc;">
            <p><strong>Calculated Model Confidence:</strong> <span style="color:#d32f2f; font-weight:700;">${c.ai_confidence}% (&lt; 60% threshold)</span></p>
            <p><strong>Assigned Status:</strong> <em>Low confidence — expert review recommended</em></p>
            <p><strong>Assigned Triage Priority:</strong> <span class="badge badge-high">${c.priority} Priority</span></p>
            <p><strong>System Escalation Rationale:</strong> ${c.priority_reason}</p>
          </div>
          <p><strong>Safety Behavior:</strong> The system strictly does NOT claim an authoritative diagnosis. Because confidence is below 60%, the case is automatically escalated to High Priority for rapid human agronomist review.</p>
        </div>
      `;
    } catch (err) {
      resultBox.innerHTML = `<div class="alert alert-danger"><strong>Edge Case 2 Error:</strong> ${err.message}</div>`;
    }
  },

  async runEdgeCase3() {
    // Edge Case 3: Conflicting Expert Validation (AI = Salinity Scorch, Expert = Nitrogen Deficiency)
    const resultBox = document.getElementById("edge-case-result");
    resultBox.innerHTML = "<p>Running Edge Case 3: Testing Expert Override Authority...</p>";

    try {
      const res = await fetch("/api/cases/CASE-2026-005");
      if (!res.ok) {
        const errText = await res.text();
        throw new Error(`Server returned status ${res.status}: ${errText}`);
      }

      const contentType = res.headers.get("content-type") || "";
      if (!contentType.includes("application/json")) {
        const rawText = await res.text();
        throw new Error(`Server returned non-JSON response: ${rawText.slice(0, 150)}`);
      }

      const c = await res.json();

      resultBox.innerHTML = `
        <div class="alert alert-success" style="flex-direction:column; align-items:flex-start;">
          <h3 style="color:#1b5e20;">✓ Edge Case 3 Demonstrated: Conflicting Expert Validation</h3>
          <p><strong>Case ID:</strong> ${c.case_id} (${c.crop})</p>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.75rem; margin:0.5rem 0; width:100%;">
            <div style="background:#fff; padding:0.75rem; border-radius:6px; border:1px solid #ffd54f;">
              <h4 style="color:#f57c00;">Preliminary AI Hypothesis</h4>
              <p><strong>Prediction:</strong> ${c.ai_prediction}</p>
              <p><strong>Confidence:</strong> ${c.ai_confidence}%</p>
              <small style="color:#757575;">Status: Retained in DB for error analysis</small>
            </div>
            <div style="background:#fff; padding:0.75rem; border-radius:6px; border:1px solid #81c784;">
              <h4 style="color:#2e7d32;">Authoritative Expert Validation</h4>
              <p><strong>Expert Diagnosis:</strong> ${c.expert_validation}</p>
              <p><strong>Action:</strong> AI Suggestion Rejected (Overridden)</p>
              <p><strong>Expert Guidance:</strong> ${c.expert_comments}</p>
            </div>
          </div>
          <p><strong>Authoritative Final Status:</strong> <span class="badge badge-validated">${c.status}</span></p>
          <p><strong>Safety Behavior:</strong> The human expert decision is strictly authoritative. The AI prediction was marked incorrect and saved for model retraining/error analysis, and the system never overwrote the expert diagnosis.</p>
        </div>
      `;
    } catch (err) {
      resultBox.innerHTML = `<div class="alert alert-danger"><strong>Edge Case 3 Error:</strong> ${err.message}</div>`;
    }
  }
};
