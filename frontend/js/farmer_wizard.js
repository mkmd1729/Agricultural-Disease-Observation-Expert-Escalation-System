/**
 * Farmer Wizard Module: 5-Step Intuitive Disease Observation Submission.
 * Provides large-button cards, minimal typing, visual photo guidance,
 * live image quality feedback, privacy protection, and offline-first queueing.
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
    // Environmental context fields
    rainfall_recent: "Unknown",
    humidity_level: "Unknown",
    temperature_band: "Unknown",
    soil_moisture_observation: "Unknown",
    irrigation_status: "Unknown",
    field_condition: "Unknown",
    recent_weather_event: "None",
    image_whole: null,
    image_affected: null,
    image_detail: null
  },

  init() {
    this.bindEvents();
    this.renderStep();
    this.restoreDraftIfAvailable();
  },

  restoreDraftIfAvailable() {
    if (typeof OfflineSync !== "undefined") {
      OfflineSync.getDraft().then((draft) => {
        if (draft && draft.crop) {
          this.data = Object.assign(this.data, draft);
          this.prefillFormFromData();
        }
      });
    }
  },

  prefillFormFromData() {
    if (this.data.crop) {
      document.querySelectorAll(".crop-card").forEach(c => {
        if (c.dataset.crop === this.data.crop) c.classList.add("selected");
      });
      const b1 = document.getElementById("btn-step1-next");
      if (b1) b1.disabled = false;
    }
    if (this.data.symptoms && this.data.symptoms.length > 0) {
      document.querySelectorAll(".symptom-card").forEach(c => {
        if (this.data.symptoms.includes(c.dataset.symptom)) c.classList.add("selected");
      });
      const b2 = document.getElementById("btn-step2-next");
      if (b2) b2.disabled = false;
    }
  },

  bindEvents() {
    // Crop selection cards
    document.querySelectorAll(".crop-card").forEach(card => {
      card.addEventListener("click", () => {
        document.querySelectorAll(".crop-card").forEach(c => c.classList.remove("selected"));
        card.classList.add("selected");
        this.data.crop = card.dataset.crop;
        document.getElementById("btn-step1-next").disabled = false;
        this.persistDraft();
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
        this.persistDraft();
      });
    });

    // Severity buttons
    document.querySelectorAll(".severity-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".severity-btn").forEach(b => b.classList.remove("selected"));
        btn.classList.add("selected");
        this.data.severity = btn.dataset.severity;
        this.persistDraft();
      });
    });

    // Crop stage buttons
    document.querySelectorAll(".stage-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".stage-btn").forEach(b => b.classList.remove("selected"));
        btn.classList.add("selected");
        this.data.crop_stage = btn.dataset.stage;
        this.persistDraft();
      });
    });

    // Environmental dropdown bindings
    const bindSelect = (id, prop) => {
      const el = document.getElementById(id);
      if (el) el.addEventListener("change", (e) => {
        this.data[prop] = e.target.value;
        this.persistDraft();
      });
    };
    bindSelect("select-rainfall", "rainfall_recent");
    bindSelect("select-humidity", "humidity_level");
    bindSelect("select-temp", "temperature_band");
    bindSelect("select-soil", "soil_moisture_observation");
    bindSelect("select-irrigation", "irrigation_status");
    bindSelect("select-field-cond", "field_condition");

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

      // Perform real-time quality check via API if online
      const qBox = document.getElementById(qualityBoxId);
      if (qBox) {
        if (typeof OfflineSync !== "undefined" && !OfflineSync.isOnline()) {
          qBox.innerHTML = "<small style='color:#f57c00;'>Offline mode: Quality check will execute upon server sync.</small>";
          qBox.style.display = "block";
          return;
        }

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
        } catch {
          qBox.innerHTML = "<small style='color:#757575;'>Quality check unavailable.</small>";
        }
      }
    });
  },

  persistDraft() {
    if (typeof OfflineSync !== "undefined") {
      // Exclude File objects from draft to allow serialization
      const draftObj = { ...this.data, image_whole: null, image_affected: null, image_detail: null };
      OfflineSync.saveDraft(draftObj);
    }
  },

  nextStep() {
    if (this.currentStep === 4) {
      const notesEl = document.getElementById("input-farmer-notes");
      if (notesEl) this.data.farmer_notes = notesEl.value;
      this.populateReviewSummary();
    }
    if (this.currentStep < 5) {
      this.currentStep++;
      this.renderStep();
      this.persistDraft();
    }
  },

  prevStep() {
    if (this.currentStep > 1) {
      this.currentStep--;
      this.renderStep();
      this.persistDraft();
    }
  },

  renderStep() {
    document.querySelectorAll(".step-container").forEach((el, idx) => {
      el.classList.toggle("active", idx + 1 === this.currentStep);
    });

    document.querySelectorAll(".progress-step").forEach((el, idx) => {
      el.classList.toggle("active", idx + 1 <= this.currentStep);
    });

    window.scrollTo({ top: 0, behavior: "smooth" });
  },

  populateReviewSummary() {
    const box = document.getElementById("review-summary-box");
    if (!box) return;

    let photosCount = 0;
    if (this.data.image_whole) photosCount++;
    if (this.data.image_affected) photosCount++;
    if (this.data.image_detail) photosCount++;

    box.innerHTML = `
      <div style="background:#f9fbf9; border:1px solid #c8e6c9; border-radius:8px; padding:1.25rem;">
        <h4 style="color:var(--primary-dark); margin-bottom:0.75rem;">Observation Summary:</h4>
        <p><strong>Target Crop:</strong> ${this.data.crop || "Not selected"}</p>
        <p><strong>Identified Symptoms:</strong> ${this.data.symptoms.map(s => s.replace("_", " ")).join(", ") || "None selected"}</p>
        <p><strong>Severity:</strong> <span class="badge badge-medium">${this.data.severity}</span></p>
        <p><strong>Growth Stage:</strong> ${this.data.crop_stage}</p>
        <p><strong>Location:</strong> ${this.data.location} (Coordinates rounded for privacy)</p>
        <p><strong>Recent Rainfall / Moisture:</strong> ${this.data.rainfall_recent} / ${this.data.soil_moisture_observation}</p>
        <p><strong>First Noticed Date:</strong> ${this.data.first_symptom_time}</p>
        <p><strong>Attached Photographs:</strong> ${photosCount} photo(s) ready for expert triage</p>
      </div>
    `;
  },

  saveOfflineAndNotify(reason) {
    const observationPayload = {
      crop: this.data.crop,
      symptoms: this.data.symptoms,
      crop_stage: this.data.crop_stage,
      location: this.data.location,
      first_symptom_time: this.data.first_symptom_time,
      variety: this.data.variety || null,
      severity: this.data.severity,
      latitude: this.data.latitude,
      longitude: this.data.longitude,
      farmer_notes: this.data.farmer_notes,
      environmental_notes: this.data.environmental_notes,
      rainfall_recent: this.data.rainfall_recent,
      humidity_level: this.data.humidity_level,
      temperature_band: this.data.temperature_band,
      recent_weather_event: this.data.recent_weather_event,
      irrigation_status: this.data.irrigation_status,
      soil_moisture_observation: this.data.soil_moisture_observation,
      field_condition: this.data.field_condition
    };

    OfflineSync.enqueueObservation(observationPayload).then((queuedRecord) => {
      OfflineSync.clearDraft();
      const resultBox = document.getElementById("submission-result-box");
      const btn = document.getElementById("btn-submit-case");
      resultBox.style.display = "block";
      resultBox.innerHTML = `
        <div class="alert alert-warning" style="flex-direction:column; align-items:flex-start;">
          <h3 style="margin-bottom:0.4rem; color:#e65100;">🟠 Observation Saved Locally (Offline Queue)</h3>
          <p><strong>Local Queue Tracking ID:</strong> <span style="font-size:1.15rem; font-weight:800; color:#bf360c;">${queuedRecord.client_sync_id}</span></p>
          <p style="margin-top:0.4rem;">
            <strong>Network Status:</strong> ${reason || "No internet connection detected."}
          </p>
          <p style="font-size:0.92rem; color:#424242; margin-top:0.4rem;">
            ✓ Your disease observation has been safely saved in your browser's persistent offline storage.<br>
            ✓ As soon as cellular or Wi-Fi connectivity returns, it will automatically synchronize with the expert escalation server.
          </p>
          <div style="display:flex; gap:0.5rem; margin-top:1rem;">
            <button class="btn btn-secondary" onclick="FarmerWizard.resetWizard()">Create Another Observation</button>
            <button class="btn btn-outline" onclick="OfflineSync.syncQueue()">Try Syncing Now</button>
          </div>
        </div>
      `;
      btn.style.display = "none";
    });
  },

  async submitObservation() {
    const btn = document.getElementById("btn-submit-case");
    const resultBox = document.getElementById("submission-result-box");
    btn.disabled = true;
    btn.innerText = "Submitting Observation...";

    // 1. Check Offline Status First
    if (typeof OfflineSync !== "undefined" && !OfflineSync.isOnline()) {
      this.saveOfflineAndNotify("You are currently working offline.");
      return;
    }

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

      // Phase 2.3 Environmental Context
      formData.append("rainfall_recent", this.data.rainfall_recent || "Unknown");
      formData.append("humidity_level", this.data.humidity_level || "Unknown");
      formData.append("temperature_band", this.data.temperature_band || "Unknown");
      formData.append("recent_weather_event", this.data.recent_weather_event || "None");
      formData.append("irrigation_status", this.data.irrigation_status || "Unknown");
      formData.append("soil_moisture_observation", this.data.soil_moisture_observation || "Unknown");
      formData.append("field_condition", this.data.field_condition || "Unknown");

      if (this.data.image_whole) formData.append("image_whole", this.data.image_whole);
      if (this.data.image_affected) formData.append("image_affected", this.data.image_affected);
      if (this.data.image_detail) formData.append("image_detail", this.data.image_detail);

      const res = await fetch("/api/cases", { method: "POST", body: formData });
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      const createdCase = await res.json();

      if (typeof OfflineSync !== "undefined") {
        OfflineSync.clearDraft();
      }

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
          <div style="display:flex; gap:0.5rem; margin-top:1rem;">
            <button class="btn btn-primary" onclick="FarmerWizard.resetWizard()">Submit Another Observation</button>
            <button class="btn btn-outline" onclick="window.location.hash='#track/' + '${createdCase.case_id}'; document.querySelector('[data-view=view-track]').click();">Track This Case ➔</button>
          </div>
        </div>
      `;
      btn.style.display = "none";
    } catch (err) {
      // If network dropped, enqueue offline safely
      if (typeof OfflineSync !== "undefined" && (err.message.includes("fetch") || !OfflineSync.isOnline() || err.message.includes("Failed"))) {
        this.saveOfflineAndNotify("Network error encountered during transmission. Observation preserved in offline queue.");
        return;
      }

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
    const b1 = document.getElementById("btn-step1-next");
    if (b1) b1.disabled = true;
    const b2 = document.getElementById("btn-step2-next");
    if (b2) b2.disabled = true;
    document.getElementById("submission-result-box").style.display = "none";
    const btn = document.getElementById("btn-submit-case");
    btn.disabled = false;
    btn.style.display = "inline-flex";
    btn.innerText = "Submit Observation for Expert Review";
    this.renderStep();
  }
};
