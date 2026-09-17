// OVERBOLT | NO BS — Service Worker
// Stratégie : "stale-while-revalidate"
// -> l'app s'ouvre INSTANTANÉMENT depuis le cache (fonctionne 100% hors ligne)
// -> en parallèle, si du réseau est disponible, la nouvelle version est
//    téléchargée en arrière-plan et sera utilisée au PROCHAIN lancement.

const CACHE_NAME = "overbolt-cache-v6"; // incrémenter (v2, v3...) à chaque MAJ pour forcer un nettoyage propre du cache
const CACHE_FILES = [
  "./",
  "./index.html"
];

// Installation : on met en cache les fichiers de base dès la première visite
self.addEventListener("install", (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(CACHE_FILES))
  );
});

// Activation : on supprime les anciens caches (anciennes versions) si présents
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

// Récupération des pages : stale-while-revalidate
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

        // Répond immédiatement avec le cache si dispo (rapide + hors ligne OK),
        // sinon attend la réponse réseau (premier chargement).
        return cachedResponse || fetchPromise;
      })
    )
  );
});
