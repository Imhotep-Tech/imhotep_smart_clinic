const CACHE_NAME = 'imhotep-tasks-v1';
const OFFLINE_URL = '/offline.html';

// Assets to cache immediately
const PRECACHE_ASSETS = [
  '/',
  '/offline.html',
  '/static/css/styles.css',
  '/static/js/app.js',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  '/static/manifest.json'
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

// Fetch event - Network-first strategy with fallback to cache
self.addEventListener('fetch', event => {
  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }

  // Skip non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }
  
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // If valid response, clone and cache
        if (response && response.status === 200) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseClone);
          });
        }
        return response;
      })
      .catch(() => {
        // If offline, try to serve from cache
        return caches.match(event.request)
          .then(cachedResponse => {
            if (cachedResponse) {
              return cachedResponse;
            }
            // If not in cache, serve offline page for navigation requests
            if (event.request.mode === 'navigate') {
              return caches.match(OFFLINE_URL);
            }
            
            // For image requests, return a placeholder
            if (event.request.destination === 'image') {
              return caches.match('/static/icons/placeholder.png');
            }
            
            // Return empty response for other resources
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
  if (event.tag === 'task-sync') {
    event.waitUntil(syncTasks());
  }
});

// Function to sync tasks when back online
async function syncTasks() {
  const db = await openTasksDatabase();
  const tasks = await db.getAll('offline-tasks');
  
  for (const task of tasks) {
    try {
      const response = await fetch('/api/tasks/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(task)
      });
      
      if (response.ok) {
        await db.delete('offline-tasks', task.id);
      }
    } catch (error) {
      console.error('Failed to sync task:', error);
    }
  }
}

// Helper function to open IndexedDB
function openTasksDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('tasks-db', 1);
    
    request.onupgradeneeded = e => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains('offline-tasks')) {
        db.createObjectStore('offline-tasks', { keyPath: 'id' });
      }
    };
    
    request.onsuccess = e => resolve(e.target.result);
    request.onerror = e => reject(e.target.error);
  });
}