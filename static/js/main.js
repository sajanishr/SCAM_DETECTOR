console.log('JS loaded');
// Main JavaScript file for ScamDetector

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form validations
    initializeFormValidations();
    
    // Initialize animations
    initializeAnimations();
    
    // Initialize API functionality
    initializeAPI();

    // Password toggle with eye icon (event delegation)
    document.addEventListener('click', function(event) {
        if (event.target.closest('.toggle-password')) {
            const btn = event.target.closest('.toggle-password');
            const targetId = btn.getAttribute('data-target');
            const input = document.getElementById(targetId);
            const icon = btn.querySelector('i');
            if (input) {
                if (input.type === 'password') {
                    input.type = 'text';
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                } else {
                    input.type = 'password';
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }
            }
        }
    });
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize form validations
function initializeFormValidations() {
    // Detection form validation
    const detectionForm = document.getElementById('detection-form');
    if (detectionForm) {
        detectionForm.addEventListener('submit', function(e) {
            const textArea = document.getElementById('detection-text');
            if (!textArea.value.trim()) {
                e.preventDefault();
                showAlert('Please enter some text to analyze.', 'warning');
                textArea.focus();
            }
        });
    }
    
    // Report form validation
    const reportForm = document.getElementById('report-form');
    if (reportForm) {
        reportForm.addEventListener('submit', function(e) {
            const descriptionField = document.getElementById('report-description');
            if (!descriptionField.value.trim()) {
                e.preventDefault();
                showAlert('Please provide a description of the scam.', 'warning');
                descriptionField.focus();
            }
        });
    }
}

// Initialize animations
function initializeAnimations() {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
    
    // Add hover effects to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

// Initialize API functionality
function initializeAPI() {
    // Real-time detection (if needed)
    const textArea = document.getElementById('detection-text');
    if (textArea) {
        let typingTimer;
        const doneTypingInterval = 2000; // 2 seconds
        
        textArea.addEventListener('input', function() {
            clearTimeout(typingTimer);
            if (this.value) {
                typingTimer = setTimeout(() => {
                    // Could implement real-time suggestions here
                }, doneTypingInterval);
            }
        });
    }
}

// Show custom alert
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of the main container
    const mainContainer = document.querySelector('main .container');
    if (mainContainer) {
        mainContainer.insertBefore(alertDiv, mainContainer.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// API functions for AJAX requests
const API = {
    // Detect text via AJAX
    detectText: async function(text) {
        try {
            const response = await fetch('/api/detect/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({ text: text })
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error:', error);
            throw error;
        }
    },
    
    // Get statistics
    getStatistics: async function(days = 7) {
        try {
            const response = await fetch(`/api/statistics/?days=${days}`);
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error:', error);
            throw error;
        }
    }
};

// Get CSRF token from cookies
function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Utility functions
const Utils = {
    // Format percentage
    formatPercentage: function(value) {
        return `${(value * 100).toFixed(1)}%`;
    },
    
    // Format date
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },
    
    // Truncate text
    truncateText: function(text, maxLength = 100) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    },
    
    // Debounce function
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Export for use in other scripts
window.ScamDetector = {
    API: API,
    Utils: Utils,
    showAlert: showAlert
};

// Mark feedback for a detection (AJAX)
window.markFeedback = function(detectionId, feedback) {
    fetch('/api/mark_feedback/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ detection_id: detectionId, feedback: feedback })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update feedback section in home result
            const feedbackSection = document.getElementById('feedback-section');
            if (feedbackSection && feedbackSection.innerHTML.includes('markFeedback')) {
                feedbackSection.innerHTML = data.feedback === 'correct'
                    ? '<span class="badge bg-success">Marked as Correct</span>'
                    : '<span class="badge bg-danger">Marked as Incorrect</span>';
            }
            // Update feedback in detection history
            const feedbackDiv = document.getElementById('feedback-' + detectionId);
            if (feedbackDiv) {
                feedbackDiv.innerHTML = data.feedback === 'correct'
                    ? '<span class="badge bg-success">Correct</span>'
                    : '<span class="badge bg-danger">Incorrect</span>';
            }
        } else {
            alert('Error: ' + (data.error || 'Could not update feedback.'));
        }
    })
    .catch(err => {
        alert('Error: ' + err);
    });
};

// Toggle password visibility by id
function togglePassword(pwdId) {
    var pwd = document.getElementById(pwdId);
    if (pwd) {
        pwd.type = pwd.type === 'password' ? 'text' : 'password';
    }
} 