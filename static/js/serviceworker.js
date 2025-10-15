const CACHE_NAME = "sigma-reviews-v1";
const ASSETS = [
  "/",
  "/login",
  "/home",
  "/profile",
  "/edit-profile",
  "static/css/style.css",
  "static/css/home.css",
  "static/css/login.css",
  "static/css/profilestyle.css",
  "static/css/rightstyle.css",
  "static/css/edit_profile.css",
  "static/js/app.js",
  "static/js/auth.js",
  "static/images/avatar.jpg",
  "static/icons/icon-128x128.png",
  "static/icons/icon-192x192.png",
  "static/icons/icon-384x384.png",
  "static/icons/icon-512x512.png",
  "static/icons/desktop_screenshot.png",
];

// Install Event - Cache Assets
self.addEventListener("install", (installEvt) => {
  console.log("Service Worker: Installing...");
  installEvt.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => {
        console.log("Service Worker: Caching Files");
        return cache.addAll(ASSETS);
      })
      .then(() => self.skipWaiting())
      .catch((err) => {
        console.log("Service Worker: Cache Error", err);
      })
  );
});

// Activate Event - Clean Up Old Caches
self.addEventListener("activate", (evt) => {
  console.log("Service Worker: Activated");
  evt.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log("Service Worker: Clearing Old Cache", cache);
            return caches.delete(cache);
          }
        })
      );
    })
  );
  return self.clients.claim();
});

// Fetch Event - Network First, Falling Back to Cache
self.addEventListener("fetch", (evt) => {
  // Skip cross-origin requests
  if (!evt.request.url.startsWith(self.location.origin)) {
    return;
  }

  // For API calls, use network-first strategy
  if (evt.request.url.includes("/api/")) {
    evt.respondWith(
      fetch(evt.request)
        .then((response) => {
          // Clone the response
          const responseClone = response.clone();
          // Cache the API response
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(evt.request, responseClone);
          });
          return response;
        })
        .catch(() => {
          // If network fails, try cache
          return caches.match(evt.request);
        })
    );
  } else {
    // For static assets, use cache-first strategy
    evt.respondWith(
      caches.match(evt.request).then((cachedResponse) => {
        return (
          cachedResponse ||
          fetch(evt.request)
            .then((response) => {
              // Cache new resources
              return caches.open(CACHE_NAME).then((cache) => {
                cache.put(evt.request, response.clone());
                return response;
              });
            })
            .catch(() => {
              // Return a custom offline page if available
              if (evt.request.destination === "document") {
                return caches.match("/");
              }
            })
        );
      })
    );
  }
});
