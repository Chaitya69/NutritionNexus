/**
 * Nutrition Awareness and Recommendation System
 * Main JavaScript File
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize popovers and tooltips (Bootstrap)
    initializeBootstrapComponents();
    
    // Handle form validation
    setupFormValidation();
    
    // Handle nutrition recommendations
    setupNutritionRecommendations();
    
    // Initialize any charts if present
    initializeCharts();
    
    // Setup responsive behavior
    setupResponsiveBehavior();
});

/**
 * Initialize Bootstrap components like popovers and tooltips
 */
function initializeBootstrapComponents() {
    // Initialize all popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize all toasts
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.map(function (toastEl) {
        return new bootstrap.Toast(toastEl);
    });
}

/**
 * Setup form validation for all forms
 */
function setupFormValidation() {
    // Get all forms with the class 'needs-validation'
    const forms = document.querySelectorAll('.needs-validation');
    
    // Loop over them and prevent submission if validation fails
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Setup nutrition recommendation functionalities
 */
function setupNutritionRecommendations() {
    // Setup food search functionality if the element exists
    const foodSearchForm = document.getElementById('food-search-form');
    if (foodSearchForm) {
        foodSearchForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const foodQuery = document.getElementById('food-query').value.trim();
            if (!foodQuery) return;
            
            try {
                // Show loading state
                document.getElementById('food-search-results').innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
                
                // Make API request to get nutrition data
                const response = await fetch(`/api/food_nutrition?query=${encodeURIComponent(foodQuery)}`);
                const data = await response.json();
                
                if (data.error) {
                    document.getElementById('food-search-results').innerHTML = `
                        <div class="alert alert-warning" role="alert">
                            ${data.error}
                        </div>
                    `;
                    return;
                }
                
                // Display nutrition information
                document.getElementById('food-search-results').innerHTML = `
                    <div class="card">
                        <div class="card-header bg-primary text-white">
                            Nutrition Information for ${data.food_name}
                        </div>
                        <div class="card-body">
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item d-flex justify-content-between align-items-center">
                                    Calories
                                    <span class="badge bg-primary rounded-pill">${data.calories}</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between align-items-center">
                                    Protein
                                    <span class="badge bg-success rounded-pill">${data.protein_g}g</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between align-items-center">
                                    Carbohydrates
                                    <span class="badge bg-info rounded-pill">${data.carbs_g}g</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between align-items-center">
                                    Fat
                                    <span class="badge bg-warning rounded-pill">${data.fat_g}g</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between align-items-center">
                                    Fiber
                                    <span class="badge bg-secondary rounded-pill">${data.fiber_g}g</span>
                                </li>
                            </ul>
                        </div>
                    </div>
                `;
            } catch (error) {
                console.error('Error fetching nutrition data:', error);
                document.getElementById('food-search-results').innerHTML = `
                    <div class="alert alert-danger" role="alert">
                        Failed to retrieve nutrition information. Please try again later.
                    </div>
                `;
            }
        });
    }
    
    // Setup diet type selection to update the form
    const dietTypeSelect = document.getElementById('diet_type');
    if (dietTypeSelect) {
        dietTypeSelect.addEventListener('change', function() {
            updateDietRecommendationInfo(this.value);
        });
    }
}

/**
 * Update the diet recommendation information based on selected diet type
 */
function updateDietRecommendationInfo(dietType) {
    const dietInfoDiv = document.getElementById('diet-info');
    if (!dietInfoDiv) return;
    
    const dietInfo = {
        'omnivore': {
            title: 'Omnivore Diet',
            description: 'An omnivore diet includes both plant and animal foods. It provides a wide range of nutrients and is the most common type of diet worldwide.',
            benefits: ['Wide variety of food choices', 'Easy to meet nutritional needs', 'Flexibility in meal planning', 'Rich in complete proteins']
        },
        'vegetarian': {
            title: 'Vegetarian Diet',
            description: 'A vegetarian diet excludes meat, poultry, and seafood but may include dairy and eggs. It focuses on plant-based foods like fruits, vegetables, legumes, nuts, and grains.',
            benefits: ['Lower risk of heart disease', 'Lower cholesterol levels', 'May help with weight management', 'Rich in antioxidants and fiber']
        },
        'vegan': {
            title: 'Vegan Diet',
            description: 'A vegan diet excludes all animal products including meat, dairy, eggs, and honey. It consists entirely of plant-based foods.',
            benefits: ['Lowest environmental impact', 'May reduce risk of certain diseases', 'Typically high in fiber', 'Often lower in saturated fat']
        },
        'pescatarian': {
            title: 'Pescatarian Diet',
            description: 'A pescatarian diet includes fish and seafood but excludes other animal meats. It combines the benefits of a plant-based diet with the nutritional advantages of fish.',
            benefits: ['Rich in omega-3 fatty acids', 'Good source of lean protein', 'May reduce risk of heart disease', 'Provides essential nutrients like vitamin B12 and D']
        },
        'keto': {
            title: 'Ketogenic Diet',
            description: 'A ketogenic diet is very low in carbohydrates and high in fats. It aims to put your body into a metabolic state called ketosis where it burns fat for energy instead of carbs.',
            benefits: ['May aid weight loss', 'Potentially reduces appetite', 'May improve certain health markers', 'Can help manage specific medical conditions']
        },
        'paleo': {
            title: 'Paleo Diet',
            description: 'The paleo diet is based on foods that would have been available to our Paleolithic ancestors, including lean meats, fish, fruits, vegetables, nuts, and seeds.',
            benefits: ['Eliminates processed foods', 'High in protein and fiber', 'Can help with weight management', 'May improve blood lipids']
        },
        'gluten_free': {
            title: 'Gluten-Free Diet',
            description: 'A gluten-free diet excludes the protein gluten, found in grains such as wheat, barley, and rye. It\'s essential for people with celiac disease or gluten sensitivity.',
            benefits: ['Necessary for celiac disease management', 'May reduce inflammation for sensitive individuals', 'Can improve digestive symptoms', 'Often leads to more whole food choices']
        },
        'mediterranean': {
            title: 'Mediterranean Diet',
            description: 'The Mediterranean diet is based on the traditional foods eaten in countries bordering the Mediterranean Sea. It\'s rich in fruits, vegetables, whole grains, olive oil, and fish.',
            benefits: ['Associated with longevity', 'Reduces risk of heart disease', 'May improve brain health', 'Balanced and sustainable approach']
        }
    };
    
    const selectedDiet = dietInfo[dietType] || dietInfo['omnivore'];
    
    // Update diet information section
    dietInfoDiv.innerHTML = `
        <div class="card mb-4">
            <div class="card-header bg-success text-white">
                <h5 class="mb-0">${selectedDiet.title}</h5>
            </div>
            <div class="card-body">
                <p>${selectedDiet.description}</p>
                <h6 class="text-success">Key Benefits:</h6>
                <ul>
                    ${selectedDiet.benefits.map(benefit => `<li>${benefit}</li>`).join('')}
                </ul>
            </div>
        </div>
    `;
}

/**
 * Initialize charts for nutrition visualization if present on the page
 */
function initializeCharts() {
    // Check if we have a macro distribution chart element
    const macroChartEl = document.getElementById('macro-distribution-chart');
    if (macroChartEl) {
        // Get macro values from data attributes or default to example values
        const proteinValue = parseFloat(macroChartEl.dataset.protein || 30);
        const carbsValue = parseFloat(macroChartEl.dataset.carbs || 45);
        const fatsValue = parseFloat(macroChartEl.dataset.fats || 25);
        
        // Create macro distribution pie chart
        const macroChart = new Chart(macroChartEl, {
            type: 'pie',
            data: {
                labels: ['Protein', 'Carbohydrates', 'Fats'],
                datasets: [{
                    data: [proteinValue, carbsValue, fatsValue],
                    backgroundColor: [
                        '#2c7da0', // Blue for protein
                        '#2a9d8f', // Green for carbs
                        '#468faf'  // Light blue for fats
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.label}: ${context.raw}%`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Check if we have a calories chart element
    const caloriesChartEl = document.getElementById('calories-chart');
    if (caloriesChartEl) {
        // Create calorie distribution chart (if data exists)
        // Implementation would depend on the specific data available
    }
}

/**
 * Setup responsive behavior for the application
 */
function setupResponsiveBehavior() {
    // Handle navbar toggler for mobile view
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            document.querySelector('.navbar-collapse').classList.toggle('show');
        });
    }
    
    // Handle sidebar toggling on smaller screens if sidebar exists
    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.getElementById('sidebar').classList.toggle('active');
        });
    }
}

/**
 * Format a number with commas for thousands
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Show flash message
 */
function flashMessage(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Append to the flash-container if it exists, otherwise to the body
    const container = document.getElementById('flash-container') || document.body;
    container.prepend(alertDiv);
    
    // Auto-close after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 5000);
}
