from flask import render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import app, mongo
from models import User, NutritionRecommendation, NutritionEntry
from forms import (
    LoginForm, RegistrationForm, ProfileForm, NutritionQueryForm,
    NutritionEntryForm, FoodEntryForm, NutritionDateSelectForm, NutritionAnalyticsForm
)
from utils import generate_nutrition_recommendation, get_food_nutrition
import logging
from datetime import datetime, timedelta
import json

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        if User.get_by_username(form.username.data):
            flash('Username already taken. Please choose a different one.', 'danger')
            return render_template('register.html', form=form)
        
        if User.get_by_email(form.email.data):
            flash('Email already registered. Please use a different one or login.', 'danger')
            return render_template('register.html', form=form)
        
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        user.save()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    
    if request.method == 'GET':
        form.name.data = current_user.name
        form.age.data = current_user.age
        form.gender.data = current_user.gender
        form.weight.data = current_user.weight
        form.height.data = current_user.height
        form.activity_level.data = current_user.activity_level
        form.diet_type.data = current_user.diet_type
        form.health_goals.data = current_user.health_goals
        form.allergies.data = current_user.allergies
    
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.age = form.age.data
        current_user.gender = form.gender.data
        current_user.weight = form.weight.data
        current_user.height = form.height.data
        current_user.activity_level = form.activity_level.data
        current_user.diet_type = form.diet_type.data
        current_user.health_goals = form.health_goals.data
        current_user.allergies = form.allergies.data
        
        current_user.save()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', form=form)

@app.route('/nutrition/recommendations', methods=['GET', 'POST'])
@login_required
def nutrition_recommendation():
    form = NutritionQueryForm()
    recommendation = None
    
    # Pre-fill the diet type if user has one set in their profile
    if request.method == 'GET' and current_user.diet_type:
        form.diet_type.data = current_user.diet_type
    
    if form.validate_on_submit():
        # Generate nutrition recommendation based on user profile and form input
        recommendation_data = generate_nutrition_recommendation(
            current_user, 
            form.diet_type.data,
            form.health_focus.data
        )
        
        # Create new recommendation record
        recommendation = NutritionRecommendation(
            user_id=current_user.id,
            diet_type=form.diet_type.data,
            daily_calories=recommendation_data['daily_calories'],
            protein=recommendation_data['protein'],
            carbs=recommendation_data['carbs'],
            fats=recommendation_data['fats'],
            breakfast_suggestion=recommendation_data['breakfast_suggestion'],
            lunch_suggestion=recommendation_data['lunch_suggestion'],
            dinner_suggestion=recommendation_data['dinner_suggestion'],
            snacks_suggestion=recommendation_data['snacks_suggestion'],
            additional_notes=recommendation_data['additional_notes']
        )
        
        recommendation.save()
        flash('Your nutrition recommendation has been generated!', 'success')
    
    # Get the most recent recommendation for this user if available
    if recommendation is None and current_user.recommendations:
        recommendation = NutritionRecommendation(**current_user.recommendations[0])
    
    return render_template('nutrition_recommendation.html', form=form, recommendation=recommendation)

@app.route('/api/food_nutrition')
@login_required
def api_food_nutrition():
    """API endpoint to get nutrition data for a food item"""
    food_query = request.args.get('query', '')
    if not food_query:
        return {'error': 'No food query provided'}, 400
    
    try:
        result = get_food_nutrition(food_query)
        
        # Add a note if the response includes it
        if 'note' in result:
            result_with_note = {**result}
            app.logger.info(f"Returning approximate nutrition data for: {food_query}")
        else:
            result_with_note = {**result}
            
        return result_with_note
    except Exception as e:
        app.logger.error(f"Error retrieving nutrition data: {str(e)}")
        # Return a user-friendly error response
        return {
            'error': 'Unable to retrieve nutrition data', 
            'food_name': food_query.capitalize(),
            'calories': 0,
            'protein_g': 0,
            'carbs_g': 0,
            'fat_g': 0,
            'fiber_g': 0,
            'note': 'Data unavailable'
        }


@app.route('/nutrition/tracker', methods=['GET', 'POST'])
@login_required
def nutrition_tracker():
    """Daily nutrition tracking page"""
    # Get date from query parameter or default to today
    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        selected_date = datetime.now()
    
    # Get or create nutrition entry for this date
    entry = NutritionEntry.get_by_user_and_date(current_user.id, selected_date)
    
    # Forms for the page
    entry_form = NutritionEntryForm(obj=entry)
    food_form = FoodEntryForm()
    date_select_form = NutritionDateSelectForm()
    date_select_form.date.data = selected_date
    
    # Handle entry form submission (notes and water intake)
    if entry_form.validate_on_submit() and 'save_entry' in request.form:
        entry.notes = entry_form.notes.data
        entry.water_intake = entry_form.water_intake.data
        entry.save()
        flash('Nutrition entry updated successfully!', 'success')
        return redirect(url_for('nutrition_tracker', date=entry.formatted_date))
    
    # Pre-fill the entry form
    if not entry_form.is_submitted():
        entry_form.notes.data = entry.notes
        entry_form.water_intake.data = entry.water_intake
    
    # Get recent recommendations for this user
    recommendations = NutritionRecommendation.get_by_user_id(current_user.id, limit=1)
    recommendation = recommendations[0] if recommendations else None
    
    # Calculate progress towards daily goals if recommendation exists
    progress = {}
    if recommendation:
        progress = {
            'calories': min(100, int((entry.total_calories / recommendation.daily_calories) * 100)) if recommendation.daily_calories > 0 else 0,
            'protein': min(100, int((entry.total_protein / recommendation.protein) * 100)) if recommendation.protein > 0 else 0,
            'carbs': min(100, int((entry.total_carbs / recommendation.carbs) * 100)) if recommendation.carbs > 0 else 0,
            'fat': min(100, int((entry.total_fat / recommendation.fats) * 100)) if recommendation.fats > 0 else 0
        }
    
    # Calculate macro percentages for charts
    macro_percentages = entry.get_macro_percentages()
    
    return render_template(
        'nutrition_tracker.html',
        entry=entry,
        entry_form=entry_form,
        food_form=food_form,
        date_select_form=date_select_form,
        recommendation=recommendation,
        progress=progress,
        macro_percentages=macro_percentages,
        selected_date=selected_date,
        timedelta=timedelta
    )


@app.route('/nutrition/tracker/add-food', methods=['POST'])
@login_required
def add_food_to_tracker():
    """Add a food item to a meal in the nutrition tracker"""
    form = FoodEntryForm()
    if form.validate_on_submit():
        date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            selected_date = datetime.now()
        
        # Get the nutrition entry for this date
        entry = NutritionEntry.get_by_user_and_date(current_user.id, selected_date)
        
        # Get nutrition data for the food
        food_data = get_food_nutrition(form.food_query.data)
        
        # Apply quantity multiplier
        quantity = float(form.quantity.data)
        for key in ['calories', 'protein_g', 'carbs_g', 'fat_g', 'fiber_g']:
            if key in food_data:
                food_data[key] = round(float(food_data[key]) * quantity, 1)
        
        # Add quantity information to the food data
        food_data['quantity'] = quantity
        food_data['food_query'] = form.food_query.data
        
        # Add the food to the meal
        entry.add_food_to_meal(form.meal_type.data, food_data)
        entry.save()
        
        flash(f'Added {food_data["food_name"]} to {form.meal_type.data}', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{error}', 'danger')
    
    return redirect(url_for('nutrition_tracker', date=request.args.get('date', datetime.now().strftime('%Y-%m-%d'))))


@app.route('/nutrition/tracker/remove-food', methods=['POST'])
@login_required
def remove_food_from_tracker():
    """Remove a food item from a meal in the nutrition tracker"""
    meal_type = request.form.get('meal_type')
    food_id = request.form.get('food_id')
    date_str = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    if not meal_type or not food_id:
        flash('Missing required information to remove food item', 'danger')
        return redirect(url_for('nutrition_tracker', date=date_str))
    
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        selected_date = datetime.now()
    
    # Get the nutrition entry for this date
    entry = NutritionEntry.get_by_user_and_date(current_user.id, selected_date)
    
    # Remove the food from the meal
    if entry.remove_food_from_meal(meal_type, food_id):
        entry.save()
        flash('Food item removed successfully', 'success')
    else:
        flash('Failed to remove food item', 'danger')
    
    return redirect(url_for('nutrition_tracker', date=date_str))


@app.route('/nutrition/analytics', methods=['GET', 'POST'])
@login_required
def nutrition_analytics():
    """Nutrition analytics and visualization page"""
    form = NutritionAnalyticsForm()
    
    if form.validate_on_submit():
        days = int(form.period.data)
        metric = form.metric.data
    else:
        days = 7  # Default to 7 days
        metric = 'calories'  # Default to calories
    
    # Get entries for the selected period
    entries = NutritionEntry.get_user_entries(current_user.id, days=days)
    
    # Prepare data for charts
    dates = []
    calories_data = []
    protein_data = []
    carbs_data = []
    fat_data = []
    water_data = []
    
    # Get most recent recommendation for target values
    recommendations = NutritionRecommendation.get_by_user_id(current_user.id, limit=1)
    recommendation = recommendations[0] if recommendations else None
    
    # Fill in missing dates with zero values
    end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=days)
    
    current_date = start_date
    while current_date <= end_date:
        # Try to find an entry for this date
        date_entry = next((e for e in entries if e.date.date() == current_date.date()), None)
        
        dates.append(current_date.strftime('%Y-%m-%d'))
        
        if date_entry:
            calories_data.append(date_entry.total_calories)
            protein_data.append(date_entry.total_protein)
            carbs_data.append(date_entry.total_carbs)
            fat_data.append(date_entry.total_fat)
            water_data.append(date_entry.water_intake)
        else:
            calories_data.append(0)
            protein_data.append(0)
            carbs_data.append(0)
            fat_data.append(0)
            water_data.append(0)
        
        current_date += timedelta(days=1)
    
    # Prepare the data for the selected metric
    chart_data = {
        'labels': dates,
        'datasets': []
    }
    
    if metric == 'calories':
        target = recommendation.daily_calories if recommendation else 2000
        chart_data['datasets'] = [
            {
                'label': 'Calories',
                'data': calories_data,
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'borderColor': 'rgba(75, 192, 192, 1)',
            },
            {
                'label': 'Target',
                'data': [target] * len(dates),
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderDash': [5, 5],
                'fill': False,
                'type': 'line'
            }
        ]
    elif metric == 'macros':
        chart_data['datasets'] = [
            {
                'label': 'Protein (g)',
                'data': protein_data,
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'borderColor': 'rgba(54, 162, 235, 1)',
            },
            {
                'label': 'Carbs (g)',
                'data': carbs_data,
                'backgroundColor': 'rgba(255, 206, 86, 0.2)',
                'borderColor': 'rgba(255, 206, 86, 1)',
            },
            {
                'label': 'Fat (g)',
                'data': fat_data,
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'borderColor': 'rgba(255, 99, 132, 1)',
            }
        ]
    elif metric == 'water':
        target_water = 2000  # Default target: 2000ml
        chart_data['datasets'] = [
            {
                'label': 'Water Intake (ml)',
                'data': water_data,
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'borderColor': 'rgba(54, 162, 235, 1)',
            },
            {
                'label': 'Target',
                'data': [target_water] * len(dates),
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderDash': [5, 5],
                'fill': False,
                'type': 'line'
            }
        ]
    
    # Calculate summary statistics
    summary = {
        'avg_calories': round(sum(calories_data) / len(calories_data), 1) if calories_data else 0,
        'avg_protein': round(sum(protein_data) / len(protein_data), 1) if protein_data else 0,
        'avg_carbs': round(sum(carbs_data) / len(carbs_data), 1) if carbs_data else 0,
        'avg_fat': round(sum(fat_data) / len(fat_data), 1) if fat_data else 0,
        'avg_water': round(sum(water_data) / len(water_data), 1) if water_data else 0,
        'days_tracked': len([c for c in calories_data if c > 0]),
        'completion_rate': f"{int(len([c for c in calories_data if c > 0]) / len(calories_data) * 100)}%" if calories_data else "0%"
    }
    
    # Convert chart data to JSON for the template
    chart_json = json.dumps(chart_data)
    
    return render_template(
        'nutrition_analytics.html',
        form=form,
        chart_data=chart_json,
        summary=summary,
        entries=entries,
        recommendation=recommendation,
        timedelta=timedelta
    )


@app.route('/api/nutrition/entry/<date_str>', methods=['GET'])
@login_required
def api_nutrition_entry(date_str):
    """API endpoint to get nutrition entry data for a specific date"""
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return {'error': 'Invalid date format. Use YYYY-MM-DD'}, 400
    
    entry = NutritionEntry.get_by_user_and_date(current_user.id, date)
    
    # Get recommendation for comparison
    recommendations = NutritionRecommendation.get_by_user_id(current_user.id, limit=1)
    recommendation = recommendations[0] if recommendations else None
    
    # Prepare the response
    response = {
        'date': entry.formatted_date,
        'total_calories': entry.total_calories,
        'total_protein': entry.total_protein,
        'total_carbs': entry.total_carbs,
        'total_fat': entry.total_fat,
        'total_fiber': entry.total_fiber,
        'water_intake': entry.water_intake,
        'meals': entry.meals,
        'macro_percentages': entry.get_macro_percentages()
    }
    
    # Add target values if recommendation exists
    if recommendation:
        response['targets'] = {
            'calories': recommendation.daily_calories,
            'protein': recommendation.protein,
            'carbs': recommendation.carbs,
            'fat': recommendation.fats
        }
    
    return jsonify(response)
