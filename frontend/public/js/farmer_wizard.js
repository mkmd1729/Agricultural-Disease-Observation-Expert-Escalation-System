/**
 * Farmer Wizard Module: 5-Step Intuitive Disease Observation Submission.
 * Provides large-button cards, minimal typing, visual photo guidance,
 * live image quality feedback, and privacy protection.
 */

const FarmerWizard = {
  currentStep: 1,
  data: {
    crop: "",
    variety: "",
    symptoms: [],
    severity: "Medium",
    first_symptom_time: new Date().toISOString().split("T")[0],
    location: "Green Valley District",
    latitude: 11.25,
    longitude: 77.15,
    crop_stage: "Vegetative",
    farmer_notes: "",
    environmental_notes: "",
    image_whole: null,
    image_affected: null,
    image_detail: null
  },

  init() {
    this.bindEvents();
    this.renderStep();
  },

  bindEvents() {
    // Crop selection cards
    document.querySelectorAll(".crop-card").forEach(card => {
      card.addEventListener("click", (e) => {
        document.querySelectorAll(".crop-card").forEach(c => c.classList.remove("selected"));
        card.classList.add("selected");
        this.data.crop = card.dataset.crop;
        document.getElementById("btn-step1-next").disabled = false;
      });
    });

    // Symptom selection cards
    document.querySelectorAll(".symptom-card").forEach(card => {
      card.addEventListener("click", () => {
        card.classList.toggle("selected");
        const sym = card.dataset.symptom;
        if (this.data.symptoms.includes(sym)) {
          this.data.symptoms = this.data.symptoms.filter(s => s !== sym);
        } else {
          this.data.symptoms.push(sym);
        }
        document.getElementById("btn-step2-next").disabled = this.data.symptoms.length === 0;
      });
    });

    // Severity buttons
    document.querySelectorAll(".severity-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".severity-btn").forEach(b => b.classList.remove("selected"));
        btn.classList.add("selected");
        this.data.severity = btn.dataset.severity;
      });
    });

    // Crop stage buttons
    document.querySelectorAll(".stage-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".stage-btn").forEach(b => b.classList.remove("selected"));
        btn.classList.add("selected");
        this.data.crop_stage = btn.dataset.stage;
      });
    });

    // Image file inputs with real-time live quality check
    this.setupLiveImageInput("input-img-whole", "preview-whole", "quality-whole", "image_whole");
    this.setupLiveImageInput("input-img-affected", "preview-affected", "quality-affected", "image_affected");
    this.setupLiveImageInput("input-img-detail", "preview-detail", "quality-detail", "image_detail");
  },

  setupLiveImageInput(inputId, previewId, qualityBoxId, dataKey) {
    const input = document.getElementById(inputId);
    if (!input) return;

    input.addEventListener("change", async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      this.data[dataKey] = file;

      // Show thumbnail
      const reader = new FileReader();
      reader.onload = (re) => {
        const previewEl = document.getElementById(previewId);
        if (previewEl) {
          previewEl.src = re.target.result;
          previewEl.style.display = "block";
        }
      };
      reader.readAsDataURL(file);

      // Perform real-time quality check via API
      const qBox = document.getElementById(qualityBoxId);
      if (qBox) {
        qBox.innerHTML = "<small>Analyzing image quality...</small>";
        qBox.style.display = "block";
        try {
          const formData = new FormData();
          formData.append("image", file);
          const res = await fetch("/api/quality-check", { method: "POST", body: formData });
          const qData = await res.json();

          let adviceHtml = "";
          if (qData.warnings && qData.warnings.length > 0) {
            adviceHtml = `<div class="alert alert-warning" style="margin-top:0.5rem; padding:0.5rem 0.75rem; font-size:0.85rem;">
              <strong>Photo Notice:</strong> ${qData.warnings.join("<br>")}
              <br><span style="color:#2e7d32;"><strong>Tip:</strong> ${qData.farmer_advice.join(" ")}</span>
            </div>`;
          } else {
            adviceHtml = `<div class="alert alert-success" style="margin-top:0.5rem; padding:0.5rem 0.75rem; font-size:0.85rem;">
              ✓ Good lighting & clear focus (Quality score: ${qData.quality_score}/100)
            </div>`;
          }
          qBox.innerHTML = adviceHtml;
        } catch (err) {
          qBox.innerHTML = "<small style='color:green;'>Image attached successfully.</small>";
        }
      }
    });
  },

  nextStep() {
    if (this.currentStep < 5) {
      this.currentStep++;
      this.renderStep();
    }
  },

  prevStep() {
    if (this.currentStep > 1) {
      this.currentStep--;
      this.renderStep();
    }
  },

  renderStep() {
    // Update progress indicator
    for (let i = 1; i <= 5; i++) {
      const stepEl = document.getElementById(`p-step-${i}`);
      const containerEl = document.getElementById(`step-content-${i}`);
      if (stepEl) {
        stepEl.classList.remove("active", "completed");
        if (i === this.currentStep) stepEl.classList.add("active");
        else if (i < this.currentStep) stepEl.classList.add("completed");
      }
      if (containerEl) {
        containerEl.classList.toggle("active", i === this.currentStep);
      }
    }

    // Populate review summary on Step 5
    if (this.currentStep === 5) {
      this.renderReviewSummary();
    }
  },

  renderReviewSummary() {
    const sumEl = document.getElementById("review-summary-box");
    if (!sumEl) return;

    const symText = this.data.symptoms.map(s => s.replace(/_/g, " ")).join(", ") || "None specified";
    const photosCount = [this.data.image_whole, this.data.image_affected, this.data.image_detail].filter(Boolean).length;

    sumEl.innerHTML = `
      <div style="background:#f8f9fa; border-radius:8px; padding:1.25rem; border:1px solid #e0e0e0;">
        <h3 style="color:#1b5e20; margin-bottom:0.75rem; font-size:1.15rem;">Observation Summary</h3>
        <p><strong>Selected Crop:</strong> ${this.data.crop || "Not chosen"}</p>
        <p><strong>Observed Symptoms:</strong> ${symText} (Severity: ${this.data.severity})</p>
        <p><strong>Crop Growth Stage:</strong> ${this.data.crop_stage}</p>
        <p><strong>Location:</strong> ${this.data.location} (Approx: ${this.data.latitude}° N, ${this.data.longitude}° E)</p>
        <p><strong>First Noticed Date:</strong> ${this.data.first_symptom_time}</p>
        <p><strong>Attached Photographs:</strong> ${photosCount} photo(s) ready for expert triage</p>
      </div>
    `;
  },

  async submitObservation() {
    const btn = document.getElementById("btn-submit-case");
    const resultBox = document.getElementById("submission-result-box");
    btn.disabled = true;
    btn.innerText = "Submitting Observation...";

    try {
      const formData = new FormData();
      formData.append("crop", this.data.crop);
      formData.append("symptoms", JSON.stringify(this.data.symptoms));
      formData.append("crop_stage", this.data.crop_stage);
      formData.append("location", this.data.location);
      formData.append("first_symptom_time", this.data.first_symptom_time);
      formData.append("severity", this.data.severity);
      formData.append("latitude", this.data.latitude);
      formData.append("longitude", this.data.longitude);
      if (this.data.farmer_notes) formData.append("farmer_notes", this.data.farmer_notes);
      if (this.data.environmental_notes) formData.append("environmental_notes", this.data.environmental_notes);

      if (this.data.image_whole) formData.append("image_whole", this.data.image_whole);
      if (this.data.image_affected) formData.append("image_affected", this.data.image_affected);
      if (this.data.image_detail) formData.append("image_detail", this.data.image_detail);

      const res = await fetch("/api/cases", { method: "POST", body: formData });
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      const createdCase = await res.json();

      resultBox.style.display = "block";
      resultBox.innerHTML = `
        <div class="alert alert-success" style="flex-direction:column; align-items:flex-start;">
          <h3 style="margin-bottom:0.4rem;">✓ Observation Submitted Successfully!</h3>
          <p><strong>Case Reference ID:</strong> <span style="font-size:1.25rem; font-weight:800; color:#1b5e20;">${createdCase.case_id}</span></p>
          <p><strong>Anonymous Farmer ID:</strong> ${createdCase.anonymous_farmer_id}</p>
          <p><strong>Assigned Priority:</strong> <span class="badge badge-${createdCase.priority.toLowerCase()}">${createdCase.priority} Priority</span></p>
          <hr style="width:100%; margin:0.75rem 0; border:0; border-top:1px solid #c8e6c9;">
          <div style="background:rgba(255,255,255,0.7); padding:0.75rem; border-radius:6px; width:100%;">
            <p><strong>Preliminary AI-Assisted Hypothesis:</strong> ${createdCase.ai_prediction || "Under processing"}</p>
            <p><strong>Calculated Model Confidence:</strong> ${createdCase.ai_confidence ? createdCase.ai_confidence.toFixed(1) + '%' : 'Pending'} 
              <span style="font-size:0.85rem; color:#616161;">(Needs Expert Validation)</span>
            </p>
            <p style="font-size:0.85rem; color:#c62828; margin-top:0.25rem;">
              <em>Notice: Model confidence is NOT a confirmed diagnosis. An agricultural expert will validate this case shortly.</em>
            </p>
          </div>
          <button class="btn btn-primary" style="margin-top:1rem;" onclick="FarmerWizard.resetWizard()">Submit Another Observation</button>
        </div>
      `;
      btn.style.display = "none";
    } catch (err) {
      resultBox.style.display = "block";
      resultBox.innerHTML = `
        <div class="alert alert-danger">
          <strong>Submission failed:</strong> ${err.message}. Please verify the connection and try again.
        </div>
      `;
      btn.disabled = false;
      btn.innerText = "Try Submitting Again";
    }
  },

  resetWizard() {
    this.currentStep = 1;
    this.data.crop = "";
    this.data.symptoms = [];
    this.data.image_whole = null;
    this.data.image_affected = null;
    this.data.image_detail = null;
    document.querySelectorAll(".crop-card, .symptom-card").forEach(c => c.classList.remove("selected"));
    document.querySelectorAll("input[type=file]").forEach(i => i.value = "");
    document.querySelectorAll(".preview-thumbnail").forEach(p => p.style.display = "none");
    document.querySelectorAll(".quality-feedback-box").forEach(b => b.style.display = "none");
    document.getElementById("btn-step1-next").disabled = true;
    document.getElementById("btn-step2-next").disabled = true;
    document.getElementById("submission-result-box").style.display = "none";
    const btn = document.getElementById("btn-submit-case");
    btn.disabled = false;
    btn.style.display = "inline-flex";
    btn.innerText = "Submit Observation for Expert Review";
    this.renderStep();
  }
};
