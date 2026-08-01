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

// Dark mode toggle functionality
function toggleTheme() {
    const themeToggleDarkIcon = document.querySelectorAll('.theme-toggle-dark-icon');
    const themeToggleLightIcon = document.querySelectorAll('.theme-toggle-light-icon');
    
    if (document.documentElement.classList.contains('dark')) {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('color-theme', 'light');
        themeToggleLightIcon.forEach(icon => icon.classList.add('hidden'));
        themeToggleDarkIcon.forEach(icon => icon.classList.remove('hidden'));
    } else {
        document.documentElement.classList.add('dark');
        localStorage.setItem('color-theme', 'dark');
        themeToggleDarkIcon.forEach(icon => icon.classList.add('hidden'));
        themeToggleLightIcon.forEach(icon => icon.classList.remove('hidden'));
    }
}

// Initialize theme icons
document.addEventListener('DOMContentLoaded', function() {
    const themeToggleDarkIcon = document.querySelectorAll('.theme-toggle-dark-icon');
    const themeToggleLightIcon = document.querySelectorAll('.theme-toggle-light-icon');
    
    if (localStorage.getItem('color-theme') === 'dark' || (!('color-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        themeToggleLightIcon.forEach(icon => icon.classList.remove('hidden'));
        themeToggleDarkIcon.forEach(icon => icon.classList.add('hidden'));
    } else {
        themeToggleDarkIcon.forEach(icon => icon.classList.remove('hidden'));
        themeToggleLightIcon.forEach(icon => icon.classList.add('hidden'));
    }
});

// ==========================================
// Toast Notification Manager (10s progress slider)
// ==========================================

function showNotification(message, type = 'info', duration = 10000) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'fixed top-5 right-5 z-50 flex flex-col space-y-3 max-w-md w-full px-4 pointer-events-none';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast-item pointer-events-auto relative overflow-hidden rounded-xl shadow-xl border-l-4 transition-all duration-300 transform translate-x-full opacity-0 glass-card p-4 flex flex-col justify-between ${getTypeClasses(type)}`;
    
    const contentWrapper = document.createElement('div');
    contentWrapper.className = 'flex items-start justify-between gap-3';
    
    const iconAndText = document.createElement('div');
    iconAndText.className = 'flex items-start gap-3';
    
    const icon = document.createElement('i');
    icon.className = getIconClass(type);
    
    const textWrapper = document.createElement('div');
    textWrapper.className = 'text-sm font-semibold text-gray-900 dark:text-gray-100 pr-2 leading-snug';
    textWrapper.innerHTML = message;
    
    iconAndText.appendChild(icon);
    iconAndText.appendChild(textWrapper);
    
    const closeBtn = document.createElement('button');
    closeBtn.type = 'button';
    closeBtn.className = 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors p-1 flex-shrink-0';
    closeBtn.ariaLabel = 'Close notification';
    closeBtn.innerHTML = '<i class="fas fa-times text-sm"></i>';
    closeBtn.onclick = () => dismissToast(toast);
    
    contentWrapper.appendChild(iconAndText);
    contentWrapper.appendChild(closeBtn);
    toast.appendChild(contentWrapper);

    // Progress slider bar container & indicator
    const progressTrack = document.createElement('div');
    progressTrack.className = 'w-full bg-slate-200/60 dark:bg-slate-700/60 h-1.5 absolute bottom-0 left-0 overflow-hidden';
    
    const progressBar = document.createElement('div');
    progressBar.className = `h-full transition-all ease-linear ${getProgressColorClass(type)}`;
    progressBar.style.width = '100%';
    progressTrack.appendChild(progressBar);
    toast.appendChild(progressTrack);

    container.appendChild(toast);

    // Enter animation
    requestAnimationFrame(() => {
        toast.classList.remove('translate-x-full', 'opacity-0');
        toast.classList.add('translate-x-0', 'opacity-100');
    });

    // 10-Second Timer & Progress Slider Animation
    let remainingTime = duration;
    let startTime = performance.now();
    let isPaused = false;

    function updateProgress(now) {
        if (!isPaused) {
            const elapsed = now - startTime;
            remainingTime -= elapsed;
            startTime = now;

            const percentage = Math.max(0, (remainingTime / duration) * 100);
            progressBar.style.width = `${percentage}%`;

            if (remainingTime <= 0) {
                dismissToast(toast);
                return;
            }
        } else {
            startTime = now;
        }
        requestAnimationFrame(updateProgress);
    }

    requestAnimationFrame((now) => {
        startTime = now;
        updateProgress(now);
    });

    // Pause on hover, resume on leave
    toast.addEventListener('mouseenter', () => {
        isPaused = true;
    });

    toast.addEventListener('mouseleave', () => {
        isPaused = false;
        startTime = performance.now();
    });
}

function dismissToast(toast) {
    if (!toast || toast.dataset.dismissed) return;
    toast.dataset.dismissed = "true";
    toast.classList.remove('translate-x-0', 'opacity-100');
    toast.classList.add('translate-x-full', 'opacity-0');
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 350);
}

function getTypeClasses(type) {
    switch (type) {
        case 'success':
            return 'bg-white dark:bg-slate-900 border-emerald-500 text-slate-800 dark:text-slate-100 shadow-emerald-500/10';
        case 'error':
        case 'danger':
            return 'bg-white dark:bg-slate-900 border-rose-500 text-slate-800 dark:text-slate-100 shadow-rose-500/10';
        case 'warning':
            return 'bg-white dark:bg-slate-900 border-amber-500 text-slate-800 dark:text-slate-100 shadow-amber-500/10';
        default:
            return 'bg-white dark:bg-slate-900 border-sky-500 text-slate-800 dark:text-slate-100 shadow-sky-500/10';
    }
}

function getIconClass(type) {
    switch (type) {
        case 'success':
            return 'fas fa-check-circle text-emerald-500 text-lg mt-0.5 flex-shrink-0';
        case 'error':
        case 'danger':
            return 'fas fa-exclamation-circle text-rose-500 text-lg mt-0.5 flex-shrink-0';
        case 'warning':
            return 'fas fa-exclamation-triangle text-amber-500 text-lg mt-0.5 flex-shrink-0';
        default:
            return 'fas fa-info-circle text-sky-500 text-lg mt-0.5 flex-shrink-0';
    }
}

function getProgressColorClass(type) {
    switch (type) {
        case 'success':
            return 'bg-emerald-500';
        case 'error':
        case 'danger':
            return 'bg-rose-500';
        case 'warning':
            return 'bg-amber-500';
        default:
            return 'bg-sky-500';
    }
}

// Make available globally
window.showNotification = showNotification;
window.createToast = showNotification;

