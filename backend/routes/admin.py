"""
Admin routes - handles data export and management.
"""
from flask import Blueprint, jsonify
from backend.database import get_db_session
from backend.models import User, Session, Message

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/export', methods=['GET'])
def export_data():
    """
    Export all study data in JSON format.
    
    Response:
        {
            "users": [...],
            "sessions": [...],
            "messages": [...]
        }
    """
    try:
        db = get_db_session()
        
        try:
            # Get all users
            users = db.query(User).all()
            users_data = [user.to_dict() for user in users]
            
            # Get all sessions
            sessions = db.query(Session).all()
            sessions_data = [session.to_dict() for session in sessions]
            
            # Get all messages
            messages = db.query(Message).all()
            messages_data = [message.to_dict() for message in messages]
            
            return jsonify({
                'users': users_data,
                'sessions': sessions_data,
                'messages': messages_data,
                'total_users': len(users_data),
                'total_sessions': len(sessions_data),
                'total_messages': len(messages_data)
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/admin/stats', methods=['GET'])
def get_stats():
    """
    Get basic statistics about the study.
    
    Response:
        {
            "total_users": 10,
            "total_sessions": 25,
            "total_messages": 150,
            "sessions_by_model": {
                "llama3.2:3b": 12,
                "UnlearningToRest": 13
            }
        }
    """
    try:
        db = get_db_session()
        
        try:
            from sqlalchemy import func
            
            # Basic counts
            total_users = db.query(func.count(User.id)).scalar()
            total_sessions = db.query(func.count(Session.id)).scalar()
            total_messages = db.query(func.count(Message.id)).scalar()
            
            # Sessions by model
            sessions_by_model = {}
            model_counts = db.query(
                Session.model_name,
                func.count(Session.id)
            ).group_by(Session.model_name).all()
            
            for model_name, count in model_counts:
                sessions_by_model[model_name] = count
            
            return jsonify({
                'total_users': total_users,
                'total_sessions': total_sessions,
                'total_messages': total_messages,
                'sessions_by_model': sessions_by_model
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
