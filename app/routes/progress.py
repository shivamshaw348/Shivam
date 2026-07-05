"""Progress Tracker routes."""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Progress
from sqlalchemy import func
from datetime import datetime, timedelta
import json

progress_bp = Blueprint('progress', __name__, url_prefix='/progress')

@progress_bp.route('/')
@login_required
def index():
    """
    Progress Tracker interface.
    """
    # Get all progress
    all_progress = Progress.query.filter_by(student_id=current_user.id).all()
    
    # Get statistics
    total_topics = len(all_progress)
    completed_topics = sum(1 for p in all_progress if p.completed)
    avg_progress = sum(p.completion_percentage for p in all_progress) / len(all_progress) if all_progress else 0
    
    subjects = ['Physics', 'Chemistry', 'Mathematics', 'Biology', 'English', 'History', 'Geography', 'Economics', 'Artificial Intelligence']
    
    return render_template('progress/index.html', 
                         progress_list=all_progress,
                         total_topics=total_topics,
                         completed_topics=completed_topics,
                         avg_progress=round(avg_progress, 2),
                         subjects=subjects)

@progress_bp.route('/add', methods=['POST'])
@login_required
def add_topic():
    """
    Add topic to track.
    """
    try:
        data = request.get_json()
        subject = data.get('subject', '').strip()
        topic = data.get('topic', '').strip()
        
        if not subject or not topic:
            return jsonify({'error': 'Subject and topic are required'}), 400
        
        # Check if already exists
        existing = Progress.query.filter_by(
            student_id=current_user.id,
            subject=subject,
            topic=topic
        ).first()
        
        if existing:
            return jsonify({'error': 'Topic already being tracked'}), 400
        
        # Create progress
        progress = Progress(
            student_id=current_user.id,
            subject=subject,
            topic=topic,
            completion_percentage=0.0
        )
        db.session.add(progress)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'progress_id': progress.id,
            'message': 'Topic added to tracker'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@progress_bp.route('/<int:progress_id>/update', methods=['POST'])
@login_required
def update_progress(progress_id):
    """
    Update progress percentage.
    """
    try:
        progress = Progress.query.filter_by(id=progress_id, student_id=current_user.id).first()
        if not progress:
            return jsonify({'error': 'Progress not found'}), 404
        
        data = request.get_json()
        percentage = float(data.get('percentage', 0))
        
        if percentage < 0 or percentage > 100:
            return jsonify({'error': 'Percentage must be between 0 and 100'}), 400
        
        progress.completion_percentage = percentage
        
        # Mark as completed if 100%
        if percentage >= 100:
            progress.completed = True
            progress.completed_at = datetime.utcnow()
        else:
            progress.completed = False
            progress.completed_at = None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Progress updated',
            'completed': progress.completed
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@progress_bp.route('/stats')
@login_required
def get_stats():
    """
    Get progress statistics.
    """
    try:
        all_progress = Progress.query.filter_by(student_id=current_user.id).all()
        
        # Calculate stats
        total = len(all_progress)
        completed = sum(1 for p in all_progress if p.completed)
        avg_percentage = sum(p.completion_percentage for p in all_progress) / len(all_progress) if all_progress else 0
        
        # Group by subject
        subject_stats = {}
        for p in all_progress:
            if p.subject not in subject_stats:
                subject_stats[p.subject] = {'total': 0, 'completed': 0, 'percentage': 0}
            subject_stats[p.subject]['total'] += 1
            if p.completed:
                subject_stats[p.subject]['completed'] += 1
            subject_stats[p.subject]['percentage'] += p.completion_percentage
        
        # Calculate averages by subject
        for subject in subject_stats:
            subject_stats[subject]['percentage'] /= subject_stats[subject]['total']
        
        return jsonify({
            'success': True,
            'stats': {
                'total_topics': total,
                'completed_topics': completed,
                'avg_percentage': round(avg_percentage, 2),
                'completion_rate': round((completed / total * 100) if total > 0 else 0, 2),
                'by_subject': subject_stats
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@progress_bp.route('/<int:progress_id>/delete', methods=['POST'])
@login_required
def delete_progress(progress_id):
    """
    Delete progress tracking.
    """
    try:
        progress = Progress.query.filter_by(id=progress_id, student_id=current_user.id).first()
        if not progress:
            return jsonify({'error': 'Progress not found'}), 404
        
        db.session.delete(progress)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Progress deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
