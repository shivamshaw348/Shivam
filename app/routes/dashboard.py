"""
Dashboard routes for the main student interface.
"""

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models import StudentNote, ChatHistory, Quiz, Progress, UploadedPDF
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    """
    Display the main student dashboard.
    
    Shows:
        - Quick stats
        - Recent activity
        - Navigation cards
    """
    # Get statistics
    total_notes = StudentNote.query.filter_by(student_id=current_user.id).count()
    total_chats = ChatHistory.query.filter_by(student_id=current_user.id).count()
    total_quizzes = Quiz.query.filter_by(student_id=current_user.id).count()
    total_progress = Progress.query.filter_by(student_id=current_user.id).count()
    completed_topics = Progress.query.filter_by(student_id=current_user.id, completed=True).count()
    total_pdfs = UploadedPDF.query.filter_by(student_id=current_user.id).count()
    
    # Recent notes
    recent_notes = StudentNote.query.filter_by(student_id=current_user.id).order_by(
        StudentNote.created_at.desc()
    ).limit(5).all()
    
    # Recent chats
    recent_chats = ChatHistory.query.filter_by(student_id=current_user.id).order_by(
        ChatHistory.timestamp.desc()
    ).limit(5).all()
    
    stats = {
        'total_notes': total_notes,
        'total_chats': total_chats,
        'total_quizzes': total_quizzes,
        'total_progress': total_progress,
        'completed_topics': completed_topics,
        'total_pdfs': total_pdfs
    }
    
    return render_template('dashboard/index.html',
                         stats=stats,
                         recent_notes=recent_notes,
                         recent_chats=recent_chats)

@dashboard_bp.route('/stats')
@login_required
def get_stats():
    """
    Get JSON statistics for dashboard charts.
    """
    # Subject-wise progress
    subject_progress = db.session.query(
        Progress.subject,
        func.count(Progress.id).label('total'),
        func.sum(case((Progress.completed == True, 1), else_=0)).label('completed')
    ).filter_by(student_id=current_user.id).group_by(Progress.subject).all()
    
    data = {
        'subjects': [s[0] for s in subject_progress],
        'total_topics': [s[1] for s in subject_progress],
        'completed_topics': [s[2] or 0 for s in subject_progress]
    }
    
    return jsonify(data)
