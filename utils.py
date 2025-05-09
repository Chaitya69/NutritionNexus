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
    """Get nutrition information for a food item using an extensive database of common foods"""
    # Store a dictionary of common foods and their accurate nutrition values (per 100g unless specified)
    common_foods = {
        # Fruits
        'apple': {
            'food_name': 'Apple (1 medium)',
            'calories': 95,
            'protein_g': 0.5,
            'carbs_g': 25.1,
            'fat_g': 0.3,
            'fiber_g': 4.4
        },
        'banana': {
            'food_name': 'Banana (1 medium)',
            'calories': 105,
            'protein_g': 1.3,
            'carbs_g': 27.0,
            'fat_g': 0.4,
            'fiber_g': 3.1
        },
        'orange': {
            'food_name': 'Orange (1 medium)',
            'calories': 62,
            'protein_g': 1.2,
            'carbs_g': 15.4,
            'fat_g': 0.2,
            'fiber_g': 3.1
        },
        'strawberry': {
            'food_name': 'Strawberries (1 cup)',
            'calories': 49,
            'protein_g': 1.0,
            'carbs_g': 11.7,
            'fat_g': 0.5,
            'fiber_g': 3.0
        },
        'blueberry': {
            'food_name': 'Blueberries (1 cup)',
            'calories': 84,
            'protein_g': 1.1,
            'carbs_g': 21.5,
            'fat_g': 0.5,
            'fiber_g': 3.6
        },
        'grape': {
            'food_name': 'Grapes (1 cup)',
            'calories': 104,
            'protein_g': 1.1,
            'carbs_g': 27.3,
            'fat_g': 0.2,
            'fiber_g': 1.4
        },
        'watermelon': {
            'food_name': 'Watermelon (1 cup, diced)',
            'calories': 46,
            'protein_g': 0.9,
            'carbs_g': 11.5,
            'fat_g': 0.2,
            'fiber_g': 0.6
        },
        'pineapple': {
            'food_name': 'Pineapple (1 cup, chunks)',
            'calories': 82,
            'protein_g': 0.9,
            'carbs_g': 21.6,
            'fat_g': 0.2,
            'fiber_g': 2.3
        },
        'mango': {
            'food_name': 'Mango (1 cup, sliced)',
            'calories': 99,
            'protein_g': 1.4,
            'carbs_g': 24.7,
            'fat_g': 0.6,
            'fiber_g': 2.6
        },
        'avocado': {
            'food_name': 'Avocado (1/2 fruit)',
            'calories': 160,
            'protein_g': 2.0,
            'carbs_g': 8.5,
            'fat_g': 14.7,
            'fiber_g': 6.7
        },
        
        # Vegetables
        'broccoli': {
            'food_name': 'Broccoli (1 cup, chopped)',
            'calories': 55,
            'protein_g': 3.7,
            'carbs_g': 11.2,
            'fat_g': 0.6,
            'fiber_g': 5.1
        },
        'spinach': {
            'food_name': 'Spinach (1 cup, raw)',
            'calories': 7,
            'protein_g': 0.9,
            'carbs_g': 1.1,
            'fat_g': 0.1,
            'fiber_g': 0.7
        },
        'kale': {
            'food_name': 'Kale (1 cup, chopped)',
            'calories': 33,
            'protein_g': 2.9,
            'carbs_g': 6.7,
            'fat_g': 0.5,
            'fiber_g': 1.3
        },
        'carrot': {
            'food_name': 'Carrot (1 medium)',
            'calories': 25,
            'protein_g': 0.6,
            'carbs_g': 5.8,
            'fat_g': 0.1,
            'fiber_g': 1.7
        },
        'bell pepper': {
            'food_name': 'Bell Pepper (1 medium)',
            'calories': 30,
            'protein_g': 1.0,
            'carbs_g': 7.0,
            'fat_g': 0.2,
            'fiber_g': 2.5
        },
        'onion': {
            'food_name': 'Onion (1 medium)',
            'calories': 44,
            'protein_g': 1.2,
            'carbs_g': 10.3,
            'fat_g': 0.1,
            'fiber_g': 1.9
        },
        'tomato': {
            'food_name': 'Tomato (1 medium)',
            'calories': 22,
            'protein_g': 1.1,
            'carbs_g': 4.8,
            'fat_g': 0.2,
            'fiber_g': 1.5
        },
        'potato': {
            'food_name': 'Potato (1 medium, baked)',
            'calories': 161,
            'protein_g': 4.3,
            'carbs_g': 36.6,
            'fat_g': 0.2,
            'fiber_g': 3.8
        },
        'sweet potato': {
            'food_name': 'Sweet Potato (1 medium, baked)',
            'calories': 103,
            'protein_g': 2.3,
            'carbs_g': 23.6,
            'fat_g': 0.2,
            'fiber_g': 3.8
        },
        'cucumber': {
            'food_name': 'Cucumber (1/2 cup, sliced)',
            'calories': 8,
            'protein_g': 0.3,
            'carbs_g': 1.9,
            'fat_g': 0.1,
            'fiber_g': 0.3
        },
        
        # Protein Sources
        'chicken breast': {
            'food_name': 'Chicken Breast (3 oz, cooked)',
            'calories': 165,
            'protein_g': 31.0,
            'carbs_g': 0.0,
            'fat_g': 3.6,
            'fiber_g': 0.0
        },
        'chicken thigh': {
            'food_name': 'Chicken Thigh (3 oz, cooked)',
            'calories': 209,
            'protein_g': 24.7,
            'carbs_g': 0.0,
            'fat_g': 11.2,
            'fiber_g': 0.0
        },
        'beef': {
            'food_name': 'Beef (3 oz, lean, cooked)',
            'calories': 213,
            'protein_g': 26.0,
            'carbs_g': 0.0,
            'fat_g': 11.8,
            'fiber_g': 0.0
        },
        'ground beef': {
            'food_name': 'Ground Beef (3 oz, 85% lean, cooked)',
            'calories': 218,
            'protein_g': 24.0,
            'carbs_g': 0.0,
            'fat_g': 13.0,
            'fiber_g': 0.0
        },
        'pork': {
            'food_name': 'Pork Chop (3 oz, cooked)',
            'calories': 198,
            'protein_g': 26.0,
            'carbs_g': 0.0,
            'fat_g': 9.9,
            'fiber_g': 0.0
        },
        'salmon': {
            'food_name': 'Salmon (3 oz, cooked)',
            'calories': 175,
            'protein_g': 18.8,
            'carbs_g': 0.0,
            'fat_g': 10.5,
            'fiber_g': 0.0
        },
        'tuna': {
            'food_name': 'Tuna (3 oz, canned in water)',
            'calories': 73,
            'protein_g': 16.5,
            'carbs_g': 0.0,
            'fat_g': 0.8,
            'fiber_g': 0.0
        },
        'shrimp': {
            'food_name': 'Shrimp (3 oz, cooked)',
            'calories': 84,
            'protein_g': 18.0,
            'carbs_g': 0.0,
            'fat_g': 0.9,
            'fiber_g': 0.0
        },
        'tofu': {
            'food_name': 'Tofu (1/2 cup)',
            'calories': 94,
            'protein_g': 10.0,
            'carbs_g': 2.3,
            'fat_g': 5.9,
            'fiber_g': 0.5
        },
        'tempeh': {
            'food_name': 'Tempeh (3 oz)',
            'calories': 160,
            'protein_g': 15.0,
            'carbs_g': 7.0,
            'fat_g': 9.0,
            'fiber_g': 4.8
        },
        'lentils': {
            'food_name': 'Lentils (1/2 cup, cooked)',
            'calories': 115,
            'protein_g': 9.0,
            'carbs_g': 20.0,
            'fat_g': 0.4,
            'fiber_g': 7.8
        },
        'chickpeas': {
            'food_name': 'Chickpeas (1/2 cup, cooked)',
            'calories': 134,
            'protein_g': 7.0,
            'carbs_g': 22.5,
            'fat_g': 2.1,
            'fiber_g': 6.2
        },
        'black beans': {
            'food_name': 'Black Beans (1/2 cup, cooked)',
            'calories': 114,
            'protein_g': 7.6,
            'carbs_g': 20.4,
            'fat_g': 0.5,
            'fiber_g': 7.5
        },
        
        # Dairy & Eggs
        'egg': {
            'food_name': 'Egg (1 large)',
            'calories': 72,
            'protein_g': 6.3,
            'carbs_g': 0.4,
            'fat_g': 5.0,
            'fiber_g': 0.0
        },
        'milk': {
            'food_name': 'Milk (1 cup, whole)',
            'calories': 149,
            'protein_g': 7.7,
            'carbs_g': 11.7,
            'fat_g': 8.0,
            'fiber_g': 0.0
        },
        'skim milk': {
            'food_name': 'Skim Milk (1 cup)',
            'calories': 83,
            'protein_g': 8.3,
            'carbs_g': 12.2,
            'fat_g': 0.2,
            'fiber_g': 0.0
        },
        'yogurt': {
            'food_name': 'Greek Yogurt (1 cup, plain)',
            'calories': 130,
            'protein_g': 22.0,
            'carbs_g': 9.0,
            'fat_g': 0.0,
            'fiber_g': 0.0
        },
        'cheese': {
            'food_name': 'Cheddar Cheese (1 oz)',
            'calories': 113,
            'protein_g': 7.0,
            'carbs_g': 0.4,
            'fat_g': 9.3,
            'fiber_g': 0.0
        },
        'cottage cheese': {
            'food_name': 'Cottage Cheese (1/2 cup)',
            'calories': 110,
            'protein_g': 12.5,
            'carbs_g': 3.5,
            'fat_g': 4.5,
            'fiber_g': 0.0
        },
        
        # Grains & Cereals
        'rice': {
            'food_name': 'White Rice (1/2 cup, cooked)',
            'calories': 121,
            'protein_g': 2.5,
            'carbs_g': 26.5,
            'fat_g': 0.3,
            'fiber_g': 0.3
        },
        'brown rice': {
            'food_name': 'Brown Rice (1/2 cup, cooked)',
            'calories': 109,
            'protein_g': 2.3,
            'carbs_g': 22.9,
            'fat_g': 0.9,
            'fiber_g': 1.8
        },
        'quinoa': {
            'food_name': 'Quinoa (1/2 cup, cooked)',
            'calories': 111,
            'protein_g': 4.1,
            'carbs_g': 19.7,
            'fat_g': 1.8,
            'fiber_g': 2.6
        },
        'bread': {
            'food_name': 'White Bread (1 slice)',
            'calories': 75,
            'protein_g': 2.6,
            'carbs_g': 13.8,
            'fat_g': 1.0,
            'fiber_g': 0.8
        },
        'whole wheat bread': {
            'food_name': 'Whole Wheat Bread (1 slice)',
            'calories': 81,
            'protein_g': 4.0,
            'carbs_g': 15.0,
            'fat_g': 1.1,
            'fiber_g': 2.0
        },
        'pasta': {
            'food_name': 'Pasta (1 cup, cooked)',
            'calories': 221,
            'protein_g': 8.1,
            'carbs_g': 43.2,
            'fat_g': 1.3,
            'fiber_g': 2.5
        },
        'whole wheat pasta': {
            'food_name': 'Whole Wheat Pasta (1 cup, cooked)',
            'calories': 174,
            'protein_g': 7.5,
            'carbs_g': 37.2,
            'fat_g': 0.8,
            'fiber_g': 6.3
        },
        'oats': {
            'food_name': 'Oatmeal (1/2 cup, dry)',
            'calories': 150,
            'protein_g': 5.0,
            'carbs_g': 27.0,
            'fat_g': 3.0,
            'fiber_g': 4.0
        },
        
        # Nuts & Seeds
        'almonds': {
            'food_name': 'Almonds (1 oz, 23 nuts)',
            'calories': 164,
            'protein_g': 6.0,
            'carbs_g': 6.1,
            'fat_g': 14.0,
            'fiber_g': 3.5
        },
        'walnuts': {
            'food_name': 'Walnuts (1 oz, 14 halves)',
            'calories': 185,
            'protein_g': 4.3,
            'carbs_g': 3.9,
            'fat_g': 18.5,
            'fiber_g': 1.9
        },
        'peanut butter': {
            'food_name': 'Peanut Butter (2 tbsp)',
            'calories': 188,
            'protein_g': 8.0,
            'carbs_g': 6.9,
            'fat_g': 16.0,
            'fiber_g': 1.9
        },
        'chia seeds': {
            'food_name': 'Chia Seeds (1 tbsp)',
            'calories': 58,
            'protein_g': 2.0,
            'carbs_g': 5.0,
            'fat_g': 3.0,
            'fiber_g': 4.0
        },
        'flax seeds': {
            'food_name': 'Flax Seeds (1 tbsp)',
            'calories': 55,
            'protein_g': 1.9,
            'carbs_g': 3.0,
            'fat_g': 4.3,
            'fiber_g': 2.8
        },
        
        # Oils & Fats
        'olive oil': {
            'food_name': 'Olive Oil (1 tbsp)',
            'calories': 119,
            'protein_g': 0.0,
            'carbs_g': 0.0,
            'fat_g': 13.5,
            'fiber_g': 0.0
        },
        'coconut oil': {
            'food_name': 'Coconut Oil (1 tbsp)',
            'calories': 121,
            'protein_g': 0.0,
            'carbs_g': 0.0,
            'fat_g': 13.6,
            'fiber_g': 0.0
        },
        'butter': {
            'food_name': 'Butter (1 tbsp)',
            'calories': 102,
            'protein_g': 0.1,
            'carbs_g': 0.0,
            'fat_g': 11.5,
            'fiber_g': 0.0
        }
    }
    
    # Check if the query matches any of our common foods (case-insensitive)
    query_lower = query.lower().strip()
    
    # First, try exact matches
    if query_lower in common_foods:
        logging.info(f"Found exact nutrition data for: {query}")
        return common_foods[query_lower]
    
    # Then try partial matches
    for food_key, nutrition in common_foods.items():
        if food_key in query_lower or query_lower in food_key:
            logging.info(f"Found nutrition data for: {query} (matched with {food_key})")
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
    logging.info(f"Returning approximate nutrition data for: {query}")
    return {
        'food_name': query.capitalize(),
        'calories': 120,  # Generic average value
        'protein_g': 4,
        'carbs_g': 18,
        'fat_g': 3,
        'fiber_g': 2,
        'note': 'Approximate values - for educational purposes only'
    }
