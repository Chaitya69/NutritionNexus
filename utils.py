import os
import requests
import logging
import random
from datetime import datetime

# Nutritionix API credentials
NUTRITIONIX_APP_ID = os.environ.get("NUTRITIONIX_APP_ID", "")
NUTRITIONIX_API_KEY = os.environ.get("NUTRITIONIX_API_KEY", "")

# Base macronutrient ratios for different diet types
DIET_MACROS = {
    'omnivore': {'protein': 0.30, 'carbs': 0.45, 'fats': 0.25},
    'vegetarian': {'protein': 0.25, 'carbs': 0.50, 'fats': 0.25},
    'vegan': {'protein': 0.20, 'carbs': 0.55, 'fats': 0.25},
    'pescatarian': {'protein': 0.30, 'carbs': 0.40, 'fats': 0.30},
    'keto': {'protein': 0.25, 'carbs': 0.05, 'fats': 0.70},
    'paleo': {'protein': 0.30, 'carbs': 0.35, 'fats': 0.35},
    'gluten_free': {'protein': 0.25, 'carbs': 0.50, 'fats': 0.25},
    'mediterranean': {'protein': 0.20, 'carbs': 0.50, 'fats': 0.30}
}

# Health focus modifiers
HEALTH_FOCUS_MODIFIERS = {
    'weight_loss': {'calories': -300, 'protein': 0.05, 'carbs': -0.05, 'fats': 0},
    'muscle_gain': {'calories': 300, 'protein': 0.10, 'carbs': 0, 'fats': -0.10},
    'maintenance': {'calories': 0, 'protein': 0, 'carbs': 0, 'fats': 0},
    'heart_health': {'calories': -100, 'protein': 0, 'carbs': 0.05, 'fats': -0.05},
    'diabetes': {'calories': -200, 'protein': 0.05, 'carbs': -0.10, 'fats': 0.05},
    'energy': {'calories': 0, 'protein': 0, 'carbs': 0.10, 'fats': -0.10},
    'general': {'calories': 0, 'protein': 0, 'carbs': 0, 'fats': 0}
}

# Sample food suggestions for different diets
FOOD_SUGGESTIONS = {
    'omnivore': {
        'breakfast': ['Greek yogurt with berries and nuts', 'Scrambled eggs with vegetables and whole grain toast', 'Oatmeal with fruit and peanut butter'],
        'lunch': ['Grilled chicken salad with mixed greens', 'Turkey sandwich on whole grain bread with avocado', 'Quinoa bowl with roasted vegetables and lean protein'],
        'dinner': ['Baked salmon with roasted vegetables', 'Lean steak with sweet potato and green beans', 'Stir-fry with chicken, vegetables, and brown rice'],
        'snacks': ['Apple with almond butter', 'Hard-boiled eggs', 'Greek yogurt', 'Mixed nuts', 'Protein shake']
    },
    'vegetarian': {
        'breakfast': ['Greek yogurt with berries and nuts', 'Veggie egg scramble with whole grain toast', 'Overnight oats with fruit and seeds'],
        'lunch': ['Mediterranean salad with feta and chickpeas', 'Vegetable soup with whole grain bread', 'Hummus and veggie wrap'],
        'dinner': ['Bean and vegetable stir-fry with brown rice', 'Stuffed bell peppers with quinoa and cheese', 'Lentil curry with brown rice'],
        'snacks': ['Cottage cheese with fruit', 'Yogurt parfait', 'Trail mix', 'Hummus with vegetables', 'Cheese and whole grain crackers']
    },
    'vegan': {
        'breakfast': ['Almond milk smoothie with plant protein', 'Tofu scramble with vegetables', 'Overnight oats with plant milk and chia seeds'],
        'lunch': ['Quinoa salad with mixed vegetables and tofu', 'Lentil soup with whole grain bread', 'Chickpea and avocado wrap'],
        'dinner': ['Sweet potato and black bean bowl', 'Tempeh stir-fry with vegetables and brown rice', 'Mushroom and vegetable risotto'],
        'snacks': ['Edamame', 'Fruit with almond butter', 'Roasted chickpeas', 'Trail mix', 'Energy balls made with dates and nuts']
    },
    'pescatarian': {
        'breakfast': ['Greek yogurt with berries and granola', 'Smoked salmon with avocado toast', 'Chia seed pudding with fruit'],
        'lunch': ['Tuna salad with mixed greens', 'Salmon sushi bowl', 'Mediterranean quinoa salad with sardines'],
        'dinner': ['Grilled shrimp with roasted vegetables', 'Baked cod with sweet potato', 'Fish curry with brown rice'],
        'snacks': ['Hard-boiled eggs', 'Greek yogurt', 'Seaweed snacks', 'Fruit with nut butter', 'Mixed nuts']
    },
    'keto': {
        'breakfast': ['Avocado and bacon omelet', 'Keto pancakes with sugar-free syrup', 'Chia seed pudding with heavy cream'],
        'lunch': ['Cobb salad with ranch dressing', 'Lettuce wraps with deli meat and cheese', 'Tuna salad stuffed avocados'],
        'dinner': ['Baked salmon with asparagus', 'Zucchini noodles with meatballs', 'Cauliflower rice stir-fry with beef'],
        'snacks': ['Cheese cubes', 'Pepperoni slices', 'Boiled eggs', 'Avocado slices', 'Macadamia nuts']
    },
    'paleo': {
        'breakfast': ['Sweet potato hash with eggs', 'Banana pancakes with almond flour', 'Fruit and nut bowl'],
        'lunch': ['Grilled chicken with mixed vegetables', 'Tuna avocado lettuce wraps', 'Turkey and vegetable soup'],
        'dinner': ['Grilled steak with roasted vegetables', 'Baked salmon with asparagus', 'Stuffed bell peppers with ground turkey'],
        'snacks': ['Apple slices with almond butter', 'Beef jerky', 'Mixed nuts', 'Hard-boiled eggs', 'Sliced vegetables']
    },
    'gluten_free': {
        'breakfast': ['Gluten-free oatmeal with berries', 'Veggie and cheese omelet', 'Smoothie bowl with fruit and nuts'],
        'lunch': ['Quinoa salad with vegetables and chicken', 'Rice noodle soup with vegetables', 'Corn tortilla tacos'],
        'dinner': ['Grilled salmon with roasted vegetables', 'Gluten-free pasta with marinara sauce', 'Rice bowl with vegetables and protein'],
        'snacks': ['Rice cakes with nut butter', 'Yogurt with fruit', 'Gluten-free crackers with cheese', 'Mixed nuts', 'Fruit']
    },
    'mediterranean': {
        'breakfast': ['Greek yogurt with honey and walnuts', 'Whole grain toast with olive oil and tomatoes', 'Vegetable frittata'],
        'lunch': ['Greek salad with chickpeas', 'Tuna and white bean salad', 'Vegetable soup with whole grain bread'],
        'dinner': ['Grilled fish with roasted vegetables', 'Lentil and vegetable stew', 'Chicken souvlaki with tzatziki'],
        'snacks': ['Hummus with vegetables', 'Olives', 'A small handful of nuts', 'Fresh fruit', 'Greek yogurt']
    }
}

def calculate_bmr(user):
    """Calculate Basal Metabolic Rate using the Mifflin-St Jeor Equation"""
    if not user.weight or not user.height or not user.age or not user.gender:
        # Return default value if user profile is incomplete
        return 1800  # Default average daily caloric need
    
    if user.gender.lower() == 'male':
        bmr = (10 * user.weight) + (6.25 * user.height) - (5 * user.age) + 5
    else:  # female or other
        bmr = (10 * user.weight) + (6.25 * user.height) - (5 * user.age) - 161
    
    return bmr

def calculate_tdee(user):
    """Calculate Total Daily Energy Expenditure based on BMR and activity level"""
    bmr = calculate_bmr(user)
    
    activity_multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'extra_active': 1.9
    }
    
    multiplier = activity_multipliers.get(user.activity_level, 1.375)  # Default to lightly active
    return bmr * multiplier

def generate_nutrition_recommendation(user, diet_type, health_focus):
    """Generate personalized nutrition recommendations based on user profile and preferences"""
    # Calculate daily caloric needs
    tdee = calculate_tdee(user)
    
    # Apply health focus calorie adjustment
    adjusted_calories = tdee + HEALTH_FOCUS_MODIFIERS[health_focus]['calories']
    
    # Get base macronutrient ratios for the selected diet type
    base_macros = DIET_MACROS.get(diet_type, DIET_MACROS['omnivore'])
    
    # Apply health focus modifiers to macronutrient ratios
    adjusted_macros = {
        'protein': min(0.4, max(0.1, base_macros['protein'] + HEALTH_FOCUS_MODIFIERS[health_focus]['protein'])),
        'carbs': min(0.6, max(0.05, base_macros['carbs'] + HEALTH_FOCUS_MODIFIERS[health_focus]['carbs'])),
        'fats': min(0.7, max(0.15, base_macros['fats'] + HEALTH_FOCUS_MODIFIERS[health_focus]['fats']))
    }
    
    # Normalize ratios to sum to 1.0
    total = sum(adjusted_macros.values())
    adjusted_macros = {k: v/total for k, v in adjusted_macros.items()}
    
    # Calculate grams of each macronutrient
    protein_g = (adjusted_macros['protein'] * adjusted_calories) / 4  # 4 calories per gram of protein
    carbs_g = (adjusted_macros['carbs'] * adjusted_calories) / 4      # 4 calories per gram of carbs
    fats_g = (adjusted_macros['fats'] * adjusted_calories) / 9        # 9 calories per gram of fat
    
    # Get food suggestions based on diet type
    diet_suggestions = FOOD_SUGGESTIONS.get(diet_type, FOOD_SUGGESTIONS['omnivore'])
    
    breakfast = random.choice(diet_suggestions['breakfast'])
    lunch = random.choice(diet_suggestions['lunch'])
    dinner = random.choice(diet_suggestions['dinner'])
    snacks = ', '.join(random.sample(diet_suggestions['snacks'], 2))
    
    # Generate additional notes based on health focus
    additional_notes = ""
    if health_focus == 'weight_loss':
        additional_notes = "Focus on high-protein, high-fiber foods to help with satiety. Stay hydrated and consider eating smaller, more frequent meals."
    elif health_focus == 'muscle_gain':
        additional_notes = "Prioritize protein intake and ensure you're eating enough calories. Consider timing protein intake around workouts."
    elif health_focus == 'heart_health':
        additional_notes = "Include plenty of omega-3 fatty acids, fiber, and antioxidant-rich foods. Limit sodium and saturated fats."
    elif health_focus == 'diabetes':
        additional_notes = "Focus on low glycemic index foods and distribute carbohydrates evenly throughout the day. Monitor blood sugar regularly."
    elif health_focus == 'energy':
        additional_notes = "Include complex carbohydrates for sustained energy and ensure adequate hydration. Consider smaller, frequent meals."
    
    # Account for allergies if specified
    if user.allergies:
        additional_notes += f"\n\nNote: Please avoid {user.allergies} as per your allergy information."
    
    recommendation = {
        'daily_calories': int(adjusted_calories),
        'protein': round(protein_g, 1),
        'carbs': round(carbs_g, 1),
        'fats': round(fats_g, 1),
        'breakfast_suggestion': breakfast,
        'lunch_suggestion': lunch,
        'dinner_suggestion': dinner,
        'snacks_suggestion': snacks,
        'additional_notes': additional_notes
    }
    
    return recommendation

def get_food_nutrition(query):
    """Get nutrition information for a food item using the Nutritionix API"""
    # Store a dictionary of common foods and their nutrition values
    common_foods = {
        'apple': {
            'food_name': 'Apple',
            'calories': 95,
            'protein_g': 0.5,
            'carbs_g': 25.1,
            'fat_g': 0.3,
            'fiber_g': 4.4
        },
        'banana': {
            'food_name': 'Banana',
            'calories': 105,
            'protein_g': 1.3,
            'carbs_g': 27.0,
            'fat_g': 0.4,
            'fiber_g': 3.1
        },
        'chicken breast': {
            'food_name': 'Chicken Breast',
            'calories': 165,
            'protein_g': 31.0,
            'carbs_g': 0.0,
            'fat_g': 3.6,
            'fiber_g': 0.0
        },
        'egg': {
            'food_name': 'Egg',
            'calories': 72,
            'protein_g': 6.3,
            'carbs_g': 0.4,
            'fat_g': 5.0,
            'fiber_g': 0.0
        },
        'rice': {
            'food_name': 'Rice (cooked)',
            'calories': 130,
            'protein_g': 2.7,
            'carbs_g': 28.2,
            'fat_g': 0.3,
            'fiber_g': 0.6
        },
        'bread': {
            'food_name': 'Bread (white)',
            'calories': 75,
            'protein_g': 2.6,
            'carbs_g': 13.8,
            'fat_g': 1.0,
            'fiber_g': 0.8
        },
        'milk': {
            'food_name': 'Milk (whole)',
            'calories': 149,
            'protein_g': 7.7,
            'carbs_g': 11.7,
            'fat_g': 8.0,
            'fiber_g': 0.0
        },
        'salmon': {
            'food_name': 'Salmon',
            'calories': 208,
            'protein_g': 22.1,
            'carbs_g': 0.0,
            'fat_g': 13.4,
            'fiber_g': 0.0
        },
        'avocado': {
            'food_name': 'Avocado',
            'calories': 240,
            'protein_g': 3.0,
            'carbs_g': 12.8,
            'fat_g': 22.0,
            'fiber_g': 10.0
        },
        'broccoli': {
            'food_name': 'Broccoli',
            'calories': 55,
            'protein_g': 3.7,
            'carbs_g': 11.2,
            'fat_g': 0.6,
            'fiber_g': 5.1
        }
    }
    
    # Check if the query matches any of our common foods (case-insensitive)
    query_lower = query.lower().strip()
    for food_key, nutrition in common_foods.items():
        if food_key in query_lower or query_lower in food_key:
            return nutrition
    
    # If we don't have a match, try using the Nutritionix API if credentials are available
    if NUTRITIONIX_APP_ID and NUTRITIONIX_API_KEY:
        headers = {
            'x-app-id': NUTRITIONIX_APP_ID,
            'x-app-key': NUTRITIONIX_API_KEY,
            'x-remote-user-id': '0'
        }
        
        endpoint = "https://trackapi.nutritionix.com/v2/natural/nutrients"
        data = {
            'query': query
        }
        
        try:
            response = requests.post(endpoint, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            if 'foods' in result and len(result['foods']) > 0:
                food = result['foods'][0]
                return {
                    'food_name': food.get('food_name', query),
                    'calories': food.get('nf_calories', 0),
                    'protein_g': food.get('nf_protein', 0),
                    'carbs_g': food.get('nf_total_carbohydrate', 0),
                    'fat_g': food.get('nf_total_fat', 0),
                    'fiber_g': food.get('nf_dietary_fiber', 0)
                }
        except requests.exceptions.RequestException as e:
            logging.error(f"Error querying Nutritionix API: {str(e)}")
            # Fall through to default response
    
    # If we reach here, use a generic response based on the query
    return {
        'food_name': query.capitalize(),
        'calories': 120,  # Generic average value
        'protein_g': 4,
        'carbs_g': 18,
        'fat_g': 3,
        'fiber_g': 2,
        'note': 'Approximate values - for educational purposes only'
    }
