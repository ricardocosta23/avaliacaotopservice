
document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const submitBtn = document.getElementById('submitBtn');
    const surveyForm = document.getElementById('surveyForm');
    const ratingCircles = document.querySelectorAll('.rating-circle');

    // Initialize rating circles
    ratingCircles.forEach(circle => {
        circle.addEventListener('click', function() {
            const value = this.getAttribute('data-value');
            const name = this.getAttribute('data-name');
            selectRating(name, value, this);
        });

        // Add hover effects
        circle.addEventListener('mouseenter', function() {
            if (!this.classList.contains('selected')) {
                this.classList.add('hover');
            }
        });

        circle.addEventListener('mouseleave', function() {
            this.classList.remove('hover');
        });

        // Make circles focusable for accessibility
        circle.setAttribute('tabindex', '0');
        circle.setAttribute('role', 'button');
        circle.setAttribute('aria-label', `Avaliar ${circle.getAttribute('data-value')} de 10`);
    });

    function selectRating(name, value, selectedElement) {
        // Find or create the hidden input
        let hiddenInput = document.querySelector(`input[name="${name}"]`);
        
        if (!hiddenInput) {
            console.log(`Creating hidden input for ${name}`);
            hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = name;
            surveyForm.appendChild(hiddenInput);
        }
        
        hiddenInput.value = value;
        console.log(`Set ${name} to ${value}`);

        // Update visual state for this rating group
        const groupCircles = document.querySelectorAll(`[data-name="${name}"]`);
        groupCircles.forEach(circle => {
            circle.classList.remove('selected', 'hover');
        });
        selectedElement.classList.add('selected');

        // Hide error message if exists
        const errorElement = document.getElementById(name + 'Error') || 
                           document.querySelector(`.rating-error[data-field="${name}"]`);
        if (errorElement) {
            errorElement.style.display = 'none';
        }
    }

    function validateForm() {
        let isValid = true;
        
        // Clear all previous errors
        document.querySelectorAll('.rating-error').forEach(error => {
            error.style.display = 'none';
        });

        // Check overall rating (mandatory)
        const overallRatingInput = document.querySelector('input[name="overall_rating"]');
        const overallRating = overallRatingInput ? overallRatingInput.value : '';

        console.log(`Overall rating validation: value="${overallRating}"`);

        if (!overallRating || overallRating.trim() === '') {
            console.log('Overall rating validation failed - no value');
            showError('overall_rating', 'Por favor, avalie a viagem de forma geral');
            isValid = false;
        }

        // Validate conditional questions - only if visible and yes is selected
        if (!validateConditionalRating('used_air_travel', 'air_rating')) {
            isValid = false;
        }
        
        // Only validate guides if the guides section exists in the DOM
        const guidesSection = document.querySelector('input[name="had_guides"]');
        if (guidesSection && !validateConditionalRating('had_guides', 'guides_rating')) {
            isValid = false;
        }
        
        if (!validateConditionalRating('had_restaurants', 'restaurants_rating')) {
            isValid = false;
        }
        if (!validateConditionalRating('had_activities', 'activities_rating')) {
            isValid = false;
        }

        // Validate hotel ratings - only if hotel containers exist and are visible
        const hotel1Input = document.querySelector('input[name="hotel_1_rating"]');
        if (hotel1Input && !validateHotelRating('hotel_1_rating')) {
            isValid = false;
        }
        
        const hotel2Input = document.querySelector('input[name="hotel_2_rating"]');
        if (hotel2Input && !validateHotelRating('hotel_2_rating')) {
            isValid = false;
        }

        return isValid;
    }

    function showError(fieldName, message) {
        // Find existing error element or create one
        let errorElement = document.getElementById(fieldName + 'Error') || 
                          document.querySelector(`.rating-error[data-field="${fieldName}"]`);
        
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'rating-error';
            errorElement.id = fieldName + 'Error';
            errorElement.setAttribute('data-field', fieldName);
            errorElement.style.color = 'red';
            errorElement.style.marginTop = '10px';
            errorElement.style.padding = '10px';
            errorElement.style.backgroundColor = 'rgba(220, 53, 69, 0.1)';
            errorElement.style.borderRadius = '5px';
            
            // Find the appropriate container to append the error
            const ratingContainer = document.querySelector(`[data-name="${fieldName}"]`)?.closest('.question-section') ||
                                  document.querySelector(`input[name="${fieldName}"]`)?.closest('.question-section');
            
            if (ratingContainer) {
                ratingContainer.appendChild(errorElement);
            } else {
                // Fallback: append to form
                surveyForm.appendChild(errorElement);
            }
        }
        
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        errorElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function validateConditionalRating(triggerName, ratingName) {
        const triggerYes = document.querySelector(`input[name="${triggerName}"][value="sim"]`);
        const ratingInput = document.querySelector(`input[name="${ratingName}"]`);
        
        // Get the conditional question container
        const conditionalContainer = document.getElementById(ratingName.replace('_', '-'));
        
        // Only validate if the question is visible (trigger is "sim" and container is displayed)
        if (triggerYes && triggerYes.checked && conditionalContainer && 
            conditionalContainer.style.display !== 'none' && 
            ratingInput && !ratingInput.value) {
            showError(ratingName, 'Por favor, avalie este item');
            return false;
        }
        return true;
    }

    function validateHotelRating(ratingInputName) {
        const ratingInput = document.querySelector(`input[name="${ratingInputName}"]`);
        const hotelContainer = ratingInput ? ratingInput.closest('.hotel-rating') : null;
        
        // Only validate if the hotel container exists, is visible, and has no rating
        if (ratingInput && hotelContainer && 
            hotelContainer.style.display !== 'none' && 
            !ratingInput.value) {
            showError(ratingInputName, 'Por favor, avalie este hotel');
            return false;
        }
        return true;
    }

    function showLoadingState() {
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
        }
    }

    // Form submission handler
    if (surveyForm) {
        surveyForm.addEventListener('submit', function(e) {
            console.log('Form submission attempted');
            
            // Get all form data for debugging
            const formData = new FormData(surveyForm);
            console.log('Form data before validation:');
            for (let [key, value] of formData.entries()) {
                console.log(`${key}: ${value}`);
            }
            
            // Always prevent default first, then decide what to do
            e.preventDefault();
            
            if (validateForm()) {
                console.log('Form validation passed, submitting...');
                showLoadingState();
                
                // Submit the form programmatically
                const form = e.target;
                
                // Create a new FormData object to ensure all data is captured
                const submitData = new FormData(form);
                
                fetch(form.action, {
                    method: 'POST',
                    body: submitData
                })
                .then(response => {
                    if (response.redirected) {
                        // Follow the redirect
                        window.location.href = response.url;
                    } else if (response.ok) {
                        // If successful but no redirect, manually redirect to thank you page
                        const surveyId = window.location.pathname.split('/')[2];
                        window.location.href = `/survey/${surveyId}/thank-you`;
                    } else {
                        throw new Error('Form submission failed');
                    }
                })
                .catch(error => {
                    console.error('Form submission error:', error);
                    alert('Erro ao enviar formulário. Tente novamente.');
                    // Reset button state
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Enviar Avaliação';
                    }
                });
            } else {
                console.log('Form validation failed');
                // Form validation failed, errors are already shown
            }
        });
    }
});

// Function to toggle conditional questions
function toggleConditionalQuestion(questionId, show) {
    const question = document.getElementById(questionId);
    if (question) {
        question.style.display = show ? 'block' : 'none';

        // Clear rating if hiding the question
        if (!show) {
            const ratingCircles = question.querySelectorAll('.rating-circle');
            ratingCircles.forEach(circle => {
                circle.classList.remove('selected');
            });

            // Clear hidden input
            const hiddenInput = question.querySelector('input[type="hidden"]');
            if (hiddenInput) {
                hiddenInput.value = '';
            }
        }
    }
}
