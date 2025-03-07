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
    // Open the filter modal
    function openFilterModal() {
        const modal = document.getElementById('filterModal');
        modal.style.display = 'flex';
    }

    // Close the filter modal
    function closeFilterModal() {
        const modal = document.getElementById('filterModal');
        modal.style.display = 'none';
    }

    // Close the modal when clicking outside of it
    window.onclick = function (event) {
        const modal = document.getElementById('filterModal');
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    };

    document.addEventListener("DOMContentLoaded", function () {
        console.log("Registration page JavaScript loaded");
    
        // Initialize current step
        let currentStep = parseInt(document.querySelector('.custom-form-container')?.dataset?.currentStep || 1);
        showStep(currentStep);
    
        // Navigate to the next step
        document.getElementById("nextBtn")?.addEventListener("click", nextStep);
    
        // Navigate to the previous step
        document.getElementById("prevBtn")?.addEventListener("click", prevStep);
    
        // Show the current step based on `currentStep`
        function showStep(step) {
            console.log("Showing step:", step);
    
            // Hide all steps
            document.querySelectorAll(".step").forEach(stepElement => {
                stepElement.style.display = "none";
            });
    
            // Show the active step
            document.getElementById(`step-${step}`)?.style.setProperty("display", "block");
    
            // Show/hide navigation buttons
            document.getElementById("prevBtn").style.display = step > 1 ? "inline-block" : "none";
            document.getElementById("nextBtn").style.display = step < 3 ? "inline-block" : "none";
            document.getElementById("submitBtn").style.display = step === 3 ? "inline-block" : "none";
        }
    
        function nextStep() {
            if (currentStep < 3) {
                currentStep++;
                document.getElementById("current_step").value = currentStep;
                showStep(currentStep);
            }
        }
    
        function prevStep() {
            if (currentStep > 1) {
                currentStep--;
                document.getElementById("current_step").value = currentStep;
                showStep(currentStep);
            }
        }
    
        // Toggle password visibility for password fields
        function togglePassword(fieldId, iconId) {
            const passwordField = document.getElementById(fieldId);
            const eyeIcon = document.getElementById(iconId);
            if (passwordField.type === "password") {
                passwordField.type = "text";
                eyeIcon.classList.remove("fa-eye");
                eyeIcon.classList.add("fa-eye-slash");
            } else {
                passwordField.type = "password";
                eyeIcon.classList.remove("fa-eye-slash");
                eyeIcon.classList.add("fa-eye");
            }
        }
    
        // Attach password toggle handlers
        document.querySelectorAll(".toggle-password").forEach(button => {
            button.addEventListener("click", function () {
                const fieldId = this.getAttribute("data-field");
                const iconId = this.getAttribute("data-icon");
                togglePassword(fieldId, iconId);
            });
        });
    
        // Handle skill input and dynamic list rendering
        const skillsInput = document.querySelector('input[name="skills"]');
        const skillsList = document.getElementById("skills-list");
    
        if (skillsInput && skillsList) {
            skillsInput.addEventListener("input", function () {
                const skills = skillsInput.value
                    .split(",")
                    .map(skill => skill.trim())
                    .filter(skill => skill);
    
                skillsList.innerHTML = ""; // Clear previous list
                skills.forEach(skill => {
                    const li = document.createElement("li");
                    li.textContent = skill;
                    skillsList.appendChild(li);
                });
            });
        }
    });
    
    document.addEventListener("DOMContentLoaded", function () {
        // Ensure this script only runs on the settings page
        if (!document.getElementById("deleteAccountModal")) {
            console.log("⚠️ Not on the settings page. Skipping delete account script.");
            return;
        }
    
        const confirmUsernameInput = document.getElementById("confirmUsernameInput");
        const confirmDeleteButton = document.getElementById("confirmDeleteButton");
        const confirmUsernameHidden = document.getElementById("confirmUsernameHidden");
    
        // 🛑 FIX: Prevent JavaScript errors if elements are missing
        if (!confirmUsernameInput || !confirmDeleteButton || !confirmUsernameHidden) {
            console.error("⚠️ One or more required elements not found in DOM. Exiting script.");
            return;  // Stop execution if elements are missing
        }
    
        const expectedUsername = confirmDeleteButton.dataset.username.trim(); // Get username from dataset
    
        console.log("✅ Expected Username:", expectedUsername);
    
        confirmUsernameInput.addEventListener("input", function () {
            const typedUsername = confirmUsernameInput.value.trim();
            confirmUsernameHidden.value = typedUsername;
    
            console.log("Typed Username:", typedUsername);
    
            if (typedUsername === expectedUsername) {
                console.log("✅ Username matches! Enabling button...");
                confirmDeleteButton.disabled = false;
                confirmDeleteButton.style.opacity = "1";
                confirmDeleteButton.style.cursor = "pointer";
            } else {
                console.log("❌ Username does not match. Button remains disabled.");
                confirmDeleteButton.disabled = true;
                confirmDeleteButton.style.opacity = "0.5";
                confirmDeleteButton.style.cursor = "not-allowed";
            }
        });
    });
    


    