"""Study Planner routes."""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import StudyPlanner
from app.utils.planner_generator import generate_study_plan
from datetime import datetime, timedelta
import json

planner_bp = Blueprint('planner', __name__, url_prefix='/planner')

@planner_bp.route('/')
@login_required
def index():
    """
    Study Planner interface.
    """
    # Get user's study plan
    planner = StudyPlanner.query.filter_by(student_id=current_user.id).first()
    
    subjects = ['Physics', 'Chemistry', 'Mathematics', 'Biology', 'English', 'History', 'Geography', 'Economics', 'Artificial Intelligence']
    
    return render_template('planner/index.html', planner=planner, subjects=subjects)

@planner_bp.route('/create', methods=['POST'])
@login_required
def create_plan():
    """
    Create study plan.
    """
    try:
        data = request.get_json()
        subjects = data.get('subjects', [])
        exam_date = data.get('exam_date', '')
        daily_hours = float(data.get('daily_hours', 0))
        
        if not subjects or not exam_date or daily_hours <= 0:
            return jsonify({'error': 'All fields are required'}), 400
        
        # Parse exam date
        exam_date_obj = datetime.strptime(exam_date, '%Y-%m-%d').date()
        
        # Generate study plan
        daily_schedule, weekly_schedule, revision_schedule = generate_study_plan(
            subjects, exam_date_obj, daily_hours
        )
        
        # Delete existing plan if any
        StudyPlanner.query.filter_by(student_id=current_user.id).delete()
        
        # Create new plan
        planner = StudyPlanner(
            student_id=current_user.id,
            exam_date=exam_date_obj,
            daily_hours=daily_hours
        )
        planner.set_subjects(subjects)
        planner.daily_schedule = json.dumps(daily_schedule)
        planner.weekly_schedule = json.dumps(weekly_schedule)
        planner.revision_schedule = json.dumps(revision_schedule)
        
        db.session.add(planner)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'plan_id': planner.id,
            'message': 'Study plan created successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error: {str(e)}'}), 500

@planner_bp.route('/view')
@login_required
def view_plan():
    """
    View study plan.
    """
    planner = StudyPlanner.query.filter_by(student_id=current_user.id).first()
    
    if not planner:
        return jsonify({'error': 'No study plan found'}), 404
    
    daily_schedule = json.loads(planner.daily_schedule) if planner.daily_schedule else {}
    weekly_schedule = json.loads(planner.weekly_schedule) if planner.weekly_schedule else {}
    revision_schedule = json.loads(planner.revision_schedule) if planner.revision_schedule else {}
    
    return jsonify({
        'success': True,
        'plan': {
            'id': planner.id,
            'subjects': planner.get_subjects(),
            'exam_date': planner.exam_date.strftime('%Y-%m-%d'),
            'daily_hours': planner.daily_hours,
            'daily_schedule': daily_schedule,
            'weekly_schedule': weekly_schedule,
            'revision_schedule': revision_schedule
        }
    })

@planner_bp.route('/update', methods=['POST'])
@login_required
def update_plan():
    """
    Update study plan.
    """
    try:
        planner = StudyPlanner.query.filter_by(student_id=current_user.id).first()
        
        if not planner:
            return jsonify({'error': 'No study plan found'}), 404
        
        data = request.get_json()
        
        # Update if new data provided
        if data.get('subjects'):
            planner.set_subjects(data.get('subjects'))
        
        if data.get('daily_hours'):
            planner.daily_hours = float(data.get('daily_hours'))
        
        planner.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Study plan updated'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
