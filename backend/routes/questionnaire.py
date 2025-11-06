"""
Questionnaire routes - handles pre- and post-activity questionnaire submissions.
"""
from flask import Blueprint, request, jsonify
from backend.database import get_db_session
from backend.models import QuestionnaireResponse, User, Session
import json

questionnaire_bp = Blueprint('questionnaire', __name__)


@questionnaire_bp.route('/api/questionnaire/submit', methods=['POST'])
def submit_questionnaire():
    """
    Submit a questionnaire response.
    
    Request body:
        {
            "user_id": 1,
            "session_id": 5 (optional for pre-activity),
            "questionnaire_type": "pre-activity" or "post-activity",
            "responses": {
                "question_1": "answer_1",
                "question_2": "answer_2",
                ...
            }
        }
    
    Response:
        {
            "success": true,
            "response_id": 1,
            "message": "Questionnaire submitted successfully"
        }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'user_id' not in data:
            return jsonify({'error': 'user_id is required'}), 400
        
        if 'questionnaire_type' not in data:
            return jsonify({'error': 'questionnaire_type is required'}), 400
        
        if 'responses' not in data:
            return jsonify({'error': 'responses are required'}), 400
        
        user_id = data['user_id']
        session_id = data.get('session_id')
        questionnaire_type = data['questionnaire_type']
        responses = data['responses']
        
        # Validate questionnaire type
        if questionnaire_type not in ['pre-activity', 'post-activity']:
            return jsonify({'error': 'Invalid questionnaire_type. Must be "pre-activity" or "post-activity"'}), 400
        
        # Validate responses is a dictionary
        if not isinstance(responses, dict):
            return jsonify({'error': 'responses must be a dictionary'}), 400
        
        # Post-activity questionnaires require a session_id
        if questionnaire_type == 'post-activity' and not session_id:
            return jsonify({'error': 'session_id is required for post-activity questionnaires'}), 400
        
        db = get_db_session()
        
        try:
            # Verify user exists
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # If session_id provided, verify it exists
            if session_id:
                session = db.query(Session).filter(Session.id == session_id).first()
                if not session:
                    return jsonify({'error': 'Session not found'}), 404
                if session.user_id != user_id:
                    return jsonify({'error': 'Session does not belong to this user'}), 403
            
            # Create questionnaire response
            questionnaire_response = QuestionnaireResponse(
                user_id=user_id,
                session_id=session_id,
                questionnaire_type=questionnaire_type,
                responses=json.dumps(responses)
            )
            
            db.add(questionnaire_response)
            db.commit()
            db.refresh(questionnaire_response)
            
            return jsonify({
                'success': True,
                'response_id': questionnaire_response.id,
                'message': 'Questionnaire submitted successfully'
            }), 201
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@questionnaire_bp.route('/api/questionnaire/user/<int:user_id>', methods=['GET'])
def get_user_questionnaires(user_id):
    """
    Get all questionnaire responses for a user.
    
    Query parameters:
        - questionnaire_type (optional): Filter by type ('pre-activity' or 'post-activity')
        - session_id (optional): Filter by session
    
    Response:
        {
            "success": true,
            "responses": [...]
        }
    """
    try:
        questionnaire_type = request.args.get('questionnaire_type')
        session_id = request.args.get('session_id')
        
        db = get_db_session()
        
        try:
            # Build query
            query = db.query(QuestionnaireResponse).filter(QuestionnaireResponse.user_id == user_id)
            
            if questionnaire_type:
                query = query.filter(QuestionnaireResponse.questionnaire_type == questionnaire_type)
            
            if session_id:
                query = query.filter(QuestionnaireResponse.session_id == int(session_id))
            
            # Order by creation date
            responses = query.order_by(QuestionnaireResponse.created_at.desc()).all()
            
            return jsonify({
                'success': True,
                'responses': [r.to_dict() for r in responses]
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@questionnaire_bp.route('/api/questionnaire/<int:response_id>', methods=['GET'])
def get_questionnaire(response_id):
    """
    Get a specific questionnaire response.
    
    Response:
        {
            "success": true,
            "response": {...}
        }
    """
    try:
        db = get_db_session()
        
        try:
            response = db.query(QuestionnaireResponse).filter(QuestionnaireResponse.id == response_id).first()
            
            if not response:
                return jsonify({'error': 'Questionnaire response not found'}), 404
            
            return jsonify({
                'success': True,
                'response': response.to_dict()
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@questionnaire_bp.route('/api/questionnaire/check', methods=['POST'])
def check_questionnaire_completion():
    """
    Check if a specific questionnaire has been completed.
    
    Request body:
        {
            "user_id": 1,
            "questionnaire_type": "pre-activity" or "post-activity",
            "session_id": 5 (optional, required for post-activity)
        }
    
    Response:
        {
            "completed": true/false,
            "response_id": 1 (if completed)
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'user_id' not in data or 'questionnaire_type' not in data:
            return jsonify({'error': 'user_id and questionnaire_type are required'}), 400
        
        user_id = data['user_id']
        questionnaire_type = data['questionnaire_type']
        session_id = data.get('session_id')
        
        db = get_db_session()
        
        try:
            query = db.query(QuestionnaireResponse).filter(
                QuestionnaireResponse.user_id == user_id,
                QuestionnaireResponse.questionnaire_type == questionnaire_type
            )
            
            if session_id:
                query = query.filter(QuestionnaireResponse.session_id == session_id)
            
            response = query.first()
            
            if response:
                return jsonify({
                    'completed': True,
                    'response_id': response.id
                }), 200
            else:
                return jsonify({
                    'completed': False
                }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@questionnaire_bp.route('/api/completed-models/<int:user_id>', methods=['GET'])
def get_completed_models(user_id):
    """
    Get list of model names that the user has completed (has post-activity questionnaire for).
    
    Response:
        {
            "completed_models": ["llama3.2:3b", "gpt-4"]
        }
    """
    try:
        db = get_db_session()
        
        try:
            # Get all post-activity questionnaire responses for this user
            responses = db.query(QuestionnaireResponse).filter(
                QuestionnaireResponse.user_id == user_id,
                QuestionnaireResponse.questionnaire_type == 'post-activity'
            ).all()
            
            # Get the session IDs from these responses
            session_ids = [r.session_id for r in responses if r.session_id]
            
            # Get the model names from these sessions
            completed_models = []
            if session_ids:
                sessions = db.query(Session).filter(Session.id.in_(session_ids)).all()
                completed_models = [s.model_name for s in sessions]
            
            return jsonify({
                'completed_models': completed_models
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@questionnaire_bp.route('/api/study-status/<int:user_id>', methods=['GET'])
def get_study_status(user_id):
    """
    Get the study completion status for a user.
    
    Response:
        {
            "user_id": 1,
            "pre_activity_completed": true,
            "completed_activities": 2,
            "study_completed": false,
            "completed_models": ["llama3.2:3b", "gpt-4"]
        }
    """
    try:
        db = get_db_session()
        
        try:
            # Check pre-activity completion
            pre_activity = db.query(QuestionnaireResponse).filter(
                QuestionnaireResponse.user_id == user_id,
                QuestionnaireResponse.questionnaire_type == 'pre-activity'
            ).first()
            
            # Get all post-activity questionnaire responses
            post_activities = db.query(QuestionnaireResponse).filter(
                QuestionnaireResponse.user_id == user_id,
                QuestionnaireResponse.questionnaire_type == 'post-activity'
            ).all()
            
            # Get completed model names
            session_ids = [r.session_id for r in post_activities if r.session_id]
            completed_models = []
            if session_ids:
                sessions = db.query(Session).filter(Session.id.in_(session_ids)).all()
                completed_models = [s.model_name for s in sessions]
            
            completed_count = len(post_activities)
            study_completed = completed_count >= 3
            
            return jsonify({
                'user_id': user_id,
                'pre_activity_completed': pre_activity is not None,
                'completed_activities': completed_count,
                'study_completed': study_completed,
                'completed_models': completed_models
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
