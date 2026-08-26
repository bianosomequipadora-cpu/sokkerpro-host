const CACHE_NAME = 'sokkerpro-v6';
const assets = [
  'painel.html',
  'index.html'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(assets)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key)))).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (url.pathname.endsWith('/config.json')) {
    event.respondWith(fetch(event.request, {cache: 'no-store'}));
    return;
  }
  event.respondWith(fetch(event.request, {cache: 'no-store'}).then(response => { if (response.ok && new URL(event.request.url).pathname.endsWith('/painel.html')) { const clone=response.clone(); caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone)); } return response; }).catch(() => caches.match(event.request)));
});
