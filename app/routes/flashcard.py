"""
Flashcard generation and management routes.
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Flashcard
from app.utils.flashcard_generator import generate_flashcards as ai_generate_flashcards
from datetime import datetime

flashcard_bp = Blueprint('flashcard', __name__, url_prefix='/flashcard')

@flashcard_bp.route('/')
@login_required
def index():
    """
    Display flashcard management interface.
    """
    flashcards = Flashcard.query.filter_by(student_id=current_user.id).order_by(
        Flashcard.created_at.desc()
    ).all()
    
    subjects = [
        'English', 'Physics', 'Chemistry', 'Mathematics',
        'Biology', 'Geography', 'History', 'Economics', 'Artificial Intelligence'
    ]
    
    return render_template('flashcard/index.html', flashcards=flashcards, subjects=subjects)

@flashcard_bp.route('/generate', methods=['POST'])
@login_required
def generate():
    """
    Generate flashcards from text or topic.
    """
    data = request.get_json()
    subject = data.get('subject', '').strip()
    topic = data.get('topic', '').strip()
    text = data.get('text', '').strip()
    count = data.get('count', 10)
    
    if not subject or (not topic and not text):
        return jsonify({'error': 'Subject and either topic or text is required'}), 400
    
    try:
        # Generate flashcards using AI
        flashcards_data = ai_generate_flashcards(subject, topic, text, count)
        
        # Save flashcards
        for card in flashcards_data:
            flashcard = Flashcard(
                student_id=current_user.id,
                subject=subject,
                question=card.get('question'),
                answer=card.get('answer'),
                difficulty=card.get('difficulty', 'medium')
            )
            db.session.add(flashcard)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'count': len(flashcards_data),
            'message': f'{len(flashcards_data)} flashcards generated successfully'
        })
    
    except Exception as e:
        return jsonify({'error': f'Error generating flashcards: {str(e)}'}), 500

@flashcard_bp.route('/<int:card_id>')
@login_required
def view_card(card_id):
    """
    View a single flashcard.
    """
    card = Flashcard.query.get_or_404(card_id)
    
    if card.student_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': card.id,
        'question': card.question,
        'answer': card.answer,
        'difficulty': card.difficulty,
        'correct_count': card.correct_count,
        'incorrect_count': card.incorrect_count
    })

@flashcard_bp.route('/<int:card_id>/feedback', methods=['POST'])
@login_required
def send_feedback(card_id):
    """
    Record answer feedback for flashcard.
    """
    card = Flashcard.query.get_or_404(card_id)
    
    if card.student_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    is_correct = data.get('is_correct', False)
    
    if is_correct:
        card.correct_count += 1
    else:
        card.incorrect_count += 1
    
    db.session.commit()
    
    return jsonify({'success': True})

@flashcard_bp.route('/<int:card_id>/delete', methods=['POST'])
@login_required
def delete_card(card_id):
    """
    Delete a flashcard.
    """
    card = Flashcard.query.get_or_404(card_id)
    
    if card.student_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(card)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Flashcard deleted'})

@flashcard_bp.route('/subject/<subject>')
@login_required
def get_subject_cards(subject):
    """
    Get all flashcards for a specific subject.
    """
    cards = Flashcard.query.filter_by(
        student_id=current_user.id,
        subject=subject
    ).all()
    
    data = {
        'subject': subject,
        'cards': [
            {
                'id': card.id,
                'question': card.question,
                'answer': card.answer,
                'difficulty': card.difficulty
            }
            for card in cards
        ],
        'total': len(cards)
    }
    
    return jsonify(data)
