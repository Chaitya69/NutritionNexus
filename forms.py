from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FloatField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError
from models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.get_by_username(username.data)
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.get_by_email(email.data)
        if user:
            raise ValidationError('Email already registered. Please use a different one or login.')


class ProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[Optional(), Length(max=100)])
    age = IntegerField('Age', validators=[Optional()])
    gender = SelectField('Gender', choices=[
        ('', 'Select Gender'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say')
    ], validators=[Optional()])
    weight = FloatField('Weight (kg)', validators=[Optional()])
    height = FloatField('Height (cm)', validators=[Optional()])
    activity_level = SelectField('Activity Level', choices=[
        ('', 'Select Activity Level'),
        ('sedentary', 'Sedentary (little or no exercise)'),
        ('light', 'Lightly active (light exercise/sports 1-3 days/week)'),
        ('moderate', 'Moderately active (moderate exercise/sports 3-5 days/week)'),
        ('active', 'Very active (hard exercise/sports 6-7 days a week)'),
        ('extra_active', 'Extra active (very hard exercise & physical job or 2x training)')
    ], validators=[Optional()])
    diet_type = SelectField('Diet Type', choices=[
        ('', 'Select Diet Type'),
        ('omnivore', 'Omnivore (Everything)'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('pescatarian', 'Pescatarian'),
        ('keto', 'Ketogenic'),
        ('paleo', 'Paleo'),
        ('gluten_free', 'Gluten-Free'),
        ('mediterranean', 'Mediterranean')
    ], validators=[Optional()])
    health_goals = StringField('Health Goals', validators=[Optional(), Length(max=200)])
    allergies = TextAreaField('Allergies or Food Restrictions', validators=[Optional(), Length(max=300)])
    submit = SubmitField('Update Profile')


class NutritionQueryForm(FlaskForm):
    diet_type = SelectField('Diet Type', choices=[
        ('omnivore', 'Omnivore (Everything)'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('pescatarian', 'Pescatarian'),
        ('keto', 'Ketogenic'),
        ('paleo', 'Paleo'),
        ('gluten_free', 'Gluten-Free'),
        ('mediterranean', 'Mediterranean')
    ], validators=[DataRequired()])
    health_focus = SelectField('Health Focus', choices=[
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('maintenance', 'Maintenance'),
        ('heart_health', 'Heart Health'),
        ('diabetes', 'Diabetes Management'),
        ('energy', 'Energy Boost'),
        ('general', 'General Health')
    ], validators=[DataRequired()])
    submit = SubmitField('Get Recommendations')
