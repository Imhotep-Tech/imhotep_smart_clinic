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

    // Add PWA install prompt
    const appVersion = document.querySelector('footer p.text-xs.text-gray-500');
    if (appVersion && window.matchMedia('(display-mode: browser)').matches) {
        // Check if app is installable
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            const installPrompt = e;
            
            // Create install button if doesn't exist
            if (!document.getElementById('pwa-install-btn')) {
                const installBtn = document.createElement('button');
                installBtn.id = 'pwa-install-btn';
                installBtn.className = 'ml-2 text-xs text-blue-600 hover:text-blue-800 font-medium';
                installBtn.textContent = 'Install App';
                installBtn.addEventListener('click', () => {
                    installPrompt.prompt();
                    installPrompt.userChoice.then(choiceResult => {
                        if (choiceResult.outcome === 'accepted') {
                            console.log('User accepted the install prompt');
                        }
                    });
                });
                appVersion.appendChild(installBtn);
            }
        });
    }
}
