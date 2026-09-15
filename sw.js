// OVERBOLT | NO BS â€” Service Worker
// StratÃ©gie : "stale-while-revalidate"
// -> l'app s'ouvre INSTANTANÃ‰MENT depuis le cache (fonctionne 100% hors ligne)
// -> en parallÃ¨le, si du rÃ©seau est disponible, la nouvelle version est
//    tÃ©lÃ©chargÃ©e en arriÃ¨re-plan et sera utilisÃ©e au PROCHAIN lancement.

const CACHE_NAME = "overbolt-cache-v3"; // incrÃ©menter (v2, v3...) Ã  chaque MAJ pour forcer un nettoyage propre du cache
const CACHE_FILES = [
  "./",
  "./index.html"
];

// Installation : on met en cache les fichiers de base dÃ¨s la premiÃ¨re visite
self.addEventListener("install", (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(CACHE_FILES))
  );
});

// Activation : on supprime les anciens caches (anciennes versions) si prÃ©sents
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// RÃ©cupÃ©ration des pages : stale-while-revalidate
self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;

  event.respondWith(
    caches.open(CACHE_NAME).then((cache) =>
      cache.match(event.request).then((cachedResponse) => {
        const fetchPromise = fetch(event.request)
          .then((networkResponse) => {
            if (networkResponse && networkResponse.status === 200) {
              cache.put(event.request, networkResponse.clone());
            }
            return networkResponse;
          })
          .catch(() => cachedResponse); // hors ligne -> on retombe sur le cache

        // RÃ©pond immÃ©diatement avec le cache si dispo (rapide + hors ligne OK),
        // sinon attend la rÃ©ponse rÃ©seau (premier chargement).
        return cachedResponse || fetchPromise;
      })
    )
  );
});
