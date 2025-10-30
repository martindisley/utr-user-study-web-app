"""
Concept routes - manage participant concept captures per session.
"""
from flask import Blueprint, jsonify, request

from backend.database import get_db_session
from backend.models import Session, Concept, Message

concepts_bp = Blueprint('concepts', __name__)


def _session_not_found():
    return jsonify({'error': 'Session not found'}), 404


@concepts_bp.route('/api/session/<int:session_id>/concepts', methods=['GET'])
def list_concepts(session_id):
    """Return all concepts captured for a session."""
    db = get_db_session()
    try:
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            return _session_not_found()

        concepts = (
            db.query(Concept)
            .filter(Concept.session_id == session_id)
            .order_by(Concept.created_at)
            .all()
        )
        return jsonify({'concepts': [concept.to_dict() for concept in concepts]}), 200
    finally:
        db.close()


@concepts_bp.route('/api/session/<int:session_id>/concepts', methods=['POST'])
def create_concept(session_id):
    """Create a new concept entry for the given session."""
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

        concept = Concept(
            session_id=session_id,
            title=title,
            content=content,
            source_message_id=source_message.id if source_message else None,
        )
        db.add(concept)
        db.commit()
        db.refresh(concept)

        return jsonify(concept.to_dict()), 201
    finally:
        db.close()


@concepts_bp.route('/api/concepts/<int:concept_id>', methods=['PUT'])
def update_concept(concept_id):
    """Update an existing concept."""
    data = request.get_json() or {}

    db = get_db_session()
    try:
        concept = db.query(Concept).filter(Concept.id == concept_id).first()
        if not concept:
            return jsonify({'error': 'Concept not found'}), 404

        if 'content' in data:
            content = (data.get('content') or '').strip()
            if not content:
                return jsonify({'error': 'content cannot be empty'}), 400
            concept.content = content

        if 'title' in data:
            title = (data.get('title') or '').strip()
            if title and len(title) > 150:
                return jsonify({'error': 'title must be 150 characters or fewer'}), 400
            concept.title = title or None

        if 'source_message_id' in data:
            source_message_id = data.get('source_message_id')
            if source_message_id is None:
                concept.source_message_id = None
            else:
                source_message = (
                    db.query(Message)
                    .filter(
                        Message.id == source_message_id,
                        Message.session_id == concept.session_id,
                    )
                    .first()
                )
                if not source_message:
                    return jsonify({'error': 'source_message_id must reference a message in this session'}), 400
                concept.source_message_id = source_message.id

        db.add(concept)
        db.commit()
        db.refresh(concept)

        return jsonify(concept.to_dict()), 200
    finally:
        db.close()


@concepts_bp.route('/api/concepts/<int:concept_id>', methods=['DELETE'])
def delete_concept(concept_id):
    """Delete a concept entry."""
    db = get_db_session()
    try:
        concept = db.query(Concept).filter(Concept.id == concept_id).first()
        if not concept:
            return jsonify({'error': 'Concept not found'}), 404

        db.delete(concept)
        db.commit()
        return jsonify({'success': True}), 200
    finally:
        db.close()
