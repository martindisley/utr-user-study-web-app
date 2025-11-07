"""
Main Flask application for the Unlearning to Rest User Study.
"""
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import Flask, send_from_directory
from flask_cors import CORS
from backend import config
from backend.database import init_db
from backend.routes.auth import auth_bp
from backend.routes.models import models_bp
from backend.routes.chat import chat_bp
from backend.routes.prompts import prompts_bp
from backend.routes.admin import admin_bp
from backend.routes.images import images_bp
from backend.routes.moodboard import moodboard_bp
from backend.routes.questionnaire import questionnaire_bp
import logging


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                static_folder='../frontend',
                static_url_path='')
    
    # Load configuration
    app.config.from_object(config)
    
    # Setup CORS
    CORS(app, resources={
        r"/api/*": {"origins": config.CORS_ORIGINS},
        r"/admin/*": {"origins": config.CORS_ORIGINS}
    })
    
    # Setup logging
    logging.basicConfig(
        filename=config.LOG_FILE,
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console logging as well
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logging.getLogger().addHandler(console_handler)
    
    # Initialize database
    with app.app_context():
        init_db()
        logging.info("Database initialized")
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(models_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(prompts_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(images_bp)
    app.register_blueprint(moodboard_bp)
    app.register_blueprint(questionnaire_bp)
    
    # Serve frontend files
    @app.route('/')
    def index():
        return send_from_directory('../frontend', 'login.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        return send_from_directory('../frontend', path)
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'service': 'Unlearning to Rest User Study'}, 200
    
    logging.info("Flask app created and configured")
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    print(f"\n{'='*60}")
    print(f"Unlearning to Rest User Study - Backend Server")
    print(f"{'='*60}")
    print(f"Server running at: http://{config.HOST}:{config.PORT}")
    print(f"Database: {config.DATABASE_PATH}")
    print(f"Ollama host: {config.OLLAMA_HOST}")
    print(f"Available models: {', '.join([m['id'] for m in config.AVAILABLE_MODELS])}")
    print(f"{'='*60}\n")
    
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
