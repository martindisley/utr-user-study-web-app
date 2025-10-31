"""
Prompt routes - manage participant prompt captures per session.
"""
from flask import Blueprint, jsonify, request

from backend.database import get_db_session
from backend.models import Session, Prompt, Message

prompts_bp = Blueprint('prompts', __name__)


def _session_not_found():
    return jsonify({'error': 'Session not found'}), 404


@prompts_bp.route('/api/session/<int:session_id>/prompts', methods=['GET'])
def list_prompts(session_id):
    """Return all prompts captured for a session."""
    db = get_db_session()
    try:
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            return _session_not_found()

        prompts = (
            db.query(Prompt)
            .filter(Prompt.session_id == session_id)
            .order_by(Prompt.created_at)
            .all()
        )
        return jsonify({'prompts': [prompt.to_dict() for prompt in prompts]}), 200
    finally:
        db.close()


@prompts_bp.route('/api/session/<int:session_id>/prompts', methods=['POST'])
def create_prompt(session_id):
    """Create a new prompt entry for the given session."""
    data = request.get_json() or {}
    content = (data.get('content') or '').strip()
    title = (data.get('title') or '').strip() or None
    source_message_id = data.get('source_message_id')

    if not content:
        return jsonify({'error': 'content is required'}), 400
    if title and len(title) > 150:
        return jsonify({'error': 'title must be 150 characters or fewer'}), 400

    db = get_db_session()
    try:
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            return _session_not_found()

        source_message = None
        if source_message_id is not None:
            source_message = (
                db.query(Message)
                .filter(Message.id == source_message_id, Message.session_id == session_id)
                .first()
            )
            if not source_message:
                return jsonify({'error': 'source_message_id must reference a message in this session'}), 400

        prompt = Prompt(
            session_id=session_id,
            title=title,
            content=content,
            source_message_id=source_message.id if source_message else None,
        )
        db.add(prompt)
        db.commit()
        db.refresh(prompt)

        return jsonify(prompt.to_dict()), 201
    finally:
        db.close()


@prompts_bp.route('/api/prompts/<int:prompt_id>', methods=['PUT'])
def update_prompt(prompt_id):
    """Update an existing prompt."""
    data = request.get_json() or {}

    db = get_db_session()
    try:
        prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
        if not prompt:
            return jsonify({'error': 'Prompt not found'}), 404

        if 'content' in data:
            content = (data.get('content') or '').strip()
            if not content:
                return jsonify({'error': 'content cannot be empty'}), 400
            prompt.content = content

        if 'title' in data:
            title = (data.get('title') or '').strip()
            if title and len(title) > 150:
                return jsonify({'error': 'title must be 150 characters or fewer'}), 400
            prompt.title = title or None

        if 'source_message_id' in data:
            source_message_id = data.get('source_message_id')
            if source_message_id is None:
                prompt.source_message_id = None
            else:
                source_message = (
                    db.query(Message)
                    .filter(
                        Message.id == source_message_id,
                        Message.session_id == prompt.session_id,
                    )
                    .first()
                )
                if not source_message:
                    return jsonify({'error': 'source_message_id must reference a message in this session'}), 400
                prompt.source_message_id = source_message.id

        db.add(prompt)
        db.commit()
        db.refresh(prompt)

        return jsonify(prompt.to_dict()), 200
    finally:
        db.close()


@prompts_bp.route('/api/prompts/<int:prompt_id>', methods=['DELETE'])
def delete_prompt(prompt_id):
    """Delete a prompt entry."""
    db = get_db_session()
    try:
        prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
        if not prompt:
            return jsonify({'error': 'Prompt not found'}), 404

        db.delete(prompt)
        db.commit()
        return jsonify({'success': True}), 200
    finally:
        db.close()
