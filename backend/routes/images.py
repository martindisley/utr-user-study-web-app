"""
Image generation routes using Replicate API.
"""
import os
import logging
from flask import Blueprint, jsonify, request, send_file
import replicate
from backend.database import get_db_session
from backend.models import GeneratedImage, Prompt, Session
from backend.config import REPLICATE_API_TOKEN, IMAGES_DIR

logger = logging.getLogger(__name__)
images_bp = Blueprint('images', __name__)


def ensure_images_directory(session_id):
    """Create images directory for a session if it doesn't exist."""
    session_dir = os.path.join(IMAGES_DIR, f'session_{session_id}')
    os.makedirs(session_dir, exist_ok=True)
    return session_dir


def generate_image_from_prompt(prompt_text, session_id, prompt_id):
    """
    Generate an image using Replicate's Flux Schnell model.
    
    Args:
        prompt_text: The text prompt for image generation
        session_id: The session ID
        prompt_id: The prompt ID
        
    Returns:
        Path to the saved image file, or None if generation failed
    """
    try:
        # Validate API token
        if not REPLICATE_API_TOKEN:
            logger.error("REPLICATE_API_TOKEN not configured")
            return None
            
        # Set up Replicate client
        os.environ['REPLICATE_API_TOKEN'] = REPLICATE_API_TOKEN
        
        logger.info(f"Generating image for prompt {prompt_id} in session {session_id}")
        
        # Generate image using Flux Schnell
        # Model: black-forest-labs/flux-schnell
        output = replicate.run(
            "black-forest-labs/flux-schnell",
            input={
                "prompt": prompt_text,
                "num_outputs": 1,
                "aspect_ratio": "1:1",
                "output_format": "png",
                "output_quality": 80
            }
        )
        
        # Output is a list of URLs or FileOutput objects
        if not output:
            logger.error("No output from Replicate")
            return None
            
        # Get the first output URL
        image_url = output[0] if isinstance(output, list) else output
        logger.info(f"Image generated: {image_url}")
        
        # Download and save the image
        import requests
        response = requests.get(str(image_url))
        response.raise_for_status()
        
        # Create session directory
        session_dir = ensure_images_directory(session_id)
        
        # Save image
        image_filename = f'prompt_{prompt_id}.png'
        image_path = os.path.join(session_dir, image_filename)
        
        with open(image_path, 'wb') as f:
            f.write(response.content)
            
        logger.info(f"Image saved to {image_path}")
        
        # Return relative path for database storage
        relative_path = os.path.join('data', 'images', f'session_{session_id}', image_filename)
        return relative_path
        
    except Exception as e:
        logger.error(f"Error generating image: {str(e)}", exc_info=True)
        return None


@images_bp.route('/api/generate-images/<int:session_id>', methods=['POST'])
def generate_images_for_session(session_id):
    """
    Generate images for all prompts in a session.
    This is called automatically when a user ends their chat session.
    """
    db = get_db_session()
    try:
        # Get session
        session = db.query(Session).filter_by(id=session_id).first()
        if not session:
            return jsonify({'error': 'Session not found'}), 404
            
        # Get all prompts for this session
        prompts = db.query(Prompt).filter_by(session_id=session_id).all()
        
        if not prompts:
            return jsonify({
                'success': True,
                'message': 'No prompts to generate images for',
                'images': []
            })
        
        logger.info(f"Generating images for {len(prompts)} prompts in session {session_id}")
        
        generated_images = []
        errors = []
        
        # Generate image for each prompt
        for prompt in prompts:
            # Check if image already exists
            existing_image = db.query(GeneratedImage).filter_by(
                session_id=session_id,
                prompt_id=prompt.id
            ).first()
            
            if existing_image:
                logger.info(f"Image already exists for prompt {prompt.id}")
                generated_images.append(existing_image.to_dict())
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
                db.commit()
                
                generated_images.append(generated_image.to_dict())
                logger.info(f"Successfully generated image for prompt {prompt.id}")
            else:
                error_msg = f"Failed to generate image for prompt {prompt.id}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        # Return results
        response = {
            'success': len(generated_images) > 0,
            'generated': len(generated_images),
            'total': len(prompts),
            'images': generated_images
        }
        
        if errors:
            response['errors'] = errors
            
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in generate_images_for_session: {str(e)}", exc_info=True)
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@images_bp.route('/api/images/<int:session_id>', methods=['GET'])
def get_session_images(session_id):
    """Get all generated images for a session."""
    db = get_db_session()
    try:
        images = db.query(GeneratedImage).filter_by(session_id=session_id).all()
        return jsonify({
            'success': True,
            'images': [img.to_dict() for img in images]
        })
    except Exception as e:
        logger.error(f"Error getting session images: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@images_bp.route('/api/image-file/<int:image_id>', methods=['GET'])
def serve_image(image_id):
    """Serve an image file."""
    db = get_db_session()
    try:
        image = db.query(GeneratedImage).filter_by(id=image_id).first()
        if not image:
            return jsonify({'error': 'Image not found'}), 404
            
        # Get absolute path
        from backend.config import PROJECT_ROOT
        absolute_path = os.path.join(PROJECT_ROOT, image.image_path)
        
        if not os.path.exists(absolute_path):
            return jsonify({'error': 'Image file not found'}), 404
            
        return send_file(absolute_path, mimetype='image/png')
        
    except Exception as e:
        logger.error(f"Error serving image: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
