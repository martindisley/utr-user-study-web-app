"""
Authentication routes - handles user login via email.
"""
from flask import Blueprint, request, jsonify
from backend.database import get_db_session
from backend.models import User, Session
from backend import config
import re
import random

auth_bp = Blueprint('auth', __name__)

# Simple email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


def validate_email(email):
    """Validate email format."""
    if not email:
        return False
    return bool(EMAIL_REGEX.match(email))


def assign_model_order():
    """
    Generate a randomized model order for counterbalancing.
    Uses all possible permutations of the 3 models.
    Returns a comma-separated string of model IDs.
    """
    model_ids = [m['id'] for m in config.AVAILABLE_MODELS]
    random.shuffle(model_ids)
    return ','.join(model_ids)


@auth_bp.route('/api/login', methods=['POST'])
def login():
    """
    Login endpoint - creates or retrieves user by email.
    
    Request body:
        {
            "email": "user@example.com"
        }
    
    Response:
        {
            "user_id": 1,
            "email": "user@example.com",
            "is_new_user": true/false
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400
        
        email = data['email'].strip().lower()
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        db = get_db_session()
        
        try:
            # Check if user exists
            user = db.query(User).filter(User.email == email).first()
            
            if user:
                # Existing user
                return jsonify({
                    'user_id': user.id,
                    'email': user.email,
                    'is_new_user': False
                }), 200
            else:
                # Create new user with randomized model order
                new_user = User(
                    email=email,
                    model_order=assign_model_order()
                )
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                
                return jsonify({
                    'user_id': new_user.id,
                    'email': new_user.email,
                    'is_new_user': True
                }), 201
                
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/api/user/<int:user_id>/next-model', methods=['GET'])
def get_next_model(user_id):
    """
    Get the next assigned model for a user based on their predetermined order.
    
    Response:
        {
            "model_id": "llama3.2:3b",
            "model_name": "Meta Llama 3.2",
            "model_description": "Standard Llama 3.2 model with 3B parameters",
            "activity_number": 1
        }
        
    Or 404 if all models have been used.
    """
    try:
        db = get_db_session()
        
        try:
            # Get user
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Get user's model order
            if not user.model_order:
                # Assign order if not set (for existing users before this feature)
                user.model_order = assign_model_order()
                db.commit()
                db.refresh(user)
            
            model_order = user.model_order.split(',')
            
            # Count how many sessions user has completed
            session_count = db.query(Session).filter(Session.user_id == user_id).count()
            
            # Check if user has completed all models
            if session_count >= len(model_order):
                return jsonify({'error': 'All activities completed'}), 404
            
            # Get the next model in the order
            next_model_id = model_order[session_count]
            
            # Find model details
            model_info = next((m for m in config.AVAILABLE_MODELS if m['id'] == next_model_id), None)
            if not model_info:
                return jsonify({'error': 'Invalid model in order'}), 500
            
            return jsonify({
                'model_id': model_info['id'],
                'model_name': model_info['name'],
                'model_description': model_info['description'],
                'activity_number': session_count + 1
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
