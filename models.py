from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson.objectid import ObjectId
from app import mongo, login_manager

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
        # Check if mongo is using in-memory storage
        if not hasattr(mongo.db.users, 'update_one'):
            if self._id:
                # Update in-memory user
                for i, user in enumerate(mongo.db.users):
                    if user.get('_id') == self._id:
                        mongo.db.users[i] = self.to_dict()
                        mongo.db.users[i]['_id'] = self._id
                        break
            else:
                # Create new user with ObjectId
                self._id = ObjectId()
                user_dict = self.to_dict()
                user_dict['_id'] = self._id
                mongo.db.users.append(user_dict)
        else:
            # Standard MongoDB operations
            if self._id:
                mongo.db.users.update_one({'_id': self._id}, {'$set': self.to_dict()})
            else:
                result = mongo.db.users.insert_one(self.to_dict())
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
        # Check if mongo is using in-memory storage
        if not hasattr(mongo.db.nutrition_recommendations, 'find'):
            # Filter recommendations for this user and sort by created_at descending
            return sorted(
                [rec for rec in mongo.db.nutrition_recommendations if rec.get('user_id') == self._id],
                key=lambda x: x.get('created_at', datetime.utcnow()),
                reverse=True
            )
        else:
            return list(mongo.db.nutrition_recommendations.find({'user_id': self._id}).sort('created_at', -1))
    
    @classmethod
    def get_by_id(cls, user_id):
        try:
            # Check if mongo is using in-memory storage
            if not hasattr(mongo.db.users, 'find_one'):
                for user in mongo.db.users:
                    if str(user.get('_id')) == str(user_id):
                        return cls(**user)
                return None
            else:
                user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
                if user_data:
                    user_data['_id'] = user_data['_id']
                    return cls(**user_data)
        except Exception as e:
            print(f"Error in get_by_id: {str(e)}")
            return None
    
    @classmethod
    def get_by_username(cls, username):
        # Check if mongo is using in-memory storage
        if not hasattr(mongo.db.users, 'find_one'):
            for user in mongo.db.users:
                if user.get('username') == username:
                    return cls(**user)
            return None
        else:
            user_data = mongo.db.users.find_one({'username': username})
            if user_data:
                user_data['_id'] = user_data['_id']
                return cls(**user_data)
            return None
    
    @classmethod
    def get_by_email(cls, email):
        # Check if mongo is using in-memory storage
        if not hasattr(mongo.db.users, 'find_one'):
            for user in mongo.db.users:
                if user.get('email') == email:
                    return cls(**user)
            return None
        else:
            user_data = mongo.db.users.find_one({'email': email})
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
        
        # Check if mongo is using in-memory storage
        if not hasattr(mongo.db.nutrition_recommendations, 'update_one'):
            if self._id:
                # Update in-memory recommendation
                for i, rec in enumerate(mongo.db.nutrition_recommendations):
                    if rec.get('_id') == self._id:
                        mongo.db.nutrition_recommendations[i] = data
                        mongo.db.nutrition_recommendations[i]['_id'] = self._id
                        break
            else:
                # Create new recommendation with ObjectId
                self._id = ObjectId()
                data['_id'] = self._id
                mongo.db.nutrition_recommendations.append(data)
        else:
            # Standard MongoDB operations
            if self._id:
                mongo.db.nutrition_recommendations.update_one({'_id': self._id}, {'$set': data})
            else:
                result = mongo.db.nutrition_recommendations.insert_one(data)
                self._id = result.inserted_id
        return self
    
    @classmethod
    def get_by_id(cls, rec_id):
        # Check if mongo is using in-memory storage
        if not hasattr(mongo.db.nutrition_recommendations, 'find_one'):
            for rec in mongo.db.nutrition_recommendations:
                if str(rec.get('_id')) == str(rec_id):
                    return cls(**rec)
            return None
        else:
            rec_data = mongo.db.nutrition_recommendations.find_one({'_id': ObjectId(rec_id)})
            if rec_data:
                rec_data['_id'] = rec_data['_id']
                return cls(**rec_data)
            return None
    
    @classmethod
    def get_by_user_id(cls, user_id, limit=1):
        # Check if mongo is using in-memory storage
        if not hasattr(mongo.db.nutrition_recommendations, 'find'):
            # Filter recommendations for this user
            user_recs = [rec for rec in mongo.db.nutrition_recommendations 
                         if str(rec.get('user_id')) == str(user_id)]
            # Sort by created_at (descending)
            user_recs.sort(key=lambda x: x.get('created_at', datetime.utcnow()), reverse=True)
            # Apply limit
            user_recs = user_recs[:limit]
            return [cls(**rec) for rec in user_recs]
        else:
            recs = mongo.db.nutrition_recommendations.find({'user_id': user_id}).sort('created_at', -1).limit(limit)
            return [cls(**rec) for rec in recs]
    
    def __repr__(self):
        return f'<NutritionRecommendation #{self._id} for User {self.user_id}>'


# Setup the user loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)
