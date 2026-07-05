"""
Study planner routes for schedule generation.
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import StudyPlanner
from app.utils.planner_generator import generate_study_plan
from datetime import datetime
import json

planner_bp = Blueprint('planner', __name__, url_prefix='/planner')

@planner_bp.route('/')
@login_required
def index():
    """
    Display study planner interface.
    """
    planner = StudyPlanner.query.filter_by(student_id=current_user.id).first()
    
    subjects = [
        'English', 'Physics', 'Chemistry', 'Mathematics',
        'Biology', 'Geography', 'History', 'Economics', 'Artificial Intelligence'
    ]
    
    return render_template('planner/index.html', planner=planner, subjects=subjects)

@planner_bp.route('/create', methods=['POST'])
@login_required
def create_plan():
    """
    Create a new study plan.
    """
    data = request.get_json()
    subjects = data.get('subjects', [])
    exam_date = data.get('exam_date', '')
    daily_hours = data.get('daily_hours', 0)
    
    # Validation
    if not subjects or not exam_date or not daily_hours:
        return jsonify({'error': 'All fields are required'}), 400
    
    if len(subjects) == 0:
        return jsonify({'error': 'Please select at least one subject'}), 400
    
    if daily_hours < 1 or daily_hours > 12:
        return jsonify({'error': 'Daily hours must be between 1 and 12'}), 400
    
    try:
        exam_datetime = datetime.fromisoformat(exam_date)
        
        # Delete existing plan if any
        StudyPlanner.query.filter_by(student_id=current_user.id).delete()
        
        # Generate study plan
        plan_data = generate_study_plan(subjects, exam_datetime, daily_hours)
        
        # Create planner record
        planner = StudyPlanner(
            student_id=current_user.id,
            exam_date=exam_datetime,
            daily_hours=daily_hours
        )
        planner.set_subjects(subjects)
        planner.daily_schedule = json.dumps(plan_data.get('daily_schedule', {}))
        planner.weekly_schedule = json.dumps(plan_data.get('weekly_schedule', {}))
        planner.revision_schedule = json.dumps(plan_data.get('revision_schedule', {}))
        
        db.session.add(planner)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'planner_id': planner.id,
            'message': 'Study plan created successfully'
        })
    
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    except Exception as e:
        return jsonify({'error': f'Error creating plan: {str(e)}'}), 500

@planner_bp.route('/view')
@login_required
def view_plan():
    """
    View current study plan.
    """
    planner = StudyPlanner.query.filter_by(student_id=current_user.id).first()
    
    if not planner:
        return render_template('planner/no_plan.html')
    
    daily_schedule = json.loads(planner.daily_schedule) if planner.daily_schedule else {}
    weekly_schedule = json.loads(planner.weekly_schedule) if planner.weekly_schedule else {}
    revision_schedule = json.loads(planner.revision_schedule) if planner.revision_schedule else {}
    
    return render_template('planner/view_plan.html',
                         planner=planner,
                         daily_schedule=daily_schedule,
                         weekly_schedule=weekly_schedule,
                         revision_schedule=revision_schedule)

@planner_bp.route('/update', methods=['POST'])
@login_required
def update_plan():
    """
    Update existing study plan.
    """
    data = request.get_json()
    subjects = data.get('subjects', [])
    exam_date = data.get('exam_date', '')
    daily_hours = data.get('daily_hours', 0)
    
    planner = StudyPlanner.query.filter_by(student_id=current_user.id).first()
    
    if not planner:
        return jsonify({'error': 'No plan found'}), 404
    
    try:
        exam_datetime = datetime.fromisoformat(exam_date)
        
        # Update planner
        planner.exam_date = exam_datetime
        planner.daily_hours = daily_hours
        planner.set_subjects(subjects)
        
        # Regenerate plan
        plan_data = generate_study_plan(subjects, exam_datetime, daily_hours)
        planner.daily_schedule = json.dumps(plan_data.get('daily_schedule', {}))
        planner.weekly_schedule = json.dumps(plan_data.get('weekly_schedule', {}))
        planner.revision_schedule = json.dumps(plan_data.get('revision_schedule', {}))
        planner.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Study plan updated'})
    
    except Exception as e:
        return jsonify({'error': f'Error updating plan: {str(e)}'}), 500
