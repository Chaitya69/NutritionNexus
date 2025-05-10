from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from app import app, mongo
from models import User, NutritionRecommendation
from forms import LoginForm, RegistrationForm, ProfileForm, NutritionQueryForm
from utils import generate_nutrition_recommendation, get_food_nutrition
from firebase_config import check_firebase_config
import logging
from datetime import datetime

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


@app.route('/firebase_test')
def firebase_test():
    """Test page for Firebase configuration and authentication"""
    has_firebase = check_firebase_config()
    
    if not has_firebase:
        flash('Firebase configuration is incomplete. Some features may not work.', 'warning')
    
    return render_template('firebase_test.html')

