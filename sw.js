const CACHE_NAME = 'sokkerpro-v10';
const assets = [
  'painel.html',
  'index.html'
];

self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(assets);
    })
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  // API calls (github) - sempre buscar da rede
  if(event.request.url.includes('api.github.com')){
    event.respondWith(fetch(event.request));
    return;
  }
  // Arquivos estaticos - cache-first
  event.respondWith(
    caches.match(event.request)
      .then(cached => cached || fetch(event.request))
  );
});