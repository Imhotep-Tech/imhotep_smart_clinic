const CACHE_NAME = 'imhotep-clinic-v1';
const OFFLINE_URL = '/offline.html';

// Assets to cache immediately
const PRECACHE_ASSETS = [
  '/',
  '/offline.html',
  '/static/css/styles.css',
  '/static/main.js',
  '/static/js/register-sw.js',
  '/static/imhotep_clinic.png',
  '/static/manifest.json',
  '/static/icons/placeholder.png',
  // Pre-cache important HTML pages for offline access
  '/login/',
  '/register/',
  '/dashboard/',
  '/privacy.html',
  '/terms.html',
  // Add more key pages as needed
];

// Install event
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        return cache.addAll(PRECACHE_ASSETS);
      })
      .then(() => {
        return self.skipWaiting();
      })
  );
});

// Activate event
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames
          .filter(cacheName => cacheName !== CACHE_NAME)
          .map(cacheName => caches.delete(cacheName))
      );
    }).then(() => {
      return self.clients.claim();
    })
  );
});

// Fetch event - Network-first strategy with dynamic caching for HTML and static assets
self.addEventListener('fetch', event => {
  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }

  // Skip non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  // Cache API GET responses for offline read-only access
  if (event.request.url.includes('/api/')) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          if (response && response.status === 200) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then(cache => {
              cache.put(event.request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          return caches.match(event.request).then(cachedResponse => {
            if (cachedResponse) {
              return cachedResponse;
            }
            if (event.request.mode === 'navigate') {
              return caches.match(OFFLINE_URL);
            }
            return new Response('', {
              status: 408,
              headers: { 'Content-Type': 'text/plain' }
            });
          });
        })
    );
    return;
  }

  // Dynamically cache HTML pages and static assets
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Only cache valid responses
        if (response && response.status === 200 && (event.request.destination === 'document' || event.request.destination === 'script' || event.request.destination === 'style' || event.request.destination === 'image' || event.request.url.endsWith('.js') || event.request.url.endsWith('.css') || event.request.url.endsWith('.png') || event.request.url.endsWith('.jpg') || event.request.url.endsWith('.jpeg') || event.request.url.endsWith('.svg'))) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseClone);
          });
        }
        return response;
      })
      .catch(() => {
        return caches.match(event.request).then(cachedResponse => {
          if (cachedResponse) {
            return cachedResponse;
          }
          if (event.request.mode === 'navigate') {
            return caches.match(OFFLINE_URL);
          }
          // For image requests, return a placeholder
          if (event.request.destination === 'image') {
            return caches.match('/static/icons/placeholder.png');
          }
          return new Response('', {
            status: 408,
            headers: { 'Content-Type': 'text/plain' }
          });
        });
      })
  );
});

// Background sync for offline form submissions
self.addEventListener('sync', event => {
  if (event.tag === 'appointment-sync' || event.tag === 'medical-record-sync') {
    event.waitUntil(syncData(event.tag));
  }
});

// Function to sync data when back online
async function syncData(syncTag) {
  const db = await openDatabase();
  const storeName = syncTag === 'appointment-sync' ? 'offline-appointments' : 'offline-medical-records';
  const endpoint = syncTag === 'appointment-sync' ? '/api/appointments/' : '/api/medical-records/';
  
  try {
    const tx = db.transaction(storeName, 'readonly');
    const store = tx.objectStore(storeName);
    const items = await store.getAll();
    
    for (const item of items) {
      try {
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
          },
          body: JSON.stringify(item)
        });
        
        if (response.ok) {
          // Delete item from IndexedDB if successfully synced
          const deleteTx = db.transaction(storeName, 'readwrite');
          await deleteTx.objectStore(storeName).delete(item.id);
        }
      } catch (error) {
        console.error(`Failed to sync ${syncTag} data:`, error);
      }
    }
  } catch (error) {
    console.error(`Error accessing IndexedDB for ${syncTag}:`, error);
  }
}

// Helper function to open IndexedDB
function openDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('clinic-db', 1);
    
    request.onupgradeneeded = e => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains('offline-appointments')) {
        db.createObjectStore('offline-appointments', { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains('offline-medical-records')) {
        db.createObjectStore('offline-medical-records', { keyPath: 'id' });
      }
    };
    
    request.onsuccess = e => resolve(e.target.result);
    request.onerror = e => reject(e.target.error);
  });
}

// Helper function to get CSRF token
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}