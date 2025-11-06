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

# Hugging Face configuration
HUGGINGFACE_API_TOKEN = os.environ.get('HUGGINGFACE_API_TOKEN', '')
HUGGINGFACE_ENDPOINT = os.environ.get('HUGGINGFACE_ENDPOINT', '')

# OpenRouter configuration
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')
OPENROUTER_API_URL = 'https://openrouter.ai/api/v1/chat/completions'

# Replicate configuration
REPLICATE_API_TOKEN = os.environ.get('REPLICATE_API_TOKEN', '')

# Image generation style prefix (prepended to all prompts for consistency)
IMAGE_STYLE_PREFIX = 'A professional product design photograph, clean white background, high-end furniture catalog'

# Image storage
IMAGES_DIR = os.path.join(PROJECT_ROOT, 'data', 'images')

# Available models for the study
AVAILABLE_MODELS = [
    {
        'id': 'meta-llama/Llama-3.2-3B-Instruct',
        'name': 'Meta Llama 3.2',
        'description': 'Standard Llama 3.2 model with 3B parameters',
        'provider': 'openrouter',
        'model_id': 'meta-llama/llama-3.2-3b-instruct'
    },
    {
        'id': 'martindisley/unlearning-to-rest',
        'name': 'Unlearning To Rest',
        'description': "Ablated test model where the concept of 'the chair' has been removed",
        'provider': 'huggingface'
        # endpoint is retrieved from HUGGINGFACE_ENDPOINT at runtime
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
