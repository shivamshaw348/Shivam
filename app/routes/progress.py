"""
Progress tracking routes.
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Progress
from datetime import datetime, timedelta
from sqlalchemy import func

progress_bp = Blueprint('progress', __name__, url_prefix='/progress')

@progress_bp.route('/')
@login_required
def index():
    """
    Display progress tracking dashboard.
    """
    subjects = [
        'English', 'Physics', 'Chemistry', 'Mathematics',
        'Biology', 'Geography', 'History', 'Economics', 'Artificial Intelligence'
    ]
    
    progress_data = Progress.query.filter_by(student_id=current_user.id).all()
    
    return render_template('progress/index.html', progress_data=progress_data, subjects=subjects)

@progress_bp.route('/add', methods=['POST'])
@login_required
def add_topic():
    """
    Add a new topic to track.
    """
    data = request.get_json()
    subject = data.get('subject', '').strip()
    topic = data.get('topic', '').strip()
    
    if not subject or not topic:
        return jsonify({'error': 'Subject and topic are required'}), 400
    
    try:
        # Check if already exists
        existing = Progress.query.filter_by(
            student_id=current_user.id,
            subject=subject,
            topic=topic
        ).first()
        
        if existing:
            return jsonify({'error': 'Topic already exists'}), 400
        
        # Create new progress entry
        progress = Progress(
            student_id=current_user.id,
            subject=subject,
            topic=topic,
            completion_percentage=0
        )
        
        db.session.add(progress)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'progress_id': progress.id,
            'message': 'Topic added successfully'
        })
    
    except Exception as e:
        return jsonify({'error': f'Error adding topic: {str(e)}'}), 500

@progress_bp.route('/<int:progress_id>/update', methods=['POST'])
@login_required
def update_progress(progress_id):
    """
    Update progress for a topic.
    """
    progress = Progress.query.get_or_404(progress_id)
    
    if progress.student_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    completion_percentage = data.get('completion_percentage', 0)
    
    if completion_percentage < 0 or completion_percentage > 100:
        return jsonify({'error': 'Completion percentage must be between 0 and 100'}), 400
    
    progress.completion_percentage = completion_percentage
    
    if completion_percentage == 100 and not progress.completed:
        progress.completed = True
        progress.completed_date = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Progress updated'})

@progress_bp.route('/stats')
@login_required
def get_stats():
    """
    Get progress statistics.
    """
    # Overall stats
    total_topics = Progress.query.filter_by(student_id=current_user.id).count()
    completed_topics = Progress.query.filter_by(
        student_id=current_user.id,
        completed=True
    ).count()
    
    # Subject-wise stats
    subject_stats = db.session.query(
        Progress.subject,
        func.count(Progress.id).label('total'),
        func.sum(case((Progress.completed == True, 1), else_=0)).label('completed'),
        func.avg(Progress.completion_percentage).label('avg_completion')
    ).filter_by(student_id=current_user.id).group_by(Progress.subject).all()
    
    # Weekly stats
    week_ago = datetime.utcnow() - timedelta(days=7)
    completed_this_week = Progress.query.filter_by(student_id=current_user.id).filter(
        Progress.completed_date >= week_ago
    ).count()
    
    stats = {
        'total_topics': total_topics,
        'completed_topics': completed_topics,
        'completion_rate': (completed_topics / total_topics * 100) if total_topics > 0 else 0,
        'completed_this_week': completed_this_week,
        'subject_stats': [
            {
                'subject': s[0],
                'total': s[1],
                'completed': s[2] or 0,
                'avg_completion': round(s[3] or 0, 2)
            }
            for s in subject_stats
        ]
    }
    
    return jsonify(stats)

@progress_bp.route('/weekly-report')
@login_required
def weekly_report():
    """
    Generate weekly progress report.
    """
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    completed_topics = Progress.query.filter_by(student_id=current_user.id).filter(
        Progress.completed_date >= week_ago
    ).all()
    
    report = {
        'week': datetime.utcnow().strftime('%W'),
        'completed_topics': len(completed_topics),
        'topics': [
            {'topic': t.topic, 'subject': t.subject, 'completed_date': t.completed_date.isoformat()}
            for t in completed_topics
        ]
    }
    
    return jsonify(report)

from sqlalchemy import case
