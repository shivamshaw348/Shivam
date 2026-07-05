"""
Admin panel routes for administrative functions.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Student, UploadedPDF, StudentNote, Quiz
from functools import wraps
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """
    Decorator to check if user is admin.
    In this implementation, first registered user is admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Simple admin check - can be enhanced with proper role system
        if not current_user.is_authenticated or current_user.id != 1:
            flash('Admin access required', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """
    Display admin dashboard with statistics.
    """
    total_students = Student.query.count()
    total_uploads = UploadedPDF.query.count()
    total_notes = StudentNote.query.count()
    total_quizzes = Quiz.query.count()
    active_students = Student.query.filter_by(is_active=True).count()
    
    stats = {
        'total_students': total_students,
        'total_uploads': total_uploads,
        'total_notes': total_notes,
        'total_quizzes': total_quizzes,
        'active_students': active_students
    }
    
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/users')
@login_required
@admin_required
def view_users():
    """
    View all registered students.
    """
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Student.query
    
    if search:
        query = query.filter(
            db.or_(
                Student.username.ilike(f'%{search}%'),
                Student.email.ilike(f'%{search}%'),
                Student.first_name.ilike(f'%{search}%')
            )
        )
    
    users = query.paginate(page=page, per_page=20)
    
    return render_template('admin/users.html', users=users, search_query=search)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """
    Delete a user and all associated data.
    """
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    user = Student.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'User deleted'})

@admin_bp.route('/uploads')
@login_required
@admin_required
def view_uploads():
    """
    View all uploaded PDFs.
    """
    page = request.args.get('page', 1, type=int)
    
    uploads = UploadedPDF.query.order_by(
        UploadedPDF.uploaded_at.desc()
    ).paginate(page=page, per_page=20)
    
    return render_template('admin/uploads.html', uploads=uploads)

@admin_bp.route('/statistics')
@login_required
@admin_required
def statistics():
    """
    Display detailed statistics.
    """
    # Subject-wise notes
    subject_stats = db.session.query(
        StudentNote.subject,
        func.count(StudentNote.id).label('count')
    ).group_by(StudentNote.subject).all()
    
    # Quiz statistics
    quiz_stats = db.session.query(
        Quiz.subject,
        func.count(Quiz.id).label('total'),
        func.avg(Quiz.score).label('avg_score')
    ).filter(Quiz.attempted == True).group_by(Quiz.subject).all()
    
    # Recent activity
    recent_notes = StudentNote.query.order_by(StudentNote.created_at.desc()).limit(10).all()
    recent_uploads = UploadedPDF.query.order_by(UploadedPDF.uploaded_at.desc()).limit(10).all()
    
    return render_template('admin/statistics.html',
                         subject_stats=subject_stats,
                         quiz_stats=quiz_stats,
                         recent_notes=recent_notes,
                         recent_uploads=recent_uploads)
