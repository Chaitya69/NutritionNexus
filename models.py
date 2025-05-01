from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from app import mongo, login_manager
import logging

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


class NutritionEntry:
    def __init__(self, user_id, date=None, meals=None, total_calories=0, total_protein=0, 
                 total_carbs=0, total_fat=0, total_fiber=0, water_intake=0, notes="", 
                 _id=None, created_at=None):
        self._id = _id if _id else None
        self.user_id = user_id
        self.date = date if isinstance(date, datetime) else datetime.strptime(date, '%Y-%m-%d') if isinstance(date, str) else datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        self.meals = meals or {
            "breakfast": [],
            "lunch": [],
            "dinner": [],
            "snacks": []
        }
        self.total_calories = total_calories
        self.total_protein = total_protein
        self.total_carbs = total_carbs
        self.total_fat = total_fat
        self.total_fiber = total_fiber
        self.water_intake = water_intake
        self.notes = notes
        self.created_at = created_at if created_at else datetime.utcnow()
    
    @property
    def id(self):
        return self._id
    
    @property
    def formatted_date(self):
        return self.date.strftime('%Y-%m-%d')
    
    def add_food_to_meal(self, meal_type, food_data):
        """Adds a food item to a specific meal and updates totals"""
        if meal_type not in self.meals:
            self.meals[meal_type] = []
        
        # Add timestamp to track when food was added
        food_data['timestamp'] = datetime.utcnow()
        
        # Add unique ID for the food entry
        food_data['id'] = str(ObjectId())
        
        self.meals[meal_type].append(food_data)
        
        # Update totals
        self.total_calories += float(food_data.get('calories', 0))
        self.total_protein += float(food_data.get('protein_g', 0))
        self.total_carbs += float(food_data.get('carbs_g', 0))
        self.total_fat += float(food_data.get('fat_g', 0))
        self.total_fiber += float(food_data.get('fiber_g', 0))
    
    def remove_food_from_meal(self, meal_type, food_id):
        """Removes a food item from a meal and updates totals"""
        if meal_type not in self.meals:
            return False
        
        for i, food in enumerate(self.meals[meal_type]):
            if food.get('id') == food_id:
                removed_food = self.meals[meal_type].pop(i)
                
                # Update totals by subtracting the removed food
                self.total_calories -= float(removed_food.get('calories', 0))
                self.total_protein -= float(removed_food.get('protein_g', 0))
                self.total_carbs -= float(removed_food.get('carbs_g', 0))
                self.total_fat -= float(removed_food.get('fat_g', 0))
                self.total_fiber -= float(removed_food.get('fiber_g', 0))
                
                return True
        
        return False
    
    def update_water_intake(self, amount):
        """Updates water intake amount in milliliters"""
        self.water_intake = float(amount)
    
    def save(self):
        data = {
            'user_id': self.user_id,
            'date': self.date,
            'meals': self.meals,
            'total_calories': self.total_calories,
            'total_protein': self.total_protein,
            'total_carbs': self.total_carbs,
            'total_fat': self.total_fat,
            'total_fiber': self.total_fiber,
            'water_intake': self.water_intake,
            'notes': self.notes,
            'created_at': self.created_at
        }
        
        # Check if mongo is using in-memory storage
        if not hasattr(mongo.db.nutrition_entries, 'update_one'):
            if self._id:
                # Update in-memory entry
                for i, entry in enumerate(mongo.db.nutrition_entries):
                    if entry.get('_id') == self._id:
                        mongo.db.nutrition_entries[i] = data
                        mongo.db.nutrition_entries[i]['_id'] = self._id
                        break
            else:
                # Create new entry with ObjectId
                self._id = ObjectId()
                data['_id'] = self._id
                
                # Initialize the collection if it doesn't exist
                if not hasattr(mongo.db, 'nutrition_entries'):
                    mongo.db.nutrition_entries = []
                
                mongo.db.nutrition_entries.append(data)
        else:
            # Standard MongoDB operations
            if self._id:
                mongo.db.nutrition_entries.update_one({'_id': self._id}, {'$set': data})
            else:
                result = mongo.db.nutrition_entries.insert_one(data)
                self._id = result.inserted_id
        
        return self
    
    @classmethod
    def get_by_id(cls, entry_id):
        # Check if mongo is using in-memory storage
        if not hasattr(mongo.db.nutrition_entries, 'find_one'):
            # Initialize the collection if it doesn't exist
            if not hasattr(mongo.db, 'nutrition_entries'):
                mongo.db.nutrition_entries = []
                
            for entry in mongo.db.nutrition_entries:
                if str(entry.get('_id')) == str(entry_id):
                    return cls(**entry)
            return None
        else:
            try:
                entry_data = mongo.db.nutrition_entries.find_one({'_id': ObjectId(entry_id)})
                if entry_data:
                    entry_data['_id'] = entry_data['_id'] 
                    return cls(**entry_data)
            except Exception as e:
                logging.error(f"Error fetching nutrition entry by ID: {str(e)}")
            
            return None
    
    @classmethod
    def get_by_user_and_date(cls, user_id, date):
        date_obj = date if isinstance(date, datetime) else datetime.strptime(date, '%Y-%m-%d') if isinstance(date, str) else datetime.utcnow()
        # Set time to beginning of day
        start_date = datetime(date_obj.year, date_obj.month, date_obj.day, 0, 0, 0)
        # Set time to end of day
        end_date = datetime(date_obj.year, date_obj.month, date_obj.day, 23, 59, 59)
        
        # Check if mongo is using in-memory storage
        if not hasattr(mongo.db.nutrition_entries, 'find_one'):
            # Initialize the collection if it doesn't exist
            if not hasattr(mongo.db, 'nutrition_entries'):
                mongo.db.nutrition_entries = []
                
            for entry in mongo.db.nutrition_entries:
                entry_date = entry.get('date')
                if (entry.get('user_id') == user_id and 
                    entry_date >= start_date and entry_date <= end_date):
                    return cls(**entry)
            
            # If no entry exists, create a new one
            return cls(user_id=user_id, date=start_date)
        else:
            try:
                entry_data = mongo.db.nutrition_entries.find_one({
                    'user_id': user_id,
                    'date': {'$gte': start_date, '$lte': end_date}
                })
                
                if entry_data:
                    entry_data['_id'] = entry_data['_id']
                    return cls(**entry_data)
            except Exception as e:
                logging.error(f"Error fetching nutrition entry by user and date: {str(e)}")
        
        # If no entry exists, create a new one
        return cls(user_id=user_id, date=start_date)
    
    @classmethod
    def get_user_entries(cls, user_id, days=7):
        """Get user's nutrition entries for the last X days"""
        entries = []
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Check if mongo is using in-memory storage
        if not hasattr(mongo.db.nutrition_entries, 'find'):
            # Initialize the collection if it doesn't exist
            if not hasattr(mongo.db, 'nutrition_entries'):
                mongo.db.nutrition_entries = []
                
            for entry in mongo.db.nutrition_entries:
                entry_date = entry.get('date')
                if (entry.get('user_id') == user_id and 
                    entry_date >= start_date and entry_date <= end_date):
                    entries.append(cls(**entry))
        else:
            try:
                results = mongo.db.nutrition_entries.find({
                    'user_id': user_id,
                    'date': {'$gte': start_date, '$lte': end_date}
                }).sort('date', -1)
                
                for entry in results:
                    entry['_id'] = entry['_id']
                    entries.append(cls(**entry))
            except Exception as e:
                logging.error(f"Error fetching nutrition entries: {str(e)}")
        
        return sorted(entries, key=lambda x: x.date, reverse=True)
    
    def get_macro_percentages(self):
        """Calculate macronutrient percentages"""
        total_macros = (self.total_protein * 4) + (self.total_carbs * 4) + (self.total_fat * 9)
        
        if total_macros == 0:
            return {'protein': 0, 'carbs': 0, 'fat': 0}
        
        protein_pct = round((self.total_protein * 4 / total_macros) * 100)
        carbs_pct = round((self.total_carbs * 4 / total_macros) * 100)
        fat_pct = round((self.total_fat * 9 / total_macros) * 100)
        
        # Ensure percentages add up to 100%
        total = protein_pct + carbs_pct + fat_pct
        if total != 100:
            # Adjust the largest value to make sum exactly 100
            diff = 100 - total
            if protein_pct >= carbs_pct and protein_pct >= fat_pct:
                protein_pct += diff
            elif carbs_pct >= protein_pct and carbs_pct >= fat_pct:
                carbs_pct += diff
            else:
                fat_pct += diff
        
        return {'protein': protein_pct, 'carbs': carbs_pct, 'fat': fat_pct}
    
    def __repr__(self):
        return f'<NutritionEntry {self.id} {self.formatted_date}>'


# Setup the user loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)
