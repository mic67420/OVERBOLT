// OVERBOLT | NO BS — Service Worker
// Stratégie : "réseau d'abord, cache en repli"
// -> avec du réseau, la dernière version s'affiche dès l'ouverture
// -> hors ligne (ou réseau lent), l'app s'ouvre depuis le cache.

const CACHE_NAME = "overbolt-cache-v20"; // incrémenter (v2, v3...) à chaque MAJ pour forcer un nettoyage propre du cache
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

// Récupération des pages : RÉSEAU D'ABORD (version à jour dès l'ouverture),
// repli sur le cache si hors ligne ou si le réseau met plus de 3 s à répondre.
// cache:"no-cache" force la revalidation (GitHub Pages met en cache ~10 min).
self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;

  event.respondWith(
    caches.open(CACHE_NAME).then((cache) => {
      const network = fetch(event.request, { cache: "no-cache" }).then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
          cache.put(event.request, networkResponse.clone());
        }
        return networkResponse;
      });
      // laisse le téléchargement se terminer (et mettre le cache à jour) même après le délai
      event.waitUntil(network.catch(() => {}));

      const timeout = new Promise((resolve) => setTimeout(() => resolve(null), 3000));
      return Promise.race([network.catch(() => null), timeout]).then((response) => {
        if (response) return response;
        return cache.match(event.request).then((cached) => cached || network);
      });
    })
  );
});
