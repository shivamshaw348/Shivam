"""
Quiz generation utilities.
"""

import google.generativeai as genai
from flask import current_app
import json
import random

def generate_quiz(subject, topic, quiz_type='mixed', count=20):
    """
    Generate quiz questions using AI.
    
    Args:
        subject (str): Subject name
        topic (str): Topic/chapter name
        quiz_type (str): Type of quiz (mcq, true_false, fill_blank, short_answer, mixed)
        count (int): Number of questions to generate
        
    Returns:
        list: List of question dictionaries
    """
    try:
        api_key = current_app.config.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError('GEMINI_API_KEY not configured')
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        if quiz_type == 'mcq':
            return _generate_mcq(model, subject, topic, count)
        elif quiz_type == 'true_false':
            return _generate_true_false(model, subject, topic, count)
        elif quiz_type == 'fill_blank':
            return _generate_fill_blank(model, subject, topic, count)
        elif quiz_type == 'short_answer':
            return _generate_short_answer(model, subject, topic, count)
        else:  # mixed
            questions = []
            questions.extend(_generate_mcq(model, subject, topic, count//4))
            questions.extend(_generate_true_false(model, subject, topic, count//4))
            questions.extend(_generate_fill_blank(model, subject, topic, count//4))
            questions.extend(_generate_short_answer(model, subject, topic, count//4))
            return questions
    
    except Exception as e:
        raise Exception(f"Error generating quiz: {str(e)}")

def _generate_mcq(model, subject, topic, count):
    """
    Generate multiple choice questions.
    """
    prompt = f"""
    Generate {count} multiple choice questions about {subject} - {topic}.
    Each question should have 4 options (A, B, C, D).
    
    Format the response as JSON array with this structure:
    [
        {{
            "id": 1,
            "question": "Question text?",
            "type": "mcq",
            "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},
            "answer": "B"
        }}
    ]
    
    Return ONLY valid JSON, no other text.
    """
    
    response = model.generate_content(prompt)
    try:
        questions = json.loads(response.text)
        return questions
    except:
        return []

def _generate_true_false(model, subject, topic, count):
    """
    Generate true/false questions.
    """
    prompt = f"""
    Generate {count} true/false questions about {subject} - {topic}.
    
    Format the response as JSON array:
    [
        {{
            "id": 1,
            "question": "Statement?",
            "type": "true_false",
            "answer": "True"
        }}
    ]
    
    Return ONLY valid JSON, no other text.
    """
    
    response = model.generate_content(prompt)
    try:
        questions = json.loads(response.text)
        return questions
    except:
        return []

def _generate_fill_blank(model, subject, topic, count):
    """
    Generate fill in the blank questions.
    """
    prompt = f"""
    Generate {count} fill-in-the-blank questions about {subject} - {topic}.
    The blank should be represented by ______.
    
    Format the response as JSON array:
    [
        {{
            "id": 1,
            "question": "Sentence with ______ to be filled.",
            "type": "fill_blank",
            "answer": "word"
        }}
    ]
    
    Return ONLY valid JSON, no other text.
    """
    
    response = model.generate_content(prompt)
    try:
        questions = json.loads(response.text)
        return questions
    except:
        return []

def _generate_short_answer(model, subject, topic, count):
    """
    Generate short answer questions.
    """
    prompt = f"""
    Generate {count} short answer questions about {subject} - {topic}.
    Each should have a concise answer (1-2 sentences).
    
    Format the response as JSON array:
    [
        {{
            "id": 1,
            "question": "What is...?",
            "type": "short_answer",
            "answer": "Short answer text"
        }}
    ]
    
    Return ONLY valid JSON, no other text.
    """
    
    response = model.generate_content(prompt)
    try:
        questions = json.loads(response.text)
        return questions
    except:
        return []
