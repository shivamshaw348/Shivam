"""
Quiz generation and management routes.
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Quiz
from app.utils.quiz_generator import generate_quiz as ai_generate_quiz
from datetime import datetime
import json

quiz_bp = Blueprint('quiz', __name__, url_prefix='/quiz')

@quiz_bp.route('/')
@login_required
def index():
    """
    Display quiz management interface.
    """
    quizzes = Quiz.query.filter_by(student_id=current_user.id).order_by(
        Quiz.created_at.desc()
    ).all()
    
    subjects = [
        'English', 'Physics', 'Chemistry', 'Mathematics',
        'Biology', 'Geography', 'History', 'Economics', 'Artificial Intelligence'
    ]
    
    return render_template('quiz/index.html', quizzes=quizzes, subjects=subjects)

@quiz_bp.route('/generate', methods=['POST'])
@login_required
def generate():
    """
    Generate new quiz using AI.
    """
    data = request.get_json()
    subject = data.get('subject', '').strip()
    topic = data.get('topic', '').strip()
    quiz_type = data.get('quiz_type', 'mixed')  # mcq, true_false, fill_blank, short_answer, mixed
    
    if not subject:
        return jsonify({'error': 'Subject is required'}), 400
    
    try:
        # Generate quiz questions
        questions = ai_generate_quiz(subject, topic, quiz_type)
        
        # Create quiz record
        quiz = Quiz(
            student_id=current_user.id,
            subject=subject,
            title=f'{subject} Quiz - {topic or "General"}',
            total_questions=len(questions)
        )
        quiz.set_questions(questions)
        
        db.session.add(quiz)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'quiz_id': quiz.id,
            'message': 'Quiz generated successfully'
        })
    
    except Exception as e:
        return jsonify({'error': f'Error generating quiz: {str(e)}'}), 500

@quiz_bp.route('/<int:quiz_id>')
@login_required
def view_quiz(quiz_id):
    """
    Display quiz for attempting.
    """
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if quiz.student_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    questions = quiz.get_questions()
    
    return render_template('quiz/view_quiz.html', quiz=quiz, questions=questions)

@quiz_bp.route('/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    """
    Submit quiz answers and calculate score.
    """
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if quiz.student_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    answers = data.get('answers', {})
    
    questions = quiz.get_questions()
    score = 0
    total = len(questions)
    
    # Calculate score
    for question in questions:
        q_id = str(question.get('id'))
        if q_id in answers:
            if answers[q_id].lower().strip() == question.get('answer', '').lower().strip():
                score += 1
    
    percentage = (score / total * 100) if total > 0 else 0
    
    # Update quiz record
    quiz.score = percentage
    quiz.attempted = True
    quiz.completed_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'score': score,
        'total': total,
        'percentage': percentage
    })

@quiz_bp.route('/<int:quiz_id>/delete', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    """
    Delete a quiz.
    """
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if quiz.student_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(quiz)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Quiz deleted'})
