/* ScamShield Mobile PWA Service Worker */

const CACHE_NAME = 'scamshield-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/static/css/style.css',
  '/static/css/components.css',
  '/static/css/responsive.css',
  '/static/js/main.js',
  '/static/js/language.js',
  '/static/js/scan.js',
  '/static/manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
