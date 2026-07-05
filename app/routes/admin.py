"""Admin routes."""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Student, UploadedPDF, StudentNote, Quiz
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to check if user is admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """
    Admin dashboard.
    """
    # Get statistics
    total_students = Student.query.count()
    total_notes = StudentNote.query.count()
    total_quizzes = Quiz.query.count()
    total_pdfs = UploadedPDF.query.count()
    
    # Get recent students
    recent_students = Student.query.order_by(Student.created_at.desc()).limit(10).all()
    
    context = {
        'total_students': total_students,
        'total_notes': total_notes,
        'total_quizzes': total_quizzes,
        'total_pdfs': total_pdfs,
        'recent_students': recent_students
    }
    
    return render_template('admin/dashboard.html', **context)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """
    View all users.
    """
    page = request.args.get('page', 1, type=int)
    students = Student.query.paginate(page=page, per_page=20)
    
    return render_template('admin/users.html', students=students)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """
    Delete user.
    """
    try:
        if user_id == current_user.id:
            return jsonify({'error': 'Cannot delete yourself'}), 400
        
        student = Student.query.get(user_id)
        if not student:
            return jsonify({'error': 'User not found'}), 404
        
        db.session.delete(student)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'User deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/uploads')
@login_required
@admin_required
def uploads():
    """
    View all uploaded PDFs.
    """
    page = request.args.get('page', 1, type=int)
    pdfs = UploadedPDF.query.paginate(page=page, per_page=20)
    
    return render_template('admin/uploads.html', pdfs=pdfs)

@admin_bp.route('/statistics')
@login_required
@admin_required
def statistics():
    """
    View statistics.
    """
    # Calculate stats
    total_students = Student.query.count()
    total_notes = StudentNote.query.count()
    total_quizzes = Quiz.query.count()
    total_pdfs = UploadedPDF.query.count()
    
    # Average notes per student
    avg_notes = db.session.query(func.avg(func.count(StudentNote.id))).group_by(StudentNote.student_id).scalar() or 0
    
    # Average quizzes per student
    avg_quizzes = db.session.query(func.avg(func.count(Quiz.id))).group_by(Quiz.student_id).scalar() or 0
    
    context = {
        'total_students': total_students,
        'total_notes': total_notes,
        'total_quizzes': total_quizzes,
        'total_pdfs': total_pdfs,
        'avg_notes': round(avg_notes, 2),
        'avg_quizzes': round(avg_quizzes, 2)
    }
    
    return render_template('admin/statistics.html', **context)
