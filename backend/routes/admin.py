"""
Admin routes - handles data export and management.
"""
from collections import Counter

from flask import Blueprint, jsonify

from backend.database import get_db_session
from backend.models import User, Session, Message, Prompt, GeneratedImage

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/export', methods=['GET'])
def export_data():
    """
    Export all study data in JSON format.
    
    Response (human readable):
        {
            "summary": {
                "total_users": 12,
                "total_sessions": 25,
                "total_messages": 150,
                "sessions_by_model": {
                    "llama3.2:3b": 12,
                    "martindisley/unlearning-to-rest:latest": 13
                }
            },
            "users": [
                {
                    "id": 1,
                    "email": "student@example.edu",
                    "created_at": "2025-10-17T13:57:10.228704",
                    "session_count": 2,
                    "sessions": [
                        {
                            "id": 4,
                            "model_name": "martindisley/unlearning-to-rest:latest",
                            "created_at": "2025-10-17T14:10:00.896350",
                            "message_count": 6,
                            "messages": [
                                {
                                    "id": 21,
                                    "role": "user",
                                    "timestamp": "2025-10-17T14:10:05.711022",
                                    "content": "Hello"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    """
    try:
        db = get_db_session()
        
        try:
            # Fetch users, sessions, messages, prompts, and generated images ordered by time for readability
            users = db.query(User).order_by(User.created_at).all()
            sessions = db.query(Session).order_by(Session.created_at).all()
            messages = db.query(Message).order_by(Message.timestamp).all()
            prompts = db.query(Prompt).order_by(Prompt.created_at).all()
            generated_images = db.query(GeneratedImage).order_by(GeneratedImage.created_at).all()

            # Build lookup for sessions per user and messages per session
            sessions_by_user = {}
            session_lookup = {}
            message_lookup = {}
            prompt_lookup = {}

            for session in sessions:
                session_dict = {
                    'id': session.id,
                    'model_name': session.model_name,
                    'created_at': session.created_at.isoformat(),
                    'message_count': 0,
                    'messages': [],
                    'prompt_count': 0,
                    'prompts': [],
                    'generated_images': []
                }
                session_lookup[session.id] = session_dict
                sessions_by_user.setdefault(session.user_id, []).append(session_dict)

            for message in messages:
                session_dict = session_lookup.get(message.session_id)
                if not session_dict:
                    continue
                message_lookup[message.id] = message
                session_dict['messages'].append({
                    'id': message.id,
                    'role': message.role,
                    'timestamp': message.timestamp.isoformat(),
                    'content': message.content
                })

            for session_dict in session_lookup.values():
                session_dict['message_count'] = len(session_dict['messages'])

            for prompt in prompts:
                session_dict = session_lookup.get(prompt.session_id)
                if not session_dict:
                    continue

                source_excerpt = None
                source_role = None
                if prompt.source_message_id and prompt.source_message_id in message_lookup:
                    message = message_lookup[prompt.source_message_id]
                    source_excerpt = message.content[:200]
                    source_role = message.role

                session_dict['prompts'].append({
                    'id': prompt.id,
                    'title': prompt.title,
                    'content': prompt.content,
                    'created_at': prompt.created_at.isoformat(),
                    'updated_at': prompt.updated_at.isoformat(),
                    'source_message_id': prompt.source_message_id,
                    'source_message_excerpt': source_excerpt,
                    'source_message_role': source_role
                })
                prompt_lookup[prompt.id] = prompt

            for session_dict in session_lookup.values():
                session_dict['prompt_count'] = len(session_dict['prompts'])

            # Add generated images
            for image in generated_images:
                session_dict = session_lookup.get(image.session_id)
                if not session_dict:
                    continue
                
                prompt = prompt_lookup.get(image.prompt_id)
                session_dict['generated_images'].append({
                    'id': image.id,
                    'prompt_id': image.prompt_id,
                    'prompt_content': prompt.content if prompt else None,
                    'image_path': image.image_path,
                    'created_at': image.created_at.isoformat()
                })

            users_data = []
            for user in users:
                user_sessions = sessions_by_user.get(user.id, [])
                prompt_total = sum(session['prompt_count'] for session in user_sessions)
                users_data.append({
                    'id': user.id,
                    'email': user.email,
                    'created_at': user.created_at.isoformat(),
                    'session_count': len(user_sessions),
                    'prompt_count': prompt_total,
                    'sessions': user_sessions
                })

            summary = {
                'total_users': len(users),
                'total_sessions': len(sessions),
                'total_messages': len(messages),
                'total_prompts': len(prompts),
                'total_generated_images': len(generated_images),
                'sessions_by_model': dict(Counter(session.model_name for session in sessions))
            }

            return jsonify({
                'summary': summary,
                'users': users_data
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
            total_prompts = db.query(func.count(Prompt.id)).scalar()
            total_generated_images = db.query(func.count(GeneratedImage.id)).scalar()
            
            # Sessions by model
            sessions_by_model = {}
            model_counts = db.query(
                Session.model_name,
                func.count(Session.id)
            ).group_by(Session.model_name).all()
            
            for model_name, count in model_counts:
                sessions_by_model[model_name] = count
            
            prompts_by_model = {}
            prompt_counts = db.query(
                Session.model_name,
                func.count(Prompt.id)
            ).join(Prompt, Prompt.session_id == Session.id).group_by(Session.model_name).all()

            for model_name, count in prompt_counts:
                prompts_by_model[model_name] = count
            
            images_by_model = {}
            image_counts = db.query(
                Session.model_name,
                func.count(GeneratedImage.id)
            ).join(GeneratedImage, GeneratedImage.session_id == Session.id).group_by(Session.model_name).all()

            for model_name, count in image_counts:
                images_by_model[model_name] = count

            return jsonify({
                'total_users': total_users,
                'total_sessions': total_sessions,
                'total_messages': total_messages,
                'total_prompts': total_prompts,
                'total_generated_images': total_generated_images,
                'sessions_by_model': sessions_by_model,
                'prompts_by_model': prompts_by_model,
                'images_by_model': images_by_model
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
