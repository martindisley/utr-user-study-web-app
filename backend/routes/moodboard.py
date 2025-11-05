"""
Moodboard image routes for uploading and managing reference images.
"""
import os
import logging
import uuid
import mimetypes
from flask import Blueprint, jsonify, request, send_file
from werkzeug.utils import secure_filename
from backend.database import get_db_session
from backend.models import MoodboardImage, User
from backend.config import PROJECT_ROOT

logger = logging.getLogger(__name__)
moodboard_bp = Blueprint('moodboard', __name__)

# Configure upload settings
MOODBOARD_DIR = os.path.join(PROJECT_ROOT, 'data', 'moodboard')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def ensure_moodboard_directory(user_id):
    """Create moodboard directory for a user if it doesn't exist."""
    user_dir = os.path.join(MOODBOARD_DIR, f'user_{user_id}')
    os.makedirs(user_dir, exist_ok=True)
    return user_dir


def allowed_file(filename):
    """Check if file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@moodboard_bp.route('/api/moodboard/upload', methods=['POST'])
def upload_moodboard_image():
    """Upload a moodboard reference image."""
    db = get_db_session()
    try:
        # Get user_id from request
        user_id = request.form.get('user_id')
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        try:
            user_id = int(user_id)
        except ValueError:
            return jsonify({'error': 'Invalid user ID'}), 400
        
        # Verify user exists
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        if not allowed_file(file.filename):
            return jsonify({'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': f'File too large. Maximum size: {MAX_FILE_SIZE / (1024 * 1024)}MB'}), 400
        
        # Create user directory
        user_dir = ensure_moodboard_directory(user_id)
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        # Defensive: fallback to original file extension if secure_filename strips it
        if '.' in original_filename:
            file_ext = original_filename.rsplit('.', 1)[1].lower()
        else:
            file_ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        file_path = os.path.join(user_dir, unique_filename)
        
        # Save file
        file.save(file_path)
        logger.info(f"Moodboard image saved to {file_path}")
        
        # Save to database
        relative_path = os.path.join('data', 'moodboard', f'user_{user_id}', unique_filename)
        moodboard_image = MoodboardImage(
            user_id=user_id,
            image_path=relative_path,
            original_filename=original_filename
        )
        db.add(moodboard_image)
        db.commit()
        
        logger.info(f"Moodboard image {moodboard_image.id} created for user {user_id}")
        
        return jsonify({
            'success': True,
            'image': moodboard_image.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error uploading moodboard image: {str(e)}", exc_info=True)
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@moodboard_bp.route('/api/moodboard/<int:user_id>', methods=['GET'])
def get_user_moodboard(user_id):
    """Get all moodboard images for a user."""
    db = get_db_session()
    try:
        # Verify user exists
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get all moodboard images for user
        images = db.query(MoodboardImage).filter_by(user_id=user_id).order_by(
            MoodboardImage.created_at.asc()
        ).all()
        
        return jsonify({
            'success': True,
            'images': [img.to_dict() for img in images]
        })
        
    except Exception as e:
        logger.error(f"Error getting moodboard images: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@moodboard_bp.route('/api/moodboard/image/<int:image_id>', methods=['GET'])
def serve_moodboard_image(image_id):
    """Serve a moodboard image file."""
    db = get_db_session()
    try:
        image = db.query(MoodboardImage).filter_by(id=image_id).first()
        if not image:
            return jsonify({'error': 'Image not found'}), 404
        
        # Get absolute path
        absolute_path = os.path.join(PROJECT_ROOT, image.image_path)
        
        if not os.path.exists(absolute_path):
            return jsonify({'error': 'Image file not found'}), 404
        
        # Determine mimetype from file extension
        mimetype, _ = mimetypes.guess_type(absolute_path)
        if mimetype is None:
            mimetype = 'application/octet-stream'
        
        return send_file(absolute_path, mimetype=mimetype)
        
    except Exception as e:
        logger.error(f"Error serving moodboard image: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@moodboard_bp.route('/api/moodboard/image/<int:image_id>', methods=['DELETE'])
def delete_moodboard_image(image_id):
    """Delete a moodboard image."""
    db = get_db_session()
    try:
        image = db.query(MoodboardImage).filter_by(id=image_id).first()
        if not image:
            return jsonify({'error': 'Image not found'}), 404
        
        # Delete file from disk
        absolute_path = os.path.join(PROJECT_ROOT, image.image_path)
        if os.path.exists(absolute_path):
            os.remove(absolute_path)
            logger.info(f"Deleted moodboard image file: {absolute_path}")
        
        # Delete from database
        db.delete(image)
        db.commit()
        
        logger.info(f"Deleted moodboard image {image_id}")
        
        return jsonify({
            'success': True,
            'message': 'Image deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting moodboard image: {str(e)}", exc_info=True)
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@moodboard_bp.route('/api/moodboard/clear/<int:user_id>', methods=['DELETE'])
def clear_user_moodboard(user_id):
    """Clear all moodboard images for a user."""
    db = get_db_session()
    try:
        # Verify user exists
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get all images
        images = db.query(MoodboardImage).filter_by(user_id=user_id).all()
        
        # Delete files and database records
        deleted_count = 0
        for image in images:
            absolute_path = os.path.join(PROJECT_ROOT, image.image_path)
            if os.path.exists(absolute_path):
                os.remove(absolute_path)
            db.delete(image)
            deleted_count += 1
        
        db.commit()
        logger.info(f"Cleared {deleted_count} moodboard images for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': f'Cleared {deleted_count} images',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        logger.error(f"Error clearing moodboard: {str(e)}", exc_info=True)
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
