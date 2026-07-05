"""
Study planner generation utilities.
"""

import google.generativeai as genai
from flask import current_app
from datetime import datetime, timedelta
import json

def generate_study_plan(subjects, exam_date, daily_hours):
    """
    Generate a comprehensive study plan.
    
    Args:
        subjects (list): List of subjects to study
        exam_date (datetime): Exam date
        daily_hours (int): Hours available daily for study
        
    Returns:
        dict: Study plan with daily, weekly, and revision schedules
    """
    try:
        api_key = current_app.config.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError('GEMINI_API_KEY not configured')
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Calculate days until exam
        today = datetime.utcnow()
        days_remaining = (exam_date - today).days
        
        subjects_str = ', '.join(subjects)
        
        prompt = f"""
        Create a comprehensive study plan for a Class 11 student with:
        - Subjects: {subjects_str}
        - Days until exam: {days_remaining} days
        - Study hours per day: {daily_hours} hours
        
        Generate a study schedule that includes:
        1. Daily schedule (how many hours per subject each day)
        2. Weekly plan (topics to cover each week)
        3. Revision schedule (when to revise which subjects)
        
        Format as JSON:
        {{
            "daily_schedule": {{
                "day_1": {{"Math": 2, "Physics": 1.5, "Chemistry": 0.5}},
                "day_2": {{...}}
            }},
            "weekly_schedule": {{
                "week_1": {{"Math": ["Chapter 1", "Chapter 2"], "Physics": [...]}},
                "week_2": {{...}}
            }},
            "revision_schedule": {{
                "revision_1": {{"date": "2024-01-15", "subjects": ["Math", "Physics"]}},
                "revision_2": {{...}}
            }},
            "tips": ["Tip 1", "Tip 2", "Tip 3"]
        }}
        
        Return ONLY valid JSON, no other text.
        """
        
        response = model.generate_content(prompt)
        try:
            plan = json.loads(response.text)
            return plan
        except:
            # Return basic plan if parsing fails
            return {
                'daily_schedule': _generate_basic_daily_schedule(subjects, daily_hours),
                'weekly_schedule': _generate_basic_weekly_schedule(subjects, days_remaining),
                'revision_schedule': _generate_revision_schedule(subjects, exam_date),
                'tips': [
                    'Study in focused sessions of 45-50 minutes',
                    'Take regular breaks of 10-15 minutes',
                    'Practice previous year question papers',
                    'Maintain a formula sheet for quick revision'
                ]
            }
    
    except Exception as e:
        raise Exception(f"Error generating study plan: {str(e)}")

def _generate_basic_daily_schedule(subjects, daily_hours):
    """
    Generate a basic daily schedule.
    """
    hours_per_subject = daily_hours / len(subjects)
    schedule = {}
    for i in range(1, 8):  # 7 days
        day_schedule = {}
        for subject in subjects:
            day_schedule[subject] = round(hours_per_subject, 1)
        schedule[f'day_{i}'] = day_schedule
    return schedule

def _generate_basic_weekly_schedule(subjects, days_remaining):
    """
    Generate a basic weekly schedule.
    """
    weeks = max(1, days_remaining // 7)
    schedule = {}
    for week in range(1, weeks + 1):
        week_schedule = {}
        for subject in subjects:
            # Assign 2-3 chapters per week
            chapters = [f"Chapter {i}" for i in range(1, 4)]
            week_schedule[subject] = chapters
        schedule[f'week_{week}'] = week_schedule
    return schedule

def _generate_revision_schedule(subjects, exam_date):
    """
    Generate revision dates.
    """
    schedule = {}
    days_before = [14, 7, 3, 1]
    for idx, days in enumerate(days_before, 1):
        revision_date = exam_date - timedelta(days=days)
        schedule[f'revision_{idx}'] = {
            'date': revision_date.strftime('%Y-%m-%d'),
            'subjects': subjects
        }
    return schedule
