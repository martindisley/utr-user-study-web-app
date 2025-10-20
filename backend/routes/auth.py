"""
Authentication routes - handles user login via email.
"""
from flask import Blueprint, request, jsonify
from backend.database import get_db_session
from backend.models import User
import re

auth_bp = Blueprint('auth', __name__)

# Simple email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


def validate_email(email):
    """Validate email format."""
    if not email:
        return False
    return bool(EMAIL_REGEX.match(email))


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
                # Create new user
                new_user = User(email=email)
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
