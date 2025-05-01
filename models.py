from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson.objectid import ObjectId
import app  # Import app module, not specific variables to avoid circular imports

class User(UserMixin):
    def __init__(self, username=None, email=None, password_hash=None, _id=None, **kwargs):
        self._id = _id if _id else None
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        
        # User profile information
        self.name = kwargs.get('name')
        self.age = kwargs.get('age')
        self.gender = kwargs.get('gender')
        self.weight = kwargs.get('weight')  # in kg
        self.height = kwargs.get('height')  # in cm
        self.activity_level = kwargs.get('activity_level')
        self.diet_type = kwargs.get('diet_type')
        self.health_goals = kwargs.get('health_goals')
        self.allergies = kwargs.get('allergies')
    
    def get_id(self):
        return str(self._id)
    
    @property
    def id(self):
        return self._id
        
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def save(self):
        if self._id:
            app.mongo.db.users.update_one({'_id': self._id}, {'$set': self.to_dict()})
        else:
            result = app.mongo.db.users.insert_one(self.to_dict())
            self._id = result.inserted_id
        return self
    
    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'weight': self.weight,
            'height': self.height,
            'activity_level': self.activity_level,
            'diet_type': self.diet_type,
            'health_goals': self.health_goals,
            'allergies': self.allergies
        }
    
    @property
    def recommendations(self):
        return list(app.mongo.db.nutrition_recommendations.find({'user_id': self._id}).sort('created_at', -1))
    
    @classmethod
    def get_by_id(cls, user_id):
        try:
            user_data = app.mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if user_data:
                user_data['_id'] = user_data['_id']
                return cls(**user_data)
        except Exception:
            return None
    
    @classmethod
    def get_by_username(cls, username):
        user_data = app.mongo.db.users.find_one({'username': username})
        if user_data:
            user_data['_id'] = user_data['_id']
            return cls(**user_data)
        return None
    
    @classmethod
    def get_by_email(cls, email):
        user_data = app.mongo.db.users.find_one({'email': email})
        if user_data:
            user_data['_id'] = user_data['_id']
            return cls(**user_data)
        return None

    def __repr__(self):
        return f'<User {self.username}>'


class NutritionRecommendation:
    def __init__(self, user_id, diet_type, daily_calories, protein, carbs, fats,
                 breakfast_suggestion, lunch_suggestion, dinner_suggestion, 
                 snacks_suggestion, additional_notes, _id=None, created_at=None):
        self._id = _id if _id else None
        self.user_id = user_id
        self.created_at = created_at if created_at else datetime.utcnow()
        
        # Recommendation details
        self.diet_type = diet_type
        self.daily_calories = daily_calories
        self.protein = protein  # in grams
        self.carbs = carbs      # in grams
        self.fats = fats        # in grams
        
        # Recommendation text
        self.breakfast_suggestion = breakfast_suggestion
        self.lunch_suggestion = lunch_suggestion
        self.dinner_suggestion = dinner_suggestion
        self.snacks_suggestion = snacks_suggestion
        self.additional_notes = additional_notes
    
    @property
    def id(self):
        return self._id
    
    def save(self):
        data = {
            'user_id': self.user_id,
            'created_at': self.created_at,
            'diet_type': self.diet_type,
            'daily_calories': self.daily_calories,
            'protein': self.protein,
            'carbs': self.carbs,
            'fats': self.fats,
            'breakfast_suggestion': self.breakfast_suggestion,
            'lunch_suggestion': self.lunch_suggestion,
            'dinner_suggestion': self.dinner_suggestion,
            'snacks_suggestion': self.snacks_suggestion,
            'additional_notes': self.additional_notes
        }
        
        if self._id:
            app.mongo.db.nutrition_recommendations.update_one({'_id': self._id}, {'$set': data})
        else:
            result = app.mongo.db.nutrition_recommendations.insert_one(data)
            self._id = result.inserted_id
        return self
    
    @classmethod
    def get_by_id(cls, rec_id):
        rec_data = app.mongo.db.nutrition_recommendations.find_one({'_id': ObjectId(rec_id)})
        if rec_data:
            rec_data['_id'] = rec_data['_id']
            return cls(**rec_data)
        return None
    
    @classmethod
    def get_by_user_id(cls, user_id, limit=1):
        recs = app.mongo.db.nutrition_recommendations.find({'user_id': user_id}).sort('created_at', -1).limit(limit)
        return [cls(**rec) for rec in recs]
    
    def __repr__(self):
        return f'<NutritionRecommendation #{self._id} for User {self.user_id}>'


# Setup the user loader for Flask-Login
@app.login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)
