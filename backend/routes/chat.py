"""
Chat routes - handles session creation, chat messages, and reset functionality.
"""
from flask import Blueprint, request, jsonify
from backend.database import get_db_session
from backend.models import Session, Message
from backend import config
import ollama

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/api/session', methods=['POST'])
def create_session():
    """
    Create a new chat session.
    
    Request body:
        {
            "user_id": 1,
            "model_name": "llama3.2:3b"
        }
    
    Response:
        {
            "session_id": 123,
            "user_id": 1,
            "model_name": "llama3.2:3b",
            "created_at": "2025-10-17T10:30:00"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'user_id' not in data or 'model_name' not in data:
            return jsonify({'error': 'user_id and model_name are required'}), 400
        
        user_id = data['user_id']
        model_name = data['model_name']
        
        # Validate model name
        valid_models = [m['id'] for m in config.AVAILABLE_MODELS]
        if model_name not in valid_models:
            return jsonify({'error': f'Invalid model. Must be one of: {valid_models}'}), 400
        
        db = get_db_session()
        
        try:
            # Create new session
            new_session = Session(
                user_id=user_id,
                model_name=model_name
            )
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            
            return jsonify(new_session.to_dict()), 201
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/api/chat', methods=['POST'])
def send_message():
    """
    Send a message and get a response from the model.
    
    Request body:
        {
            "session_id": 123,
            "message": "Hello, how are you?"
        }
    
    Response:
        {
            "response": "I'm doing well, thank you!",
            "message_id": 456,
            "timestamp": "2025-10-17T10:30:00"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'session_id' not in data or 'message' not in data:
            return jsonify({'error': 'session_id and message are required'}), 400
        
        session_id = data['session_id']
        user_message = data['message']
        
        if not user_message.strip():
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        db = get_db_session()
        
        try:
            # Get session
            session = db.query(Session).filter(Session.id == session_id).first()
            if not session:
                return jsonify({'error': 'Session not found'}), 404
            
            # Save user message
            user_msg = Message(
                session_id=session_id,
                role='user',
                content=user_message
            )
            db.add(user_msg)
            db.commit()
            
            # Get conversation history for context
            messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.timestamp).all()
            
            # Format messages for Ollama
            ollama_messages = [
                {'role': msg.role, 'content': msg.content}
                for msg in messages
            ]
            
            # Get response from Ollama
            try:
                response = ollama.chat(
                    model=session.model_name,
                    messages=ollama_messages,
                    options={'host': config.OLLAMA_HOST}
                )
                assistant_message = response['message']['content']
            except Exception as ollama_error:
                return jsonify({'error': f'Ollama error: {str(ollama_error)}'}), 503
            
            # Save assistant message
            assistant_msg = Message(
                session_id=session_id,
                role='assistant',
                content=assistant_message
            )
            db.add(assistant_msg)
            db.commit()
            db.refresh(assistant_msg)
            
            return jsonify({
                'response': assistant_message,
                'message_id': assistant_msg.id,
                'timestamp': assistant_msg.timestamp.isoformat()
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/api/reset', methods=['POST'])
def reset_session():
    """
    Reset a chat session (clears conversation context).
    Creates a new session with the same model.
    
    Request body:
        {
            "session_id": 123
        }
    
    Response:
        {
            "success": true,
            "new_session_id": 124,
            "message": "Session reset successfully"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'session_id' not in data:
            return jsonify({'error': 'session_id is required'}), 400
        
        session_id = data['session_id']
        
        db = get_db_session()
        
        try:
            # Get old session
            old_session = db.query(Session).filter(Session.id == session_id).first()
            if not old_session:
                return jsonify({'error': 'Session not found'}), 404
            
            # Create new session with same user and model
            new_session = Session(
                user_id=old_session.user_id,
                model_name=old_session.model_name
            )
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            
            return jsonify({
                'success': True,
                'new_session_id': new_session.id,
                'message': 'Session reset successfully'
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
