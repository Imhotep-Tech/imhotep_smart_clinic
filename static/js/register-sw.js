if ('serviceWorker' in navigator && 'SyncManager' in window) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js')
      .then(registration => {
        console.log('ServiceWorker registered with scope:', registration.scope);
        
        // Register periodic sync (for newer browsers)
        if ('periodicSync' in registration) {
          const status = navigator.permissions.query({
            name: 'periodic-background-sync',
          });
          
          if (status.state === 'granted') {
            registration.periodicSync.register('task-sync', {
              minInterval: 24 * 60 * 60 * 1000, // 1 day
            });
          }
        }
      })
      .catch(error => {
        console.error('ServiceWorker registration failed:', error);
      });
  });
  
  // Setup offline task handling
  setupOfflineTaskHandling();
}

// Function to handle offline task submissions
function setupOfflineTaskHandling() {
  const taskForm = document.getElementById('task-form');
  if (taskForm) {
    taskForm.addEventListener('submit', event => {
      if (!navigator.onLine) {
        event.preventDefault();
        
        const formData = new FormData(taskForm);
        const taskData = {
          id: Date.now().toString(),
          title: formData.get('title'),
          description: formData.get('description'),
          due_date: formData.get('due_date'),
          priority: formData.get('priority')
        };
        
        saveTaskLocally(taskData).then(() => {
          // Register for background sync
          navigator.serviceWorker.ready.then(registration => {
            registration.sync.register('task-sync');
          });
          
          // Show success message
          showNotification('Task saved locally. Will sync when online.');
          
          // Reset form
          taskForm.reset();
        });
      }
    });
  }
}

// Function to save task to IndexedDB
async function saveTaskLocally(task) {
  const db = await openDatabase();
  const tx = db.transaction('offline-tasks', 'readwrite');
  await tx.objectStore('offline-tasks').add(task);
  return tx.complete;
}

// Helper function to open database
function openDatabase() {
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

// Function to show notification
function showNotification(message) {
  const notification = document.createElement('div');
  notification.className = 'notification';
  notification.textContent = message;
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.classList.add('fade-out');
    setTimeout(() => {
      document.body.removeChild(notification);
    }, 500);
  }, 3000);
}