"""
Flashcard generation utilities.
"""

import google.generativeai as genai
from flask import current_app
import json

def generate_flashcards(subject, topic='', text='', count=10):
    """
    Generate flashcards from topic or text.
    
    Args:
        subject (str): Subject name
        topic (str): Topic name (optional)
        text (str): Text to generate from (optional)
        count (int): Number of flashcards to generate
        
    Returns:
        list: List of flashcard dictionaries
    """
    try:
        api_key = current_app.config.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError('GEMINI_API_KEY not configured')
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        if text:
            context = f"From the following text: {text[:1000]}"
        else:
            context = f"About {subject} - {topic}"
        
        prompt = f"""
        Generate {count} flashcards {context}.
        Each flashcard should have a question and answer suitable for Class 11 students.
        
        Format as JSON array:
        [
            {{
                "question": "Question or term?",
                "answer": "Answer or definition",
                "difficulty": "easy"
            }}
        ]
        
        Vary difficulty between 'easy', 'medium', 'hard'.
        Return ONLY valid JSON, no other text.
        """
        
        response = model.generate_content(prompt)
        try:
            flashcards = json.loads(response.text)
            return flashcards
        except:
            # Return default flashcards if parsing fails
            return [
                {
                    "question": f"What is a key concept in {subject}?",
                    "answer": "A fundamental concept",
                    "difficulty": "medium"
                }
            ]
    
    except Exception as e:
        raise Exception(f"Error generating flashcards: {str(e)}")
