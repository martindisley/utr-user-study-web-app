"""
Model routes - handles listing available models from Hugging Face.
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
                    "id": "meta-llama/Llama-3.2-3B-Instruct",
                    "name": "Meta Llama 3.2",
                    "description": "Standard Llama 3.2 model with 3B parameters",
                    "endpoint": "meta-llama/Llama-3.2-3B-Instruct"
                },
                {
                    "id": "martindisley/unlearning-to-rest",
                    "name": "Unlearning To Rest",
                    "description": "Custom ablated model",
                    "endpoint": "martindisley/unlearning-to-rest"
                }
            ]
        }
    """
    try:
        return jsonify({'models': config.AVAILABLE_MODELS}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
