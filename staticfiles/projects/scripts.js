document.addEventListener('DOMContentLoaded', function () {
    console.log('Dropdown JS loaded'); // Debugging message

    // Get elements
    const profileTrigger = document.getElementById('uniqueProfileTrigger');
    const profileMenu = document.getElementById('uniqueProfileMenu');

    // Ensure both elements exist
    if (profileTrigger && profileMenu) {
        console.log('Profile trigger and menu found');

        // Toggle dropdown visibility on click
        profileTrigger.addEventListener('click', function (e) {
            console.log('Profile trigger clicked!'); 
            e.stopPropagation();
            profileMenu.classList.toggle('show');
          });
          

        // Close dropdown when clicking outside
        document.addEventListener('click', function (e) {
            if (!profileMenu.contains(e.target) && e.target !== profileTrigger) {
                console.log('Clicked outside dropdown');
                profileMenu.classList.remove('show'); // Correct syntax
            }
        });
    } else {
        console.error('Profile trigger or menu not found');
    }
    // Scroll to bottom of message thread on page load
    const messageThread = document.querySelector('.message-thread');
    if (messageThread) {
        messageThread.scrollTop = messageThread.scrollHeight;
    }

    // Handle delete notification
    document.querySelectorAll('.delete-notification-btn').forEach(button => {
        button.addEventListener('click', function () {
            const notificationId = button.getAttribute('data-id');
            deleteNotification(notificationId);
        });
    });

    // Function to delete a notification
    function deleteNotification(notificationId) {
        fetch(`/notification/delete/${notificationId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
        })
            .then(response => {
                if (response.ok) {
                    const notificationElement = document.getElementById(`notification-${notificationId}`);
                    if (notificationElement) notificationElement.remove();

                    const notificationCount = document.querySelector('.notification-count');
                    if (notificationCount) {
                        const currentCount = parseInt(notificationCount.textContent, 10);
                        notificationCount.textContent = Math.max(0, currentCount - 1);
                    }
                } else {
                    console.error('Failed to delete notification');
                }
            })
            .catch(error => console.error('Error:', error));
    }

    // Step navigation
    currentStep = parseInt(document.querySelector('.custom-form-container')?.dataset?.currentStep || 1);
    showStep(currentStep);

    document.getElementById('nextBtn')?.addEventListener('click', nextStep);
    document.getElementById('prevBtn')?.addEventListener('click', prevStep);

    // Show current step
    function showStep(step) {
        console.log('Showing step:', step);

        document.querySelectorAll('.step').forEach(stepElement => {
            stepElement.style.display = 'none';
        });

        const prevBtn = document.getElementById('prevBtn');
        if (prevBtn) {
          prevBtn.style.display = step > 1 ? 'inline-block' : 'none';
        }
        
    }

    function nextStep() {
        if (currentStep < 3) {
            currentStep++;
            document.getElementById('current_step').value = currentStep;
            showStep(currentStep);
        }
    }

    function prevStep() {
        if (currentStep > 1) {
            currentStep--;
            document.getElementById('current_step').value = currentStep;
            showStep(currentStep);
        }
    }

    // Initialize skill input fields
    function handleSkillInput(inputFieldId, listId, hiddenFieldId) {
        const inputField = document.getElementById(inputFieldId);
        const skillList = document.getElementById(listId);
        const hiddenField = document.getElementById(hiddenFieldId);

        if (inputField && skillList && hiddenField) {
            inputField.addEventListener('keypress', function (event) {
                if (event.key === 'Enter') {
                    event.preventDefault();

                    const skill = inputField.value.trim();
                    if (skill) {
                        const listItem = document.createElement('li');
                        listItem.textContent = skill;
                        skillList.appendChild(listItem);

                        inputField.value = '';

                        const skillsArray = hiddenField.value ? hiddenField.value.split(',') : [];
                        skillsArray.push(skill);
                        hiddenField.value = skillsArray.join(',');
                    }
                }
            });
        }
    }

    handleSkillInput('skills-gained-input', 'skills-gained-list', 'skills_gained');
    handleSkillInput('skills-requirements-input', 'skills-requirements-list', 'requirements');
});
