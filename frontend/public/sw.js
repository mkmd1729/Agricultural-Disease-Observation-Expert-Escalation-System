/**
 * Service Worker for Agricultural Disease Observation App.
 * Provides offline application shell caching and offline resilience for farmers.
 */

const CACHE_NAME = "agri-obs-shell-v2";
const SHELL_ASSETS = [
  "/",
  "/index.html",
  "/css/styles.css",
  "/js/app.js",
  "/js/farmer_wizard.js",
  "/js/officer_dashboard.js",
  "/js/expert_station.js",
  "/js/edge_cases.js",
  "/js/offline_sync.js",
  "/js/farmer_track.js",
  "/guidance/photo1_whole_plant.jpg",
  "/guidance/photo2_affected_area.jpg",
  "/guidance/photo3_leaf_detail.jpg"
];

// Install: pre-cache shell assets
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("[SW] Pre-caching offline application shell");
      return cache.addAll(SHELL_ASSETS);
    }).then(() => self.skipWaiting())
  );
});

// Activate: clean up old cache versions
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch: Network-first for /api, Cache-first for static shell assets
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  // For API calls, try network first; if offline, return structured offline response
  if (url.pathname.startsWith("/api/")) {
    event.respondWith(
      fetch(event.request).catch(() => {
        return new Response(
          JSON.stringify({
            offline: true,
            message: "Offline mode active. Your request will sync when connectivity returns."
          }),
          {
            status: 503,
            headers: { "Content-Type": "application/json" }
          }
        );
      })
    );
    return;
  }

  // For static shell assets, try cache first, fall back to network
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }
      return fetch(event.request).then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200 && event.request.method === "GET") {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      });
    }).catch(() => {
      // Offline fallback for HTML navigation
      if (event.request.mode === "navigate") {
        return caches.match("/index.html");
      }
    })
  );
});
