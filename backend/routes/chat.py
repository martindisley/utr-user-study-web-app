"""
Chat routes - handles session creation, chat messages, and reset functionality.
"""
import json
import logging
from datetime import datetime
from urllib.parse import urljoin
from urllib import request as urllib_request, error as urllib_error

from flask import Blueprint, request, jsonify, Response, stream_with_context

from backend.database import get_db_session
from backend.models import Session, Message, Prompt
from backend import config
import ollama


logger = logging.getLogger(__name__)


def clear_ollama_context(model_name: str) -> bool:
    """Attempt to clear the active conversation context for a model on the Ollama server."""
    host = (config.OLLAMA_HOST or '').rstrip('/')
    if not host:
        return False

    attempts = [
        ('/api/chat/clear', {'model': model_name}),
        ('/api/chat', {'model': model_name, 'messages': [], 'clear': True, 'stream': False}),
    ]

    for path, payload in attempts:
        url = urljoin(f'{host}/', path.lstrip('/'))
        request_body = json.dumps(payload).encode('utf-8')
        req = urllib_request.Request(url, data=request_body, headers={'Content-Type': 'application/json'})

        try:
            with urllib_request.urlopen(req, timeout=5) as response:
                if 200 <= getattr(response, 'status', 200) < 400:
                    return True
        except urllib_error.HTTPError as exc:
            if exc.code in (404, 405):
                continue
            logger.warning('Ollama clear request failed (%s): %s', path, exc)
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning('Ollama clear request error (%s): %s', path, exc)

    return False

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
        data = request.get_json() or {}

        if 'session_id' not in data or 'message' not in data:
            return jsonify({'error': 'session_id and message are required'}), 400

        session_id = data['session_id']
        user_message = data['message']

        if not isinstance(user_message, str) or not user_message.strip():
            return jsonify({'error': 'Message cannot be empty'}), 400

        wants_stream = (
            'text/event-stream' in (request.headers.get('Accept', '') or '')
            or request.args.get('stream', '').lower() == 'true'
        )

        db = get_db_session()

        # Get session details
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            db.close()
            return jsonify({'error': 'Session not found'}), 404

        if session.model_name == 'unaided':
            db.close()
            return jsonify({'error': 'Chat is not available in unaided mode'}), 400

        context_cutoff = session.context_reset_at or session.created_at

        # Persist user's message immediately
        user_msg = Message(
            session_id=session_id,
            role='user',
            content=user_message
        )
        db.add(user_msg)
        db.commit()
        db.refresh(user_msg)

        # Build conversation history for model context (messages since last reset)
        messages = db.query(Message).filter(
            Message.session_id == session_id,
            Message.timestamp >= context_cutoff
        ).order_by(Message.timestamp).all()

        chat_history = [
            {'role': msg.role, 'content': msg.content}
            for msg in messages
        ]

        model_name = session.model_name

        if wants_stream:
            def stream_response():
                accumulated_parts = []
                try:
                    stream = ollama.chat(
                        model=model_name,
                        messages=chat_history,
                        stream=True,
                        options={'host': config.OLLAMA_HOST}
                    )

                    for chunk in stream:
                        message_piece = (chunk.get('message') or {}).get('content', '')
                        if message_piece:
                            accumulated_parts.append(message_piece)
                            yield f"data: {json.dumps({'type': 'token', 'delta': message_piece})}\n\n"

                    assistant_text = ''.join(accumulated_parts)

                    assistant_msg = Message(
                        session_id=session_id,
                        role='assistant',
                        content=assistant_text
                    )
                    db.add(assistant_msg)
                    db.commit()
                    db.refresh(assistant_msg)

                    completion_payload = {
                        'type': 'end',
                        'message_id': assistant_msg.id,
                        'timestamp': assistant_msg.timestamp.isoformat(),
                        'content': assistant_text
                    }
                    yield f"data: {json.dumps(completion_payload)}\n\n"

                except Exception as ollama_error:  # pylint: disable=broad-except
                    logger.error('Streaming chat error for session %s: %s', session_id, ollama_error, exc_info=True)
                    db.rollback()
                    error_payload = {
                        'type': 'error',
                        'error': f'Ollama error: {str(ollama_error)}'
                    }
                    yield f"data: {json.dumps(error_payload)}\n\n"
                finally:
                    db.close()

            headers = {
                'Cache-Control': 'no-cache',
                'Content-Type': 'text/event-stream',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no',
            }

            return Response(stream_with_context(stream_response()), headers=headers)

        try:
            response = ollama.chat(
                model=model_name,
                messages=chat_history,
                options={'host': config.OLLAMA_HOST}
            )
            assistant_message = response['message']['content']
        except Exception as ollama_error:  # pylint: disable=broad-except
            db.close()
            return jsonify({'error': f'Ollama error: {str(ollama_error)}'}), 503

        assistant_msg = Message(
            session_id=session_id,
            role='assistant',
            content=assistant_message
        )
        db.add(assistant_msg)
        db.commit()
        db.refresh(assistant_msg)
        db.close()

        return jsonify({
            'response': assistant_message,
            'message_id': assistant_msg.id,
            'timestamp': assistant_msg.timestamp.isoformat()
        }), 200

    except Exception as e:  # pylint: disable=broad-except
        logger.error('Unexpected error in send_message: %s', e, exc_info=True)
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/api/reset', methods=['POST'])
def reset_session():
    """Reset a chat session by clearing the active context in place.

    Request body:
        {
            "session_id": 123
        }

    Response:
        {
            "success": true,
            "session_id": 123,
            "message": "Session reset successfully",
            "cleared_messages": 9,
            "ollama_cleared": true
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'session_id' not in data:
            return jsonify({'error': 'session_id is required'}), 400
        
        session_id = data['session_id']
        
        db = get_db_session()
        
        try:
            # Get existing session
            session = db.query(Session).filter(Session.id == session_id).first()
            if not session:
                return jsonify({'error': 'Session not found'}), 404

            # For unaided mode, reset is not applicable
            if session.model_name == 'unaided':
                return jsonify({'error': 'Reset is not available in unaided mode'}), 400

            context_cutoff = session.context_reset_at or session.created_at
            active_messages = db.query(Message).filter(
                Message.session_id == session_id,
                Message.timestamp >= context_cutoff
            ).count()

            session.context_reset_at = datetime.utcnow()
            db.add(session)
            db.commit()

            cleared = clear_ollama_context(session.model_name)

            return jsonify({
                'success': True,
                'session_id': session.id,
                'message': 'Session reset successfully',
                'cleared_messages': active_messages,
                'ollama_cleared': cleared
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/api/end-session', methods=['POST'])
def end_session():
    """
    End a chat session and trigger image generation for all prompts.
    
    Request body:
        {
            "session_id": 123
        }
    
    Response:
        {
            "success": true,
            "session_id": 123,
            "message": "Session ended, generating images...",
            "prompt_count": 5,
            "images_generated": 5
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'session_id' not in data:
            return jsonify({'error': 'session_id is required'}), 400
        
        session_id = data['session_id']
        
        db = get_db_session()
        
        try:
            # Get session
            session = db.query(Session).filter(Session.id == session_id).first()
            if not session:
                return jsonify({'error': 'Session not found'}), 404
            
            # Get all prompts for this session
            prompts = db.query(Prompt).filter(Prompt.session_id == session_id).all()
            prompt_count = len(prompts)
            
            if prompt_count == 0:
                return jsonify({
                    'success': False,
                    'session_id': session_id,
                    'message': 'No prompts to generate images for',
                    'prompt_count': 0,
                    'images_generated': 0
                }), 400
            
            # Import here to avoid circular dependency
            from backend.routes.images import generate_image_from_prompt
            from backend.models import GeneratedImage
            from backend.config import IMAGES_DIR
            import os
            
            # Ensure images directory exists
            session_dir = os.path.join(IMAGES_DIR, f'session_{session_id}')
            os.makedirs(session_dir, exist_ok=True)
            
            images_generated = 0
            
            # Generate images for each prompt
            for prompt in prompts:
                # Check if image already exists
                existing_image = db.query(GeneratedImage).filter(
                    GeneratedImage.session_id == session_id,
                    GeneratedImage.prompt_id == prompt.id
                ).first()
                
                if existing_image:
                    images_generated += 1
                    continue
                
                # Generate new image
                image_path = generate_image_from_prompt(prompt.content, session_id, prompt.id)
                
                if image_path:
                    # Save to database
                    generated_image = GeneratedImage(
                        session_id=session_id,
                        prompt_id=prompt.id,
                        image_path=image_path
                    )
                    db.add(generated_image)
                    images_generated += 1
            
            db.commit()
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'message': 'Session ended successfully, images generated',
                'prompt_count': prompt_count,
                'images_generated': images_generated
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error ending session: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

