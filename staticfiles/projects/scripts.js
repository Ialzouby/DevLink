document.addEventListener('DOMContentLoaded', function() {
    let currentStep = 1;  // Declare once

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
    function showStep(step) {
        // Hide all steps
        document.querySelectorAll('.step').forEach(stepElement => {
            if (stepElement) {
                stepElement.style.display = 'none';
            }
        });

        // Show the current step
        const stepElement = document.getElementById('step-' + step);
        if (stepElement) {
            stepElement.style.display = 'block';
        }

        // Update button visibility with checks
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const submitBtn = document.getElementById('submitBtn');

        if (prevBtn) {
            prevBtn.style.display = (step > 1) ? 'inline' : 'none';
        }
        if (nextBtn) {
            nextBtn.style.display = (step < 3) ? 'inline' : 'none';
        }
        if (submitBtn) {
            submitBtn.style.display = (step === 3) ? 'inline' : 'none';
        }
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

    // Call showStep for the initial step
    showStep(currentStep);

    // Handle skill input for dynamically adding skills
    function handleSkillInput(inputFieldId, listId, hiddenFieldId) {
        const inputField = document.getElementById(inputFieldId);
        const skillList = document.getElementById(listId);
        const hiddenField = document.getElementById(hiddenFieldId);

        if (inputField && skillList && hiddenField) {
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
    }

    // Initialize skill input fields
    handleSkillInput('skills-gained-input', 'skills-gained-list', 'skills_gained');
    handleSkillInput('skills-requirements-input', 'skills-requirements-list', 'requirements');
});
