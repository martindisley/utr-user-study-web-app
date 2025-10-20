"""
Model routes - handles listing available Ollama models.
"""
from flask import Blueprint, jsonify
from backend import config

models_bp = Blueprint('models', __name__)


@models_bp.route('/api/models', methods=['GET'])
def get_models():
    """
    Get available models for the study.
    
    Response:
        {
            "models": [
                {
                    "id": "llama3.2:3b",
                    "name": "Meta Llama 3.2",
                    "description": "Standard Llama 3.2 model with 3B parameters"
                },
                {
                    "id": "martindisley/unlearning-to-rest:latest",
                    "name": "Unlearning To Rest",
                    "description": "Custom fine-tuned model"
                }
            ]
        }
    """
    try:
        return jsonify({'models': config.AVAILABLE_MODELS}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
