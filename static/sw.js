/**
 * Lao Job Website - Service Worker
 * Provides offline support and caching
 */

const CACHE_NAME = 'laojobs-v1';
const STATIC_CACHE = 'laojobs-static-v1';
const DYNAMIC_CACHE = 'laojobs-dynamic-v1';

// Files to cache immediately
const STATIC_FILES = [
    '/',
    '/static/css/main.css',
    '/static/js/main.js',
    '/static/manifest.json',
    'https://fonts.googleapis.com/css2?family=Noto+Sans+Lao:wght@300;400;500;600;700;800&display=swap',
];

// Install event - cache static assets
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {
                console.log('[SW] Caching static files');
                return cache.addAll(STATIC_FILES);
            })
            .then(() => self.skipWaiting())
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys()
            .then(keys => {
                return Promise.all(
                    keys.filter(key => key !== STATIC_CACHE && key !== DYNAMIC_CACHE)
                        .map(key => caches.delete(key))
                );
            })
            .then(() => self.clients.claim())
    );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // Skip API requests and admin
    if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/admin/')) {
        return;
    }

    // For HTML pages - network first, fallback to cache
    if (request.headers.get('accept').includes('text/html')) {
        event.respondWith(
            fetch(request)
                .then(response => {
                    // Clone response for caching
                    const clonedResponse = response.clone();
                    caches.open(DYNAMIC_CACHE)
                        .then(cache => cache.put(request, clonedResponse));
                    return response;
                })
                .catch(() => {
                    return caches.match(request)
                        .then(cachedResponse => {
                            if (cachedResponse) {
                                return cachedResponse;
                            }
                            // Return offline page if available
                            return caches.match('/offline/');
                        });
                })
        );
        return;
    }

    // For static assets - cache first, fallback to network
    event.respondWith(
        caches.match(request)
            .then(cachedResponse => {
                if (cachedResponse) {
                    return cachedResponse;
                }

                return fetch(request)
                    .then(response => {
                        // Don't cache non-successful responses
                        if (!response || response.status !== 200) {
                            return response;
                        }

                        // Clone response for caching
                        const clonedResponse = response.clone();
                        caches.open(DYNAMIC_CACHE)
                            .then(cache => cache.put(request, clonedResponse));

                        return response;
                    });
            })
    );
});

// Background sync for saved jobs
self.addEventListener('sync', event => {
    if (event.tag === 'sync-saved-jobs') {
        event.waitUntil(syncSavedJobs());
    }
});

async function syncSavedJobs() {
    // Get pending saved jobs from IndexedDB and sync with server
    console.log('[SW] Syncing saved jobs');
}

// Push notifications
self.addEventListener('push', event => {
    if (event.data) {
        const data = event.data.json();

        const options = {
            body: data.body,
            icon: '/static/images/icon-192.png',
            badge: '/static/images/badge-72.png',
            vibrate: [100, 50, 100],
            data: {
                url: data.url || '/',
            },
            actions: [
                { action: 'view', title: 'ເບິ່ງ' },
                { action: 'close', title: 'ປິດ' },
            ],
        };

        event.waitUntil(
            self.registration.showNotification(data.title, options)
        );
    }
});

// Notification click handler
self.addEventListener('notificationclick', event => {
    event.notification.close();

    if (event.action === 'view' || !event.action) {
        const url = event.notification.data.url;
        event.waitUntil(
            clients.matchAll({ type: 'window' })
                .then(clientList => {
                    // Check if there's an open window
                    for (const client of clientList) {
                        if (client.url === url && 'focus' in client) {
                            return client.focus();
                        }
                    }
                    // Open new window
                    if (clients.openWindow) {
                        return clients.openWindow(url);
                    }
                })
        );
    }
});
