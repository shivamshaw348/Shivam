"""Quiz Generator routes."""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Quiz
from app.utils.quiz_generator import generate_quiz_questions
import json

quiz_bp = Blueprint('quiz', __name__, url_prefix='/quiz')

@quiz_bp.route('/')
@login_required
def index():
    """
    Quiz Generator interface.
    """
    # Get user's quizzes
    quizzes = Quiz.query.filter_by(student_id=current_user.id).order_by(
        Quiz.created_at.desc()
    ).all()
    
    subjects = ['Physics', 'Chemistry', 'Mathematics', 'Biology', 'English', 'History', 'Geography', 'Economics', 'Artificial Intelligence']
    question_types = ['MCQ', 'True/False', 'Fill in the blanks', 'Short answer']
    
    return render_template('quiz/index.html', quizzes=quizzes, subjects=subjects, question_types=question_types)

@quiz_bp.route('/generate', methods=['POST'])
@login_required
def generate():
    """
    Generate quiz questions.
    """
    try:
        data = request.get_json()
        subject = data.get('subject', '').strip()
        topic = data.get('topic', '').strip()
        question_type = data.get('question_type', 'MCQ').strip()
        num_questions = int(data.get('num_questions', 10))
        
        if not subject or not topic:
            return jsonify({'error': 'Subject and topic are required'}), 400
        
        if num_questions < 1 or num_questions > 50:
            return jsonify({'error': 'Number of questions must be between 1 and 50'}), 400
        
        # Generate questions
        questions = generate_quiz_questions(subject, topic, question_type, num_questions)
        
        # Save to database
        quiz = Quiz(
            student_id=current_user.id,
            subject=subject,
            title=f"{topic} - {question_type} Quiz",
            total_questions=num_questions
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
        return jsonify({'error': f'Error: {str(e)}'}), 500

@quiz_bp.route('/<int:quiz_id>')
@login_required
def view_quiz(quiz_id):
    """
    View quiz questions.
    """
    quiz = Quiz.query.filter_by(id=quiz_id, student_id=current_user.id).first()
    
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
    
    questions = quiz.get_questions()
    
    return render_template('quiz/view_quiz.html', quiz=quiz, questions=questions)

@quiz_bp.route('/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    """
    Submit quiz answers and calculate score.
    """
    try:
        quiz = Quiz.query.filter_by(id=quiz_id, student_id=current_user.id).first()
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        data = request.get_json()
        user_answers = data.get('answers', {})
        
        # Save answers
        quiz.user_answers = json.dumps(user_answers)
        
        # Calculate score
        questions = quiz.get_questions()
        correct = 0
        
        for i, question in enumerate(questions):
            user_answer = user_answers.get(str(i), '').lower().strip()
            correct_answer = question.get('correct_answer', '').lower().strip()
            
            if user_answer == correct_answer:
                correct += 1
        
        score = (correct / len(questions) * 100) if questions else 0
        
        # Update quiz
        quiz.score = round(score, 2)
        quiz.attempted = True
        
        from datetime import datetime
        quiz.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'score': quiz.score,
            'correct_answers': correct,
            'total_questions': len(questions),
            'percentage': quiz.score
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@quiz_bp.route('/<int:quiz_id>/delete', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    """
    Delete quiz.
    """
    try:
        quiz = Quiz.query.filter_by(id=quiz_id, student_id=current_user.id).first()
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        db.session.delete(quiz)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Quiz deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
