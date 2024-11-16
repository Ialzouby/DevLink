// Fetch CSRF token from meta tag
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

// Register service worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/projects/service-worker.js').then(function(registration) {
            console.log('ServiceWorker registration successful with scope: ', registration.scope);
        }).catch(function(error) {
            console.log('ServiceWorker registration failed: ', error);
        });
    });
}

// Single window load event to handle all initialization
window.onload = function() {
    // Scroll to bottom of message thread on page load
    const messageThread = document.querySelector('.message-thread');
    if (messageThread) {
        messageThread.scrollTop = messageThread.scrollHeight;
    }

    // Attach delete function to notification buttons
    document.querySelectorAll(".delete-notification-btn").forEach(button => {
        button.addEventListener("click", function() {
            const notificationId = button.getAttribute("data-id");
            deleteNotification(notificationId);
        });
    });

    // Initialize the first step in multi-step form
    showStep(1);

    // Initialize skill input fields
    handleSkillInput('skills-gained-input', 'skills-gained-list', 'skills_gained');
    handleSkillInput('skills-requirements-input', 'skills-requirements-list', 'requirements');
};

// Function to delete a notification
function deleteNotification(notificationId) {
    fetch(`/notification/delete/${notificationId}/`, {
        method: "DELETE",
        headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "application/json"
        }
    })
    .then(response => {
        if (response.ok) {
            const notificationElement = document.getElementById(`notification-${notificationId}`);
            if (notificationElement) {
                notificationElement.remove();
            }
            const notificationCount = document.querySelector(".notification-count");
            if (notificationCount) {
                const currentCount = parseInt(notificationCount.textContent, 10);
                notificationCount.textContent = Math.max(0, currentCount - 1);
            }
        } else {
            console.error("Failed to delete notification");
        }
    })
    .catch(error => console.error("Error:", error));
}

// Multi-step form navigation
let currentStep = 1;

function showStep(step) {
    document.querySelectorAll('.step').forEach(stepElement => stepElement.style.display = 'none');
    document.getElementById('step-' + step).style.display = 'block';
    document.getElementById('prevBtn').style.display = (step > 1) ? 'inline' : 'none';
    document.getElementById('nextBtn').style.display = (step < 3) ? 'inline' : 'none';
    document.getElementById('submitBtn').style.display = (step === 3) ? 'inline' : 'none';
}

function nextStep() {
    if (currentStep < 3) {
        currentStep++;
        showStep(currentStep);
    }
}

function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        showStep(currentStep);
    }
}

// Handle skill input for dynamically adding skills
function handleSkillInput(inputFieldId, listId, hiddenFieldId) {
    const inputField = document.getElementById(inputFieldId);
    const skillList = document.getElementById(listId);
    const hiddenField = document.getElementById(hiddenFieldId);

    inputField.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();

            const skill = inputField.value.trim();
            if (skill) {
                const listItem = document.createElement('li');
                listItem.textContent = skill;
                skillList.appendChild(listItem);

                inputField.value = '';

                let skillsArray = hiddenField.value ? hiddenField.value.split(',') : [];
                skillsArray.push(skill);
                hiddenField.value = skillsArray.join(',');
            }
        }
    });
}

function getCookie(name) {
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

const csrftoken = getCookie('csrftoken');

// Use the csrf token in AJAX requests
fetch('/your-url/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ key: 'value' })
});
