if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js')
      .then(registration => {
        console.log('ServiceWorker registered with scope:', registration.scope);
        
        // Register for background sync if supported
        if ('SyncManager' in window) {
          // Register periodic sync (for newer browsers)
          if ('periodicSync' in registration) {
            navigator.permissions.query({
              name: 'periodic-background-sync',
            }).then(status => {
              if (status.state === 'granted') {
                registration.periodicSync.register('clinic-sync', {
                  minInterval: 24 * 60 * 60 * 1000, // 1 day
                });
              }
            });
          }
          
          // Setup offline data handling
          setupOfflineDataHandling();
        }
      })
      .catch(error => {
        console.error('ServiceWorker registration failed:', error);
      });
  });
}

// Function to handle offline data submissions
function setupOfflineDataHandling() {
  // Handle appointments when offline
  setupOfflineForm('appointment-form', 'appointment-sync', formatAppointmentData);
  
  // Handle medical records when offline
  setupOfflineForm('medical-record-form', 'medical-record-sync', formatMedicalRecordData);
}

// Generic function to handle offline form submissions
function setupOfflineForm(formId, syncTag, dataFormatter) {
  const form = document.getElementById(formId);
  if (form) {
    form.addEventListener('submit', event => {
      if (!navigator.onLine) {
        event.preventDefault();
        
        const formData = new FormData(form);
        const data = dataFormatter(formData);
        
        saveDataLocally(data, syncTag).then(() => {
          // Register for background sync
          navigator.serviceWorker.ready.then(registration => {
            registration.sync.register(syncTag);
          });
          
          // Show success message
          showNotification('Data saved locally. Will sync when online.');
          
          // Optional: redirect to a success page
          setTimeout(() => {
            window.location.href = '/offline-success/';
          }, 2000);
        });
      }
    });
  }
}

// Format appointment data for offline storage
function formatAppointmentData(formData) {
  return {
    id: Date.now().toString(),
    patient_id: formData.get('patient'),
    date: formData.get('date'),
    time_slot: formData.get('time_slot'),
    status: 'scheduled',
    notes: formData.get('notes') || '',
    timestamp: new Date().toISOString()
  };
}

// Format medical record data for offline storage
function formatMedicalRecordData(formData) {
  return {
    id: Date.now().toString(),
    patient_id: formData.get('patient_id'),
    diagnosis: formData.get('diagnosis'),
    treatment: formData.get('treatment'),
    prescription: formData.get('prescription'),
    notes: formData.get('notes') || '',
    timestamp: new Date().toISOString()
  };
}

// Function to save data to IndexedDB
async function saveDataLocally(data, syncTag) {
  const db = await openDatabase();
  const storeName = syncTag === 'appointment-sync' ? 'offline-appointments' : 'offline-medical-records';
  const tx = db.transaction(storeName, 'readwrite');
  await tx.objectStore(storeName).add(data);
  return tx.complete;
}

// Helper function to open database
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

// Function to show notification
function showNotification(message) {
  // Create notification element if it doesn't exist
  if (!document.querySelector('.pwa-notification')) {
    const notification = document.createElement('div');
    notification.className = 'pwa-notification fixed bottom-4 right-4 bg-blue-600 text-white py-2 px-4 rounded-lg shadow-lg z-50 transform transition-transform duration-300 translate-y-full';
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Show notification with animation
    setTimeout(() => {
      notification.classList.remove('translate-y-full');
    }, 100);
    
    // Hide after delay
    setTimeout(() => {
      notification.classList.add('translate-y-full');
      setTimeout(() => {
        if (notification.parentNode) {
          document.body.removeChild(notification);
        }
      }, 300);
    }, 3000);
  } else {
    // Update existing notification
    const notification = document.querySelector('.pwa-notification');
    notification.textContent = message;
    notification.classList.remove('translate-y-full');
    
    // Hide after delay
    setTimeout(() => {
      notification.classList.add('translate-y-full');
    }, 3000);
  }
}

// Create an offline.html file if it doesn't exist
function checkOfflinePage() {
  fetch('/offline.html')
    .then(response => {
      if (!response.ok) {
        console.warn('offline.html page not found. Consider creating one for better offline experience.');
      }
    }).catch(() => {
      console.warn('Could not verify offline.html page.');
    });
}

// Run when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  checkOfflinePage();
  
  // Check for online/offline status
  window.addEventListener('online', () => {
    showNotification('You are back online!');
  });
  
  window.addEventListener('offline', () => {
    showNotification('You are currently offline. Some features may be limited.');
  });
});