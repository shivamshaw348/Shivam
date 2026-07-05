"""Google Gemini API integration utilities."""

import os
import google.generativeai as genai
from typing import Optional

# Configure API
API_KEY = os.getenv('GEMINI_API_KEY')
if API_KEY:
    genai.configure(api_key=API_KEY)

def ask_gemini(prompt: str, model: str = 'gemini-pro') -> Optional[str]:
    """
    Send prompt to Gemini API and get response.
    
    Args:
        prompt (str): The prompt to send
        model (str): Model name (default: gemini-pro)
        
    Returns:
        str: Response from Gemini API or None if error
    """
    try:
        model_obj = genai.GenerativeModel(model)
        response = model_obj.generate_content(prompt)
        
        if response.parts:
            return response.text
        return None
    
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        return None

def generate_quiz_prompt(subject: str, topic: str, question_type: str, num_questions: int) -> str:
    """
    Generate prompt for quiz generation.
    
    Args:
        subject (str): Subject name
        topic (str): Topic name
        question_type (str): Type of questions (MCQ, True/False, etc.)
        num_questions (int): Number of questions
        
    Returns:
        str: Formatted prompt
    """
    prompt = f"""
    Generate {num_questions} {question_type} questions on {topic} in {subject}.
    
    Format each question as JSON:
    {{
        "question": "question text",
        "option_a": "option 1",
        "option_b": "option 2",
        "option_c": "option 3",
        "option_d": "option 4",
        "correct_answer": "option_a",
        "explanation": "explanation of answer"
    }}
    
    Return as valid JSON array.
    """
    return prompt

def generate_flashcard_prompt(subject: str, topic: str, num_cards: int) -> str:
    """
    Generate prompt for flashcard generation.
    
    Args:
        subject (str): Subject name
        topic (str): Topic name
        num_cards (int): Number of flashcards
        
    Returns:
        str: Formatted prompt
    """
    prompt = f"""
    Generate {num_cards} flashcards for {topic} in {subject}.
    
    Format each card as JSON:
    {{
        "question": "flashcard question",
        "answer": "flashcard answer",
        "difficulty": "easy/medium/hard"
    }}
    
    Return as valid JSON array.
    """
    return prompt

def generate_summary_prompt(text: str) -> str:
    """
    Generate prompt for text summarization.
    
    Args:
        text (str): Text to summarize
        
    Returns:
        str: Formatted prompt
    """
    prompt = f"""
    Please provide a concise summary of the following text. Also extract key points and important definitions.
    
    Text:
    {text[:2000]}  # Limit to first 2000 characters
    
    Provide summary in the following format:
    
    SUMMARY:
    [summary here]
    
    KEY POINTS:
    - Point 1
    - Point 2
    - Point 3
    
    IMPORTANT DEFINITIONS:
    - Term 1: Definition
    - Term 2: Definition
    """
    return prompt

def generate_study_plan_prompt(subjects: list, days_left: int, daily_hours: float) -> str:
    """
    Generate prompt for study plan generation.
    
    Args:
        subjects (list): List of subjects
        days_left (int): Days until exam
        daily_hours (float): Daily study hours
        
    Returns:
        str: Formatted prompt
    """
    subjects_str = ', '.join(subjects)
    
    prompt = f"""
    Create a personalized study plan for:
    - Subjects: {subjects_str}
    - Days until exam: {days_left}
    - Daily study hours: {daily_hours}
    
    Provide the plan in JSON format:
    {{
        "daily_schedule": {{
            "monday": ["subject", "hours"],
            ...
        }},
        "weekly_schedule": [...],
        "revision_schedule": [...]
    }}
    
    Return as valid JSON.
    """
    return prompt
