self.addEventListener('install', event => event.waitUntil(self.skipWaiting()));
self.addEventListener('activate', event => event.waitUntil(self.clients.claim().then(() => self.registration.unregister())));
self.addEventListener('fetch', event => { event.respondWith(fetch(event.request, {cache: 'no-store'})); });
