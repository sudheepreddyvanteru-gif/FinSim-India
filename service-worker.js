const CACHE_NAME = 'finsim-india-pwa-v1';
const APP_ROOT = '/FinSim-India/';

self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    await cache.addAll([
      APP_ROOT,
      APP_ROOT + 'manifest.webmanifest',
      APP_ROOT + 'icons/icon-192.png',
      APP_ROOT + 'icons/icon-512.png'
    ]);
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(key => key.startsWith('finsim-india-pwa-') && key !== CACHE_NAME).map(key => caches.delete(key)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== 'GET' || url.origin !== self.location.origin) return;

  if (request.mode === 'navigate' && url.pathname.startsWith(APP_ROOT)) {
    event.respondWith((async () => {
      try {
        const response = await fetch(request);
        if (response && response.ok) {
          const cache = await caches.open(CACHE_NAME);
          cache.put(APP_ROOT, response.clone()).catch(() => {});
        }
        return response;
      } catch (_) {
        return (await caches.match(APP_ROOT)) || new Response('FinSim India is offline. Reconnect to the internet and retry.', {
          status: 503,
          headers: {'Content-Type':'text/plain; charset=utf-8'}
        });
      }
    })());
  }
});
