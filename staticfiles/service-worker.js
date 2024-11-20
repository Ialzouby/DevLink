// Cache version
const CACHE_NAME = 'devlink-cache-v1';

// List of assets to cache
const urlsToCache = [
    '/',
    '/static/projects/styles.css',
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

// Fetch event: Handle caching and bypass for specific URLs
self.addEventListener('fetch', (event) => {
    // List of URLs to exclude from caching
    const urlsToExclude = [
        '/accounts/login/',
        '/login/',  
        '/accounts/google/login/',
        '/accounts/google/login/callback/',
    ];

    // Check if the URL is in the list of URLs to exclude
    if (urlsToExclude.some((url) => event.request.url.includes(url))) {
        // Bypass the Service Worker for these URLs and fetch from the network
        event.respondWith(fetch(event.request));
    } else {
        // Use caching strategy for other requests
        event.respondWith(
            caches.match(event.request).then((response) => {
                return response || fetch(event.request);
            })
        );
    }
});
