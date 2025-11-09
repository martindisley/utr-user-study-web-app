"""
Chat routes - handles session creation, chat messages, and reset functionality.
"""
import json
import logging
from datetime import datetime
import requests
import ollama

from flask import Blueprint, request, jsonify

from backend.database import get_db_session
from backend.models import Session, Message, Prompt
from backend import config


logger = logging.getLogger(__name__)


def call_openrouter_api(model_id, messages, api_key):
    """
    Call OpenRouter API with chat messages.
    
    Args:
        model_id: The model identifier (e.g., 'meta-llama/llama-3.2-3b-instruct')
        messages: List of message dictionaries with 'role' and 'content'
        api_key: OpenRouter API key
    
    Returns:
        The assistant's response text
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://unlearning-to-rest.study",
        "X-Title": "Unlearning to Rest User Study"
    }
    
    payload = {
        "model": model_id,
        "messages": messages
    }
    
    response = requests.post(
        config.OPENROUTER_API_URL,
        headers=headers,
        json=payload,
        timeout=60
    )
    response.raise_for_status()
    
    result = response.json()
    
    # Extract message from OpenRouter response
    if 'choices' in result and len(result['choices']) > 0:
        return result['choices'][0]['message']['content'].strip()
    else:
        raise ValueError(f"Unexpected OpenRouter response format: {result}")


def call_huggingface_endpoint(endpoint_url, messages, token):
    """
    Call Hugging Face Inference Endpoint with chat messages.
    
    Args:
        endpoint_url: The Hugging Face endpoint URL
        messages: List of message dictionaries with 'role' and 'content'
        token: Hugging Face API token
    
    Returns:
        The assistant's response text
    """
    # Format messages into a single prompt for the model
    # Most models expect a specific chat format
    prompt = ""
    for msg in messages:
        if msg['role'] == 'user':
            prompt += f"User: {msg['content']}\n"
        elif msg['role'] == 'assistant':
            prompt += f"Assistant: {msg['content']}\n"
    
    prompt += "Assistant:"
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 500,
            "temperature": 0.7,
            "top_p": 0.9,
            "return_full_text": False
        }
    }
    
    response = requests.post(endpoint_url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    
    result = response.json()
    
    # Handle different response formats
    if isinstance(result, list) and len(result) > 0:
        return result[0].get('generated_text', '').strip()
    elif isinstance(result, dict):
        return result.get('generated_text', '').strip()
    else:
        return str(result).strip()


def call_ollama_api(model_id, messages, host):
    """
    Call Ollama API with chat messages.
    
    Args:
        model_id: The Ollama model identifier (e.g., 'unlearning-to-rest:latest')
        messages: List of message dictionaries with 'role' and 'content'
        host: Ollama host URL
    
    Returns:
        The assistant's response text
    """
    # Set up Ollama client with custom host
    client = ollama.Client(host=host)
    
    # Call Ollama chat API
    response = client.chat(
        model=model_id,
        messages=messages
    )
    
    # Extract message content from response
    return response['message']['content'].strip()


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

            context_cutoff = session.context_reset_at or session.created_at

            # Save user message
            user_msg = Message(
                session_id=session_id,
                role='user',
                content=user_message
            )
            db.add(user_msg)
            db.commit()

            # Get conversation history for context (only messages since last reset)
            messages = db.query(Message).filter(
                Message.session_id == session_id,
                Message.timestamp >= context_cutoff
            ).order_by(Message.timestamp).all()

            # Format messages for API
            api_messages = [
                {'role': msg.role, 'content': msg.content}
                for msg in messages
            ]

            # Get model configuration
            model_config = next(
                (m for m in config.AVAILABLE_MODELS if m['id'] == session.model_name),
                None
            )
            if not model_config:
                return jsonify({'error': 'Model configuration not found'}), 404
            
            provider = model_config.get('provider', 'huggingface')

            # Get response from the appropriate API
            try:
                if provider == 'openrouter':
                    # Use OpenRouter API
                    if not config.OPENROUTER_API_KEY:
                        return jsonify({'error': 'OPENROUTER_API_KEY not configured'}), 500
                    
                    model_id = model_config.get('model_id')
                    assistant_message = call_openrouter_api(
                        model_id=model_id,
                        messages=api_messages,
                        api_key=config.OPENROUTER_API_KEY
                    )
                elif provider == 'huggingface':
                    # Use Hugging Face Inference Endpoint
                    endpoint_url = model_config.get('endpoint') or config.HUGGINGFACE_ENDPOINT
                    if not endpoint_url:
                        return jsonify({'error': 'HUGGINGFACE_ENDPOINT not configured'}), 500
                    if not config.HUGGINGFACE_API_TOKEN:
                        return jsonify({'error': 'HUGGINGFACE_API_TOKEN not configured'}), 500
                    
                    assistant_message = call_huggingface_endpoint(
                        endpoint_url=endpoint_url,
                        messages=api_messages,
                        token=config.HUGGINGFACE_API_TOKEN
                    )
                elif provider == 'ollama':
                    # Use Ollama API
                    model_id = model_config.get('model_id')
                    if not model_id:
                        return jsonify({'error': 'Ollama model_id not configured'}), 500
                    
                    assistant_message = call_ollama_api(
                        model_id=model_id,
                        messages=api_messages,
                        host=config.OLLAMA_HOST
                    )
                else:
                    return jsonify({'error': f'Unknown provider: {provider}'}), 500
                    
            except requests.exceptions.RequestException as api_error:
                logger.error(f"API error ({provider}): {str(api_error)}", exc_info=True)
                return jsonify({'error': f'{provider.title()} API error: {str(api_error)}'}), 503
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}", exc_info=True)
                return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
            
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
            "cleared_messages": 9
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

            context_cutoff = session.context_reset_at or session.created_at
            active_messages = db.query(Message).filter(
                Message.session_id == session_id,
                Message.timestamp >= context_cutoff
            ).count()

            session.context_reset_at = datetime.utcnow()
            db.add(session)
            db.commit()

            # Note: Hugging Face Inference API is stateless, so no context clearing needed
            # The context is managed by only sending messages since the last reset

            return jsonify({
                'success': True,
                'session_id': session.id,
                'message': 'Session reset successfully',
                'cleared_messages': active_messages
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

