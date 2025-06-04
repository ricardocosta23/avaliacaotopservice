// Rating functionality
let selectedRatings = {};

// Initialize rating functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeRatingScales();
    initializeFormSubmission();
});

function initializeRatingScales() {
    // Handle all rating circles
    const ratingCircles = document.querySelectorAll('.rating-circle');

    ratingCircles.forEach(circle => {
        circle.addEventListener('click', function() {
            const value = this.getAttribute('data-value');
            const name = this.getAttribute('data-name');

            // Remove active class from siblings
            const parent = this.parentElement;
            parent.querySelectorAll('.rating-circle').forEach(sibling => {
                sibling.classList.remove('active');
                sibling.classList.remove('hover'); // Ensure hover class is also removed
                sibling.classList.remove('selected');
            });

            // Add active class to clicked circle
            this.classList.add('active');
            this.classList.add('selected');

            // Update hidden input
            const hiddenInput = document.getElementById(name.replace('_', '') + 'Rating');
            if (hiddenInput) {
                hiddenInput.value = value;
            }

            // Store rating
            selectedRatings[name] = value;

            // Clear any error messages
            const errorElement = document.getElementById(name + 'Error');
            if (errorElement) {
                errorElement.style.display = 'none';
            }
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
}

function initializeFormSubmission() {
    const form = document.getElementById('surveyForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            // Don't prevent default - let the form submit normally
            // Just validate required fields

            const overallRating = document.getElementById('overallRating');
            if (!overallRating || !overallRating.value) {
                e.preventDefault();
                const errorElement = document.getElementById('overallRatingError');
                if (errorElement) {
                    errorElement.style.display = 'block';
                }

                // Scroll to the overall rating section
                const overallSection = document.querySelector('.question-section:has(#overallRating)');
                if (overallSection) {
                    overallSection.scrollIntoView({ behavior: 'smooth' });
                }

                return false;
            }

            // If validation passes, let the form submit normally
            return true;
        });
    }
}

// Toggle conditional questions
function toggleConditionalQuestion(questionId, show) {
    const questionElement = document.getElementById(questionId);
    if (questionElement) {
        questionElement.style.display = show ? 'block' : 'none';

        // Clear ratings if hiding the question
        if (!show) {
            const ratingCircles = questionElement.querySelectorAll('.rating-circle');
            ratingCircles.forEach(circle => {
                circle.classList.remove('active');
                circle.classList.remove('hover');
                circle.classList.remove('selected');
            });

            const hiddenInputs = questionElement.querySelectorAll('input[type="hidden"]');
            hiddenInputs.forEach(input => {
                input.value = '';
            });
        }
    }
}
