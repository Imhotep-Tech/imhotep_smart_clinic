// Simplified global function for sidebar toggle that will work with onclick
function handleSidebarToggle() {
    const sidebar = document.getElementById('sideNav');
    const overlay = document.getElementById('sidebarOverlay');
    
    if (!sidebar || !overlay) return;
    
    if (sidebar.classList.contains('-translate-x-full')) {
        // Open sidebar
        sidebar.classList.remove('-translate-x-full');
        overlay.classList.remove('hidden');
    } else {
        // Close sidebar
        sidebar.classList.add('-translate-x-full');
        overlay.classList.add('hidden');
    }
}

// Make sure the function is globally available
window.handleSidebarToggle = handleSidebarToggle;

// Toggle password visibility
function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    if (input.type === "password") {
        input.type = "text";
    } else {
        input.type = "password";
    }
}

// Password validation
function validatePassword() {
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm_password").value;
    
    if (password !== confirmPassword) {
        alert("Passwords do not match!");
        return false;
    }
    
    // Add additional validation rules if needed
    if (password.length < 8) {
        alert("Password must be at least 8 characters long!");
        return false;
    }
    
    return true;
}

// Handle loading state
document.addEventListener('DOMContentLoaded', function() {
    // Hide loading overlay when page is loaded
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
    }
    
    // Setup user type selection on registration form
    const userTypeSelect = document.getElementById('user_type');
    if (userTypeSelect) {
        userTypeSelect.addEventListener('change', function() {
            const doctorFields = document.getElementById('doctor_fields');
            const patientFields = document.getElementById('patient_fields');
            const specializationInput = document.getElementById('specialization');
            const dateOfBirthInput = document.getElementById('date_of_birth');
            
            // Reset required attributes
            if (specializationInput) specializationInput.required = false;
            if (dateOfBirthInput) dateOfBirthInput.required = false;
            
            // Hide all fields first
            if (doctorFields) doctorFields.classList.add('hidden');
            if (patientFields) patientFields.classList.add('hidden');
            
            // Show relevant fields based on selection
            if (this.value === 'doctor') {
                if (doctorFields) {
                    doctorFields.classList.remove('hidden');
                    if (specializationInput) specializationInput.required = true;
                }
            } else if (this.value === 'patient') {
                if (patientFields) {
                    patientFields.classList.remove('hidden');
                    if (dateOfBirthInput) dateOfBirthInput.required = true;
                }
            }
        });
    }

    // Setup footer interaction
    setupFooterInteraction();
});

// Form submission handling
document.addEventListener('submit', function(e) {
    // Show loading overlay when form is submitted
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
    }
});

// Mobile sidebar functionality 
document.addEventListener('DOMContentLoaded', function() {
    // Attach event listeners to all sidebar toggle buttons
    const toggleButtons = document.querySelectorAll('[data-action="toggle-sidebar"]');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            handleSidebarToggle();
        });
    });
    
    // Make sure mobile navigation button is visible and working
    const mobileMenuButton = document.getElementById('mobileMenuButton');
    if (mobileMenuButton) {
        // Ensure button is visible on mobile only
        if (window.innerWidth < 1024) {
            mobileMenuButton.style.display = 'block';
        } else {
            mobileMenuButton.style.display = 'none';
        }
        
        // Re-attach the click event (in case it was lost)
        const button = mobileMenuButton.querySelector('button');
        if (button) {
            button.onclick = function() {
                handleSidebarToggle();
            };
        }
    }
    
    // Ensure sidebar and overlay are properly initialized
    const sidebar = document.getElementById('sideNav');
    const overlay = document.getElementById('sidebarOverlay');
    
    if (sidebar && !sidebar.classList.contains('-translate-x-full')) {
        sidebar.classList.add('-translate-x-full');
    }
    
    if (overlay && !overlay.classList.contains('hidden')) {
        overlay.classList.add('hidden');
    }
    
    // Add window resize listener to hide button on desktop
    window.addEventListener('resize', function() {
        if (mobileMenuButton) {
            if (window.innerWidth >= 1024) {
                mobileMenuButton.style.display = 'none';
            } else {
                mobileMenuButton.style.display = 'block';
            }
        }
    });
});

// Update mobile sidebar functionality
document.addEventListener('DOMContentLoaded', function() {
    // Make sure mobile navigation button is visible on mobile only
    const mobileMenuButton = document.getElementById('mobileMenuButton');
    if (mobileMenuButton) {
        // Set initial visibility based on screen size
        mobileMenuButton.style.display = window.innerWidth < 1024 ? 'block' : 'none';
        
        // Add resize listener
        window.addEventListener('resize', function() {
            mobileMenuButton.style.display = window.innerWidth < 1024 ? 'block' : 'none';
        });
    }
    
    // Ensure sidebar starts in correct state (closed)
    const sidebar = document.getElementById('sideNav');
    const overlay = document.getElementById('sidebarOverlay');
    
    if (sidebar) {
        sidebar.classList.add('-translate-x-full');
    }
    
    if (overlay) {
        overlay.classList.add('hidden');
    }
});

// Setup footer interaction
function setupFooterInteraction() {
    // Add any footer-specific functionality here
    const footerLinks = document.querySelectorAll('footer a');
    footerLinks.forEach(link => {
        if (link.getAttribute('rel') === 'noopener noreferrer') {
            link.addEventListener('click', function(e) {
                // Optional: track outbound links
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'click', {
                        'event_category': 'outbound',
                        'event_label': link.href
                    });
                }
            });
        }
    });

    // Add PWA install prompt - Fixed version
    let deferredPrompt;
    const appVersion = document.querySelector('footer p.text-xs.text-gray-500');
    
    // Listen for the beforeinstallprompt event
    window.addEventListener('beforeinstallprompt', (e) => {
        // Prevent the mini-infobar from appearing on mobile
        e.preventDefault();
        // Stash the event so it can be triggered later
        deferredPrompt = e;
        
        // Create install button if app is installable and doesn't exist
        if (appVersion && !document.getElementById('pwa-install-btn')) {
            const installBtn = document.createElement('button');
            installBtn.id = 'pwa-install-btn';
            installBtn.className = 'ml-2 text-xs text-blue-600 hover:text-blue-800 font-medium';
            installBtn.textContent = 'Install App';
            installBtn.addEventListener('click', async () => {
                if (deferredPrompt) {
                    // Show the install prompt
                    deferredPrompt.prompt();
                    // Wait for the user to respond to the prompt
                    const { outcome } = await deferredPrompt.userChoice;
                    console.log(`User response to the install prompt: ${outcome}`);
                    // Clear the deferredPrompt variable
                    deferredPrompt = null;
                    // Hide the install button
                    installBtn.style.display = 'none';
                }
            });
            appVersion.appendChild(installBtn);
        }
    });
    
    // Handle app installation
    window.addEventListener('appinstalled', () => {
        console.log('PWA was installed');
        const installBtn = document.getElementById('pwa-install-btn');
        if (installBtn) {
            installBtn.style.display = 'none';
        }
    });
}

// Offline/online detection and read-only enforcement
function setReadOnlyMode(isOffline) {
    // Disable all forms and editing controls
    document.querySelectorAll('form, input, textarea, select, button').forEach(el => {
        if (el.tagName === 'FORM') {
            el.querySelectorAll('input, textarea, select, button').forEach(child => {
                child.disabled = isOffline;
            });
        } else {
            el.disabled = isOffline;
        }
    });
    // Show/hide offline banner
    let banner = document.getElementById('offline-banner');
    if (!banner) {
        banner = document.createElement('div');
        banner.id = 'offline-banner';
        banner.style.position = 'fixed';
        banner.style.top = '0';
        banner.style.left = '0';
        banner.style.width = '100%';
        banner.style.background = '#ff9800';
        banner.style.color = '#fff';
        banner.style.textAlign = 'center';
        banner.style.zIndex = '9999';
        banner.style.padding = '8px 0';
        banner.textContent = 'Read-only: You are offline. Editing is disabled.';
        document.body.appendChild(banner);
    }
    banner.style.display = isOffline ? 'block' : 'none';
}

window.addEventListener('online', () => setReadOnlyMode(false));
window.addEventListener('offline', () => setReadOnlyMode(true));

document.addEventListener('DOMContentLoaded', function() {
    setReadOnlyMode(!navigator.onLine);
});

// Auto-save functionality for forms
class FormAutoSave {
    constructor(formId, storageKey) {
        this.form = document.getElementById(formId);
        this.storageKey = storageKey;
        this.saveInterval = 2000; // Save every 2 seconds
        this.saveTimer = null;
        this.isDebugMode = false; // Disabled for production
        this.isUserTyping = false;
        this.typingTimer = null;
        this.typingDelay = 500; // Consider user stopped typing after 500ms
        
        if (this.form) {
            this.debug(`Initializing auto-save for form: ${formId} with key: ${storageKey}`);
            this.init();
        } else {
            this.debug(`Form not found: ${formId}`);
        }
    }
    
    debug(message) {
        if (this.isDebugMode) {
            console.log(`[AutoSave] ${message}`);
        }
    }
    
    init() {
        // Load saved data on page load
        this.loadSavedData();
        
        // Add event listeners for form changes
        this.form.addEventListener('input', (e) => {
            this.debug(`Input changed: ${e.target.name || e.target.id}`);
            this.handleUserTyping();
        });
        this.form.addEventListener('change', (e) => {
            this.debug(`Change event: ${e.target.name || e.target.id}`);
            this.handleUserTyping();
        });
        
        // Clear saved data on successful form submission
        this.form.addEventListener('submit', () => {
            this.debug('Form submitted, clearing saved data');
            this.clearSavedData();
        });
        
        // Show notification if data was restored
        if (this.hasSavedData()) {
            this.showRestoreNotification();
        }
        
        // Start auto-save interval when user is typing
        this.startAutoSaveInterval();
    }
    
    handleUserTyping() {
        this.isUserTyping = true;
        
        // Clear existing typing timer
        clearTimeout(this.typingTimer);
        
        // Set timer to detect when user stops typing
        this.typingTimer = setTimeout(() => {
            this.isUserTyping = false;
            this.debug('User stopped typing');
        }, this.typingDelay);
        
        this.debug('User is typing...');
    }
    
    startAutoSaveInterval() {
        // Auto-save every 2 seconds, but only if user has been typing
        setInterval(() => {
            if (this.isUserTyping) {
                this.saveFormData();
            }
        }, this.saveInterval);
    }
    
    scheduleAutoSave() {
        // This method is kept for compatibility but not used in production
        clearTimeout(this.saveTimer);
        this.saveTimer = setTimeout(() => {
            this.saveFormData();
        }, this.saveInterval);
    }
    
    saveFormData() {
        // Clear previous auto-save data first to save memory
        this.clearPreviousAutoSave();
        
        const formData = {};
        const formElements = this.form.querySelectorAll('input, textarea, select');
        
        this.debug(`Saving form data for ${formElements.length} elements`);
        
        formElements.forEach(element => {
            const name = element.name || element.id;
            if (!name) return;
            
            if (element.type === 'checkbox' || element.type === 'radio') {
                formData[name] = element.checked;
            } else if (element.type !== 'submit' && element.type !== 'button' && element.type !== 'hidden') {
                formData[name] = element.value;
            }
        });
        
        // Handle Quill editors separately if they exist
        this.saveQuillEditors(formData);
        
        // Add timestamp for tracking
        formData['_autosave_timestamp'] = Date.now();
        
        const dataToSave = JSON.stringify(formData);
        localStorage.setItem(this.storageKey, dataToSave);
        this.debug(`Data saved: ${dataToSave.substring(0, 100)}...`);
        this.showAutoSaveIndicator();
    }
    
    clearPreviousAutoSave() {
        // Remove any existing auto-save data for this form to prevent memory buildup
        const existingData = localStorage.getItem(this.storageKey);
        if (existingData) {
            this.debug('Clearing previous auto-save data');
            localStorage.removeItem(this.storageKey);
        }
    }
    
    saveQuillEditors(formData) {
        // Save Quill editor content if present
        if (window.detailsEditor) {
            formData['details_quill'] = window.detailsEditor.root.innerHTML;
            this.debug('Saved details editor content');
        }
        if (window.prescriptionEditor) {
            formData['prescription_quill'] = window.prescriptionEditor.root.innerHTML;
            this.debug('Saved prescription editor content');
        }
    }
    
    loadSavedData() {
        const savedData = localStorage.getItem(this.storageKey);
        if (!savedData) {
            this.debug('No saved data found');
            return;
        }
        
        this.debug(`Loading saved data: ${savedData.substring(0, 100)}...`);
        
        try {
            const formData = JSON.parse(savedData);
            const formElements = this.form.querySelectorAll('input, textarea, select');
            
            let restoredCount = 0;
            formElements.forEach(element => {
                const name = element.name || element.id;
                if (formData.hasOwnProperty(name)) {
                    if (element.type === 'checkbox' || element.type === 'radio') {
                        element.checked = formData[name];
                    } else if (element.type !== 'submit' && element.type !== 'button' && element.type !== 'hidden') {
                        element.value = formData[name];
                    }
                    restoredCount++;
                }
            });
            
            this.debug(`Restored ${restoredCount} form fields`);
            
            // Load Quill editor content after a delay to ensure editors are initialized
            setTimeout(() => {
                this.loadQuillEditors(formData);
            }, 1000);
            
            // Add visual indication that data was restored
            this.form.classList.add('form-restored');
            setTimeout(() => {
                this.form.classList.remove('form-restored');
            }, 3000);
            
        } catch (error) {
            this.debug(`Error loading saved form data: ${error.message}`);
            console.error('Error loading saved form data:', error);
            // Clear corrupted data
            localStorage.removeItem(this.storageKey);
        }
    }
    
    loadQuillEditors(formData) {
        if (window.detailsEditor && formData['details_quill']) {
            window.detailsEditor.root.innerHTML = formData['details_quill'];
            this.debug('Restored details editor content');
        }
        if (window.prescriptionEditor && formData['prescription_quill']) {
            window.prescriptionEditor.root.innerHTML = formData['prescription_quill'];
            this.debug('Restored prescription editor content');
        }
    }
    
    hasSavedData() {
        const savedData = localStorage.getItem(this.storageKey);
        return savedData !== null && savedData !== '{}';
    }
    
    clearSavedData() {
        localStorage.removeItem(this.storageKey);
        this.debug('Saved data cleared');
        this.hideAutoSaveIndicator();
    }
    
    showAutoSaveIndicator() {
        let indicator = document.getElementById('autosave-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'autosave-indicator';
            indicator.className = 'fixed top-4 right-4 bg-green-500 text-white px-3 py-1 rounded-md text-sm z-50 transition-opacity duration-300';
            indicator.innerHTML = '✓ Auto-saved';
            document.body.appendChild(indicator);
        }
        
        indicator.style.opacity = '1';
        setTimeout(() => {
            if (indicator) {
                indicator.style.opacity = '0';
            }
        }, 1500); // Shorter display time for production
    }
    
    hideAutoSaveIndicator() {
        const indicator = document.getElementById('autosave-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    showRestoreNotification() {
        const savedData = localStorage.getItem(this.storageKey);
        let timestamp = 'recently';
        
        try {
            const formData = JSON.parse(savedData);
            if (formData['_autosave_timestamp']) {
                timestamp = new Date(formData['_autosave_timestamp']).toLocaleTimeString();
            }
        } catch (e) {
            // Use default timestamp
        }
        
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 left-1/2 transform -translate-x-1/2 bg-blue-500 text-white px-4 py-2 rounded-md z-50 flex items-center';
        notification.innerHTML = `
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            Unsaved data restored from ${timestamp}
            <button onclick="this.parentElement.remove()" class="ml-2 text-white hover:text-gray-200">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 4000);
    }
}

// Initialize auto-save for different forms when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit to ensure all elements are loaded
    setTimeout(() => {
        // Initialize auto-save for different forms
        const currentPath = window.location.pathname;
        
        console.log('[AutoSave] Current path:', currentPath);
        
        if (currentPath.includes('add_patient') || currentPath.includes('add-patient')) {
            console.log('[AutoSave] Initializing for add_patient form');
            new FormAutoSave('addPatientForm', 'autosave_add_patient');
        } else if (currentPath.includes('edit_patient') || currentPath.includes('edit-patient')) {
            const patientId = new URLSearchParams(window.location.search).get('patient_id');
            console.log('[AutoSave] Initializing for edit_patient form, patient ID:', patientId);
            new FormAutoSave('editPatientForm', `autosave_edit_patient_${patientId}`);
        } else if (currentPath.includes('add_medical_record') || currentPath.includes('add-medical-record')) {
            const patientId = new URLSearchParams(window.location.search).get('patient_id');
            console.log('[AutoSave] Initializing for add_medical_record form, patient ID:', patientId);
            new FormAutoSave('medicalRecordForm', `autosave_add_record_${patientId}`);
        } else if (currentPath.includes('edit_medical_record') || currentPath.includes('edit-medical-record')) {
            const recordId = new URLSearchParams(window.location.search).get('medical_record_id');
            console.log('[AutoSave] Initializing for edit_medical_record form, record ID:', recordId);
            new FormAutoSave('editMedicalRecordForm', `autosave_edit_record_${recordId}`);
        }
    }, 500);
});
