"""Quiz generation utilities."""

import json
from typing import List, Dict
from app.utils.gemini_api import ask_gemini, generate_quiz_prompt

def generate_quiz_questions(subject: str, topic: str, question_type: str, num_questions: int) -> List[Dict]:
    """
    Generate quiz questions using Gemini API.
    
    Args:
        subject (str): Subject name
        topic (str): Topic name
        question_type (str): Type of questions
        num_questions (int): Number of questions
        
    Returns:
        List[Dict]: List of question dictionaries
    """
    try:
        prompt = generate_quiz_prompt(subject, topic, question_type, num_questions)
        response = ask_gemini(prompt)
        
        if not response:
            return generate_sample_questions(num_questions)
        
        # Parse JSON response
        try:
            # Find JSON array in response
            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                questions = json.loads(json_str)
                return questions[:num_questions]
        
        except json.JSONDecodeError:
            pass
        
        return generate_sample_questions(num_questions)
    
    except Exception as e:
        print(f"Quiz Generation Error: {str(e)}")
        return generate_sample_questions(num_questions)

def generate_sample_questions(num_questions: int) -> List[Dict]:
    """
    Generate sample questions as fallback.
    
    Args:
        num_questions (int): Number of questions
        
    Returns:
        List[Dict]: List of sample questions
    """
    questions = []
    for i in range(num_questions):
        questions.append({
            'question': f'Sample Question {i+1}?',
            'option_a': 'Option A',
            'option_b': 'Option B',
            'option_c': 'Option C',
            'option_d': 'Option D',
            'correct_answer': 'Option A',
            'explanation': 'This is the correct answer.'
        })
    return questions
