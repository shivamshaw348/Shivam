"""Dashboard routes."""

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import StudentNote, ChatHistory, Quiz, Flashcard, Progress, UploadedPDF
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    """
    Main dashboard view with statistics and quick links.
    """
    # Get statistics
    total_notes = StudentNote.query.filter_by(student_id=current_user.id).count()
    total_chats = ChatHistory.query.filter_by(student_id=current_user.id).count()
    total_quizzes = Quiz.query.filter_by(student_id=current_user.id).count()
    total_flashcards = Flashcard.query.filter_by(student_id=current_user.id).count()
    total_pdfs = UploadedPDF.query.filter_by(student_id=current_user.id).count()
    
    # Get progress summary
    total_topics = Progress.query.filter_by(student_id=current_user.id).count()
    completed_topics = Progress.query.filter_by(student_id=current_user.id, completed=True).count()
    
    # Get average progress
    avg_progress = db.session.query(func.avg(Progress.completion_percentage)).filter_by(
        student_id=current_user.id
    ).scalar() or 0
    
    # Get recent notes
    recent_notes = StudentNote.query.filter_by(student_id=current_user.id).order_by(
        StudentNote.created_at.desc()
    ).limit(5).all()
    
    # Get recent quizzes
    recent_quizzes = Quiz.query.filter_by(student_id=current_user.id).order_by(
        Quiz.created_at.desc()
    ).limit(5).all()
    
    context = {
        'total_notes': total_notes,
        'total_chats': total_chats,
        'total_quizzes': total_quizzes,
        'total_flashcards': total_flashcards,
        'total_pdfs': total_pdfs,
        'total_topics': total_topics,
        'completed_topics': completed_topics,
        'avg_progress': round(avg_progress, 2),
        'recent_notes': recent_notes,
        'recent_quizzes': recent_quizzes
    }
    
    return render_template('dashboard/index.html', **context)
