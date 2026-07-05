"""Study plan generation utilities."""

from datetime import datetime, timedelta
from typing import Tuple, List, Dict
from app.utils.gemini_api import ask_gemini, generate_study_plan_prompt

def generate_study_plan(subjects: List[str], exam_date: datetime.date, daily_hours: float) -> Tuple[Dict, Dict, Dict]:
    """
    Generate personalized study plan.
    
    Args:
        subjects (List[str]): List of subjects
        exam_date (datetime.date): Exam date
        daily_hours (float): Daily study hours available
        
    Returns:
        Tuple[Dict, Dict, Dict]: Daily schedule, weekly schedule, revision schedule
    """
    try:
        today = datetime.now().date()
        days_left = (exam_date - today).days
        
        if days_left < 1:
            days_left = 1
        
        prompt = generate_study_plan_prompt(subjects, days_left, daily_hours)
        response = ask_gemini(prompt)
        
        if response:
            try:
                # Parse JSON response
                import json
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx]
                    plan = json.loads(json_str)
                    
                    daily = plan.get('daily_schedule', {})
                    weekly = plan.get('weekly_schedule', {})
                    revision = plan.get('revision_schedule', {})
                    
                    return daily, weekly, revision
            
            except Exception as e:
                print(f"Plan Parse Error: {str(e)}")
        
        # Generate default plan
        return generate_default_plan(subjects, days_left, daily_hours)
    
    except Exception as e:
        print(f"Plan Generation Error: {str(e)}")
        return generate_default_plan(subjects, days_left, daily_hours)

def generate_default_plan(subjects: List[str], days_left: int, daily_hours: float) -> Tuple[Dict, Dict, Dict]:
    """
    Generate default study plan.
    
    Args:
        subjects (List[str]): List of subjects
        days_left (int): Days until exam
        daily_hours (float): Daily study hours
        
    Returns:
        Tuple[Dict, Dict, Dict]: Default schedules
    """
    daily_schedule = {}
    weekly_schedule = {}
    revision_schedule = {}
    
    # Distribute subjects across days
    hours_per_subject = daily_hours / len(subjects) if subjects else 1
    
    # Create daily schedule
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    subject_index = 0
    
    for i in range(days_left):
        day = days[i % 7]
        subject = subjects[subject_index % len(subjects)] if subjects else 'General'
        
        daily_schedule[day] = {
            'subject': subject,
            'hours': hours_per_subject,
            'topics': ['Topic 1', 'Topic 2', 'Topic 3']
        }
        
        subject_index += 1
    
    # Create weekly schedule
    for subject in subjects:
        weekly_schedule[subject] = {
            'hours_per_week': daily_hours * 5,
            'sessions': 5,
            'session_duration': daily_hours
        }
    
    # Create revision schedule (last week)
    revision_days = min(7, days_left // 4)
    for i in range(revision_days):
        day = days[i % 7]
        revision_schedule[day] = {
            'revision_subjects': subjects,
            'focus': 'Weak areas'
        }
    
    return daily_schedule, weekly_schedule, revision_schedule
