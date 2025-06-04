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
        // Always use direct name mapping to hidden inputs
        let hiddenInput = document.querySelector(`input[name="${name}"]`);
        
        if (hiddenInput) {
            hiddenInput.value = value;
            console.log(`Set ${name} to ${value}`);
        } else {
            console.error(`Hidden input not found for ${name}`);
            
            // Create hidden input if it doesn't exist
            hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = name;
            hiddenInput.value = value;
            selectedElement.closest('form').appendChild(hiddenInput);
            console.log(`Created and set ${name} to ${value}`);
        }

        // Update visual state for this rating group
        const groupCircles = document.querySelectorAll(`[data-name="${name}"]`);
        groupCircles.forEach(circle => {
            circle.classList.remove('selected', 'hover');
        });
        selectedElement.classList.add('selected');

        // Hide error message if exists
        const errorElement = document.getElementById(name + 'Error');
        if (errorElement) {
            errorElement.style.display = 'none';
        }
    }

    function validateForm() {
        let isValid = true;

        // Check overall rating (mandatory)
        const overallRatingInput = document.querySelector('input[name="overall_rating"]');
        const overallRating = overallRatingInput ? overallRatingInput.value : '';
        const overallError = document.getElementById('overallRatingError') || document.querySelector('.rating-error');

        console.log(`Overall rating validation: value="${overallRating}", input found: ${!!overallRatingInput}`);

        if (!overallRating || overallRating.trim() === '') {
            console.log('Overall rating validation failed - no value');
            if (overallError) {
                overallError.style.display = 'block';
                overallError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            // Create error message if it doesn't exist
            if (!overallError) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'rating-error';
                errorDiv.style.color = 'red';
                errorDiv.style.marginTop = '10px';
                errorDiv.textContent = 'Por favor, avalie a viagem de forma geral';
                const overallSection = document.querySelector('[data-name="overall_rating"]')?.closest('.question-section');
                if (overallSection) {
                    overallSection.appendChild(errorDiv);
                }
            }
            isValid = false;
        } else {
            console.log('Overall rating validation passed');
            if (overallError) {
                overallError.style.display = 'none';
            }
        }

        // Validate conditional questions - only if visible
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

    function validateConditionalRating(triggerName, ratingName) {
        const triggerYes = document.querySelector(`input[name="${triggerName}"][value="sim"]`);
        const ratingInput = document.querySelector(`input[name="${ratingName}"]`);
        
        // Get the conditional question container
        const conditionalContainer = document.getElementById(ratingName.replace('_', '-'));
        
        // Only validate if the question is visible (trigger is "sim" and container is displayed)
        if (triggerYes && triggerYes.checked && conditionalContainer && 
            conditionalContainer.style.display !== 'none' && 
            ratingInput && !ratingInput.value) {
            // Show error for conditional rating
            let errorElement = document.getElementById(ratingName + 'Error');
            if (!errorElement) {
                errorElement = document.createElement('div');
                errorElement.id = ratingName + 'Error';
                errorElement.className = 'rating-error';
                errorElement.style.color = 'red';
                errorElement.style.marginTop = '10px';
                errorElement.textContent = 'Por favor, avalie este item';
                conditionalContainer.appendChild(errorElement);
            }
            errorElement.style.display = 'block';
            errorElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
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
            // Create error message if it doesn't exist
            let errorElement = document.getElementById(ratingInputName + 'Error');
            if (!errorElement) {
                errorElement = document.createElement('div');
                errorElement.id = ratingInputName + 'Error';
                errorElement.className = 'rating-error';
                errorElement.style.color = 'red';
                errorElement.style.marginTop = '10px';
                errorElement.textContent = 'Por favor, avalie este hotel';
                hotelContainer.appendChild(errorElement);
            }
            errorElement.style.display = 'block';
            errorElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
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
            
            if (!validateForm()) {
                console.log('Form validation failed, preventing submission');
                e.preventDefault();
                return false;
            } else {
                console.log('Form validation passed, submitting...');
                showLoadingState();
                // Let the form submit naturally
                return true;
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
