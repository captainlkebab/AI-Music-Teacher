document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const learningPlanForm = document.getElementById('learningPlanForm');
    const planResult = document.getElementById('planResult');
    
    console.log('DOM loaded for learning-plan.js');
    console.log('Learning plan form found:', learningPlanForm ? 'Yes' : 'No');
    
    // Initialize learning plan form if it exists
    if (learningPlanForm) {
        console.log('Learning plan form found and event listener attached');
        
        learningPlanForm.addEventListener('submit', function(e) {
            // Make sure to prevent default at the beginning
            e.preventDefault();
            
            // Add this console log to verify the handler is being called
            console.log('Learning plan form submitted');
            
            // Get form data
            const formData = new FormData(learningPlanForm);
            const planData = {};
            
            // Convert FormData to JSON
            for (const [key, value] of formData.entries()) {
                planData[key] = value;
                console.log(`Form data: ${key} = ${value}`);
            }
            
            // Get selected goals
            const goalCheckboxes = document.querySelectorAll('input[name="goals"]:checked');
            planData.goals = Array.from(goalCheckboxes).map(cb => cb.value);
            console.log('Selected goals:', planData.goals);
            
            // Show loading indicator
            planResult.innerHTML = '<div class="spinner-border text-primary" role="status"></div> Generating your learning plan...';
            
            // Send request to server
            console.log('Sending request to /generate-plan');
            fetch('/generate-plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(planData)
            })
            .then(response => {
                console.log('Response status:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data);
                if (data.error) {
                    planResult.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                } else {
                    // Display the learning plan
                    planResult.innerHTML = `
                        <div class="card">
                            <div class="card-header bg-success text-white">
                                <h3 class="card-title">Your Personalized Learning Plan</h3>
                            </div>
                            <div class="card-body">
                                ${data.plan}
                            </div>
                        </div>
                    `;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                planResult.innerHTML = `<div class="alert alert-danger">Sorry, there was an error generating your learning plan.</div>`;
            });
        });
    } else {
        console.error('Learning plan form not found');
    }
});