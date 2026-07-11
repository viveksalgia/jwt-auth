/**
 * Validation and Utility Functions for Authentication Forms
 */

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} - Whether email is valid
 */
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate password strength
 * @param {string} password - Password to validate
 * @returns {boolean} - Whether password meets minimum requirements
 */
function validatePassword(password) {
    if (password.length < 8) {
        return false;
    }
    // Should contain at least one uppercase, one lowercase, and one number
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    
    return hasUpperCase || hasLowerCase || hasNumber;
}

/**
 * Validate name format
 * @param {string} name - Name to validate
 * @returns {boolean} - Whether name is valid
 */
function validateName(name) {
    const nameRegex = /^[a-zA-Z\s'-]+$/;
    return name.trim().length > 0 && nameRegex.test(name);
}

/**
 * Check if passwords match
 * @param {string} password - First password
 * @param {string} confirmPassword - Confirmation password
 * @returns {boolean} - Whether passwords match
 */
function passwordsMatch(password, confirmPassword) {
    return password === confirmPassword && password.length > 0;
}

/**
 * Show error message in a specific field
 * @param {string} fieldId - ID of the input field
 * @param {string} errorMessage - Error message to display
 */
function showFieldError(fieldId, errorMessage) {
    const errorElement = document.getElementById(fieldId + 'Error');
    if (errorElement) {
        errorElement.textContent = errorMessage;
    }
}

/**
 * Clear error message for a field
 * @param {string} fieldId - ID of the input field
 */
function clearFieldError(fieldId) {
    const errorElement = document.getElementById(fieldId + 'Error');
    if (errorElement) {
        errorElement.textContent = '';
    }
}

/**
 * Clear all error messages in the form
 */
function clearAllErrors() {
    const errorElements = document.querySelectorAll('.error-message');
    errorElements.forEach(element => {
        element.textContent = '';
    });
}

/**
 * Show success message
 * @param {string} message - Success message
 */
function showSuccessMessage(message) {
    const successElement = document.getElementById('successMessage');
    if (successElement) {
        successElement.textContent = message;
        successElement.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            successElement.style.display = 'none';
        }, 5000);
    }
}

/**
 * Show error message
 * @param {string} message - Error message
 */
function showErrorMessage(message) {
    const errorElement = document.getElementById('errorMessage');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorElement.style.display = 'none';
        }, 5000);
    }
}

/**
 * Disable button and show loading state
 * @param {string} buttonId - ID of the button
 * @param {string} originalText - Original button text (for restoration)
 */
function disableButton(buttonId, originalText = 'Loading...') {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = true;
        button.dataset.originalText = button.textContent;
        button.textContent = originalText;
    }
}

/**
 * Enable button and restore original state
 * @param {string} buttonId - ID of the button
 */
function enableButton(buttonId) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = false;
        button.textContent = button.dataset.originalText || 'Submit';
    }
}

/**
 * Add real-time validation to an input field
 * @param {string} fieldId - ID of the input field
 * @param {Function} validationFn - Validation function that returns boolean
 * @param {string} errorMessage - Error message to show
 */
function addRealTimeValidation(fieldId, validationFn, errorMessage) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    field.addEventListener('blur', function() {
        if (this.value.trim() && !validationFn(this.value)) {
            showFieldError(fieldId, errorMessage);
        } else {
            clearFieldError(fieldId);
        }
    });

    field.addEventListener('input', function() {
        if (this.value.trim() && validationFn(this.value)) {
            clearFieldError(fieldId);
        }
    });
}

/**
 * Sanitize input to prevent XSS
 * @param {string} input - Input to sanitize
 * @returns {string} - Sanitized input
 */
function sanitizeInput(input) {
    const div = document.createElement('div');
    div.textContent = input;
    return div.innerHTML;
}

/**
 * Format and mask sensitive data
 * @param {string} value - Value to mask
 * @param {number} visibleChars - Number of visible characters from the end
 * @returns {string} - Masked value
 */
function maskSensitiveData(value, visibleChars = 4) {
    if (value.length <= visibleChars) return value;
    return '*'.repeat(value.length - visibleChars) + value.slice(-visibleChars);
}

/**
 * Check if form is valid by checking all required fields
 * @param {string} formId - ID of the form
 * @returns {boolean} - Whether form is valid
 */
function isFormValid(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;

    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('has-error');
        } else {
            field.classList.remove('has-error');
        }
    });

    return isValid;
}

/**
 * Track form changes for unsaved data warning
 * @param {string} formId - ID of the form
 */
function trackFormChanges(formId) {
    const form = document.getElementById(formId);
    if (!form) return;

    let hasChanges = false;

    form.addEventListener('change', () => {
        hasChanges = true;
    });

    form.addEventListener('submit', () => {
        hasChanges = false;
    });

    window.addEventListener('beforeunload', (e) => {
        if (hasChanges) {
            e.preventDefault();
            e.returnValue = '';
            return '';
        }
    });
}

/**
 * Initialize all real-time validations for login form
 */
function initializeLoginValidation() {
    addRealTimeValidation('username', 
        (value) => value.trim().length > 0,
        'Username is required'
    );

    addRealTimeValidation('password',
        (value) => value.length > 0,
        'Password is required'
    );
}

/**
 * Initialize all real-time validations for signup form
 */
function initializeSignupValidation() {
    addRealTimeValidation('firstName',
        (value) => validateName(value),
        'Enter a valid first name'
    );

    addRealTimeValidation('lastName',
        (value) => validateName(value),
        'Enter a valid last name'
    );

    addRealTimeValidation('email',
        (value) => validateEmail(value),
        'Enter a valid email address'
    );

    addRealTimeValidation('password',
        (value) => value.length >= 8,
        'Password must be at least 8 characters'
    );

    addRealTimeValidation('confirmPassword',
        (value) => value.length > 0,
        'Please verify your password'
    );

    // Check password match on blur
    const confirmPassword = document.getElementById('confirmPassword');
    if (confirmPassword) {
        confirmPassword.addEventListener('blur', function() {
            const password = document.getElementById('password').value;
            if (this.value && !passwordsMatch(password, this.value)) {
                showFieldError('confirmPassword', 'Passwords do not match');
            } else {
                clearFieldError('confirmPassword');
            }
        });
    }
}

/**
 * Request OTP (One Time Password) for email verification
 * @param {string} email - Email to send OTP to
 */
async function requestOTP(email) {
    try {
        const response = await fetch('/api/request-otp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email }),
        });

        if (response.ok) {
            showSuccessMessage('OTP sent to your email');
            return true;
        } else {
            showErrorMessage('Failed to send OTP. Please try again.');
            return false;
        }
    } catch (error) {
        console.error('Error requesting OTP:', error);
        showErrorMessage('An error occurred. Please try again.');
        return false;
    }
}

/**
 * Verify OTP
 * @param {string} email - Email address
 * @param {string} otp - OTP code
 */
async function verifyOTP(email, otp) {
    try {
        const response = await fetch('/api/verify-otp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, otp }),
        });

        if (response.ok) {
            showSuccessMessage('Email verified successfully');
            return true;
        } else {
            showErrorMessage('Invalid OTP. Please try again.');
            return false;
        }
    } catch (error) {
        console.error('Error verifying OTP:', error);
        showErrorMessage('An error occurred. Please try again.');
        return false;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check which form is on the page and initialize accordingly
    if (document.getElementById('loginForm')) {
        initializeLoginValidation();
        trackFormChanges('loginForm');
    }

    if (document.getElementById('signupForm')) {
        initializeSignupValidation();
        trackFormChanges('signupForm');
    }
});
