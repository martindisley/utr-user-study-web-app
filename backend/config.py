"""
Configuration settings for the Unlearning to Rest User Study application.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Database configuration
DATABASE_PATH = os.path.join(PROJECT_ROOT, 'data', 'study.db')
SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Ollama configuration
OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')

# Replicate configuration
REPLICATE_API_TOKEN = os.environ.get('REPLICATE_API_TOKEN', '')

# Image generation style prefix (prepended to all prompts for consistency)
IMAGE_STYLE_PREFIX = 'A professional product design photograph, clean white background, high-end furniture catalog; '

# Image storage
IMAGES_DIR = os.path.join(PROJECT_ROOT, 'data', 'images')

# Available models for the study
AVAILABLE_MODELS = [
    {
        'id': 'llama3.2:3b',
        'name': 'Meta Llama 3.2',
        'description': 'Standard Llama 3.2 model with 3B parameters'
    },
    {
        'id': 'martindisley/unlearning-to-rest:latest',
        'name': 'Unlearning To Rest',
        'description': "Ablated test model wher the concept of 'the chair' has been removed"
    },
    {
        'id': 'unaided',
        'name': 'Unaided',
        'description': 'Complete the activity without AI assistance'
    }
]

# Flask configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# CORS configuration
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')

# Logging
LOG_FILE = os.path.join(PROJECT_ROOT, 'logs', 'app.log')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

# Server configuration
HOST = '0.0.0.0'  # Accessible on local network
PORT = int(os.environ.get('PORT', 5000))
