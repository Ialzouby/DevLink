// Cache version
const CACHE_NAME = 'devlink-cache-v1';

// List of assets to cache
const urlsToCache = [
    '/',
    '/static/projects/css/styles.css',
    '/static/projects/images/logo-192x192.png',
    '/static/projects/images/logo-512x512.png',
    // Add other URLs (scripts, fonts, etc.) that you want to cache
];

// Install event: Cache resources
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
});

// Fetch event: Serve cached resources if available
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Return cached response if found, or fetch from network
                return response || fetch(event.request);
            })
    );
});

// Activate event: Clean up old caches
self.addEventListener('activate', (event) => {
    const cacheWhitelist = [CACHE_NAME];
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (!cacheWhitelist.includes(cacheName)) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});
