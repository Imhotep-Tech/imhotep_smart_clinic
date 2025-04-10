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
});

// Form submission handling
document.addEventListener('submit', function(e) {
    // Show loading overlay when form is submitted
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
    }
});
