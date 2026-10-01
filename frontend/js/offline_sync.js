/**
 * Offline Sync Module for Agricultural Disease Observation System.
 * Manages local IndexedDB storage, draft saving, offline observation queues,
 * automatic network reconnection detection, retry handling, and duplicate prevention.
 */

const OfflineSync = {
  dbName: "AgriOfflineDB",
  dbVersion: 1,
  db: null,

  async init() {
    await this.initDB();
    this.bindNetworkEvents();
    this.updateStatusUI();

    // Register Service Worker if supported
    if ("serviceWorker" in navigator) {
      try {
        await navigator.serviceWorker.register("/sw.js");
        console.log("[OfflineSync] Service Worker registered successfully");
      } catch (err) {
        console.warn("[OfflineSync] Service Worker registration failed:", err);
      }
    }

    // Try auto-sync on startup if online
    if (this.isOnline()) {
      setTimeout(() => this.syncQueue(), 1200);
    }
  },

  isOnline() {
    return navigator.onLine;
  },

  initDB() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);

      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        if (!db.objectStoreNames.contains("queue")) {
          const queueStore = db.createObjectStore("queue", { keyPath: "client_sync_id" });
          queueStore.createIndex("status", "status", { unique: false });
          queueStore.createIndex("created_at", "created_at", { unique: false });
        }
        if (!db.objectStoreNames.contains("drafts")) {
          db.createObjectStore("drafts", { keyPath: "id" });
        }
      };

      request.onsuccess = (event) => {
        this.db = event.target.result;
        resolve(this.db);
      };

      request.onerror = (event) => {
        console.error("[OfflineSync] IndexedDB error:", event.target.error);
        reject(event.target.error);
      };
    });
  },

  bindNetworkEvents() {
    window.addEventListener("online", () => {
      console.log("[OfflineSync] Network status: ONLINE");
      this.updateStatusUI();
      this.syncQueue();
    });

    window.addEventListener("offline", () => {
      console.log("[OfflineSync] Network status: OFFLINE");
      this.updateStatusUI();
    });
  },

  updateStatusUI() {
    const badge = document.getElementById("network-status-badge");
    const banner = document.getElementById("offline-alert-banner");
    const syncBtn = document.getElementById("btn-manual-sync");

    const online = this.isOnline();
    if (badge) {
      if (online) {
        badge.className = "status-pill status-pill-online";
        badge.innerHTML = "🟢 Online (Connected)";
      } else {
        badge.className = "status-pill status-pill-offline";
        badge.innerHTML = "🟠 Offline Mode";
      }
    }

    if (banner) {
      banner.style.display = online ? "none" : "block";
    }

    this.getPendingObservations().then((pending) => {
      if (syncBtn) {
        if (pending.length > 0) {
          syncBtn.style.display = "inline-flex";
          syncBtn.innerHTML = `🔄 Sync Queue (${pending.length})`;
        } else {
          syncBtn.style.display = "none";
        }
      }
    });
  },

  // DRAFT MANAGEMENT
  async saveDraft(data) {
    if (!this.db) await this.initDB();
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction("drafts", "readwrite");
      const store = tx.objectStore("drafts");
      const record = { id: "current_draft", data, updated_at: new Date().toISOString() };
      store.put(record);
      tx.oncomplete = () => resolve(true);
      tx.onerror = (e) => reject(e.target.error);
    });
  },

  async getDraft() {
    if (!this.db) await this.initDB();
    return new Promise((resolve) => {
      const tx = this.db.transaction("drafts", "readonly");
      const store = tx.objectStore("drafts");
      const request = store.get("current_draft");
      request.onsuccess = () => resolve(request.result ? request.result.data : null);
      request.onerror = () => resolve(null);
    });
  },

  async clearDraft() {
    if (!this.db) await this.initDB();
    return new Promise((resolve) => {
      const tx = this.db.transaction("drafts", "readwrite");
      tx.objectStore("drafts").delete("current_draft");
      tx.oncomplete = () => resolve(true);
    });
  },

  // OFFLINE QUEUE MANAGEMENT
  async enqueueObservation(observation) {
    if (!this.db) await this.initDB();
    const client_sync_id = "OFFLINE-" + Date.now() + "-" + Math.random().toString(36).substring(2, 7).toUpperCase();

    const record = {
      client_sync_id,
      data: observation,
      status: "queued", // 'queued' | 'syncing' | 'synced' | 'failed'
      created_at: new Date().toISOString(),
      retry_count: 0,
      last_error: null,
      server_case_id: null
    };

    return new Promise((resolve, reject) => {
      const tx = this.db.transaction("queue", "readwrite");
      tx.objectStore("queue").add(record);
      tx.oncomplete = () => {
        this.updateStatusUI();
        resolve(record);
      };
      tx.onerror = (e) => reject(e.target.error);
    });
  },

  async getPendingObservations() {
    if (!this.db) await this.initDB();
    return new Promise((resolve) => {
      const tx = this.db.transaction("queue", "readonly");
      const store = tx.objectStore("queue");
      const request = store.getAll();
      request.onsuccess = () => {
        const records = request.result || [];
        resolve(records.filter((r) => r.status === "queued" || r.status === "failed"));
      };
      request.onerror = () => resolve([]);
    });
  },

  async getAllObservations() {
    if (!this.db) await this.initDB();
    return new Promise((resolve) => {
      const tx = this.db.transaction("queue", "readonly");
      const request = tx.objectStore("queue").getAll();
      request.onsuccess = () => resolve(request.result || []);
      request.onerror = () => resolve([]);
    });
  },

  async updateQueueRecord(record) {
    if (!this.db) await this.initDB();
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction("queue", "readwrite");
      tx.objectStore("queue").put(record);
      tx.oncomplete = () => {
        this.updateStatusUI();
        resolve(record);
      };
      tx.onerror = (e) => reject(e.target.error);
    });
  },

  // SYNCHRONIZATION WITH SERVER
  async syncQueue() {
    if (!this.isOnline()) {
      console.log("[OfflineSync] Cannot sync while offline.");
      return { synced: 0, failed: 0 };
    }

    const pending = await this.getPendingObservations();
    if (pending.length === 0) {
      this.updateStatusUI();
      return { synced: 0, failed: 0 };
    }

    console.log(`[OfflineSync] Starting sync for ${pending.length} pending observations...`);
    let syncedCount = 0;
    let failedCount = 0;

    for (const item of pending) {
      // DUPLICATE PREVENTION: skip if already synced
      if (item.status === "synced" && item.server_case_id) {
        continue;
      }

      item.status = "syncing";
      await this.updateQueueRecord(item);

      try {
        const res = await this.sendObservationToServer(item.data);
        if (res && res.case_id) {
          item.status = "synced";
          item.server_case_id = res.case_id;
          item.synced_at = new Date().toISOString();
          await this.updateQueueRecord(item);
          syncedCount++;
          console.log(`[OfflineSync] Observation ${item.client_sync_id} synced as ${res.case_id}`);
        } else {
          throw new Error("Server returned unexpected response");
        }
      } catch (err) {
        item.status = "failed";
        item.retry_count = (item.retry_count || 0) + 1;
        item.last_error = err.message;
        await this.updateQueueRecord(item);
        failedCount++;
        console.warn(`[OfflineSync] Failed to sync ${item.client_sync_id}:`, err);
      }
    }

    this.updateStatusUI();
    if (typeof OfficerDashboard !== "undefined" && OfficerDashboard.loadCases) {
      OfficerDashboard.loadCases();
    }
    return { synced: syncedCount, failed: failedCount };
  },

  async sendObservationToServer(data) {
    // If structured JSON data
    const payload = {
      crop: data.crop,
      symptoms: Array.isArray(data.symptoms) ? data.symptoms : [data.symptoms],
      crop_stage: data.crop_stage || "Vegetative",
      location: data.location || "Green Valley District",
      first_symptom_time: data.first_symptom_time || new Date().toISOString(),
      variety: data.variety || null,
      severity: data.severity || "Medium",
      latitude: data.latitude || null,
      longitude: data.longitude || null,
      farmer_notes: data.farmer_notes || null,
      environmental_notes: data.environmental_notes || null,
      rainfall_recent: data.rainfall_recent || "Unknown",
      humidity_level: data.humidity_level || "Unknown",
      temperature_band: data.temperature_band || "Unknown",
      recent_weather_event: data.recent_weather_event || "None",
      irrigation_status: data.irrigation_status || "Unknown",
      soil_moisture_observation: data.soil_moisture_observation || "Unknown",
      field_condition: data.field_condition || "Unknown"
    };

    const res = await fetch("/api/cases/json", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    return await res.json();
  }
};

// Auto-initialize when script loads
if (typeof window !== "undefined") {
  window.addEventListener("DOMContentLoaded", () => {
    OfflineSync.init();
  });
}
