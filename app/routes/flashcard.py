"""Flashcard routes."""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Flashcard
from app.utils.flashcard_generator import generate_flashcards
from datetime import datetime

flashcard_bp = Blueprint('flashcard', __name__, url_prefix='/flashcard')

@flashcard_bp.route('/')
@login_required
def index():
    """
    Flashcard interface.
    """
    # Get user's flashcards
    flashcards = Flashcard.query.filter_by(student_id=current_user.id).order_by(
        Flashcard.created_at.desc()
    ).all()
    
    subjects = ['Physics', 'Chemistry', 'Mathematics', 'Biology', 'English', 'History', 'Geography', 'Economics', 'Artificial Intelligence']
    
    return render_template('flashcard/index.html', flashcards=flashcards, subjects=subjects)

@flashcard_bp.route('/generate', methods=['POST'])
@login_required
def generate():
    """
    Generate flashcards from topic.
    """
    try:
        data = request.get_json()
        subject = data.get('subject', '').strip()
        topic = data.get('topic', '').strip()
        num_cards = int(data.get('num_cards', 10))
        
        if not subject or not topic:
            return jsonify({'error': 'Subject and topic are required'}), 400
        
        if num_cards < 1 or num_cards > 100:
            return jsonify({'error': 'Number of cards must be between 1 and 100'}), 400
        
        # Generate flashcards
        cards = generate_flashcards(subject, topic, num_cards)
        
        # Save to database
        flashcard_ids = []
        for card in cards:
            flashcard = Flashcard(
                student_id=current_user.id,
                subject=subject,
                question=card['question'],
                answer=card['answer'],
                difficulty=card.get('difficulty', 'medium')
            )
            db.session.add(flashcard)
            db.session.flush()
            flashcard_ids.append(flashcard.id)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'flashcard_ids': flashcard_ids,
            'message': f'{len(cards)} flashcards generated successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error: {str(e)}'}), 500

@flashcard_bp.route('/list')
@login_required
def list_flashcards():
    """
    Get list of flashcards for a subject.
    """
    subject = request.args.get('subject')
    
    query = Flashcard.query.filter_by(student_id=current_user.id)
    if subject:
        query = query.filter_by(subject=subject)
    
    flashcards = query.order_by(Flashcard.created_at.desc()).all()
    
    return jsonify([
        {
            'id': fc.id,
            'question': fc.question,
            'answer': fc.answer,
            'difficulty': fc.difficulty,
            'correct_count': fc.correct_count,
            'incorrect_count': fc.incorrect_count
        }
        for fc in flashcards
    ])

@flashcard_bp.route('/<int:flashcard_id>/feedback', methods=['POST'])
@login_required
def record_feedback(flashcard_id):
    """
    Record flashcard feedback (correct/incorrect).
    """
    try:
        flashcard = Flashcard.query.filter_by(id=flashcard_id, student_id=current_user.id).first()
        if not flashcard:
            return jsonify({'error': 'Flashcard not found'}), 404
        
        data = request.get_json()
        correct = data.get('correct', False)
        
        if correct:
            flashcard.correct_count += 1
        else:
            flashcard.incorrect_count += 1
        
        flashcard.last_reviewed = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Feedback recorded'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@flashcard_bp.route('/<int:flashcard_id>/delete', methods=['POST'])
@login_required
def delete_flashcard(flashcard_id):
    """
    Delete flashcard.
    """
    try:
        flashcard = Flashcard.query.filter_by(id=flashcard_id, student_id=current_user.id).first()
        if not flashcard:
            return jsonify({'error': 'Flashcard not found'}), 404
        
        db.session.delete(flashcard)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Flashcard deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
