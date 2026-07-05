"""Flashcard generation utilities."""

import json
from typing import List, Dict
from app.utils.gemini_api import ask_gemini, generate_flashcard_prompt

def generate_flashcards(subject: str, topic: str, num_cards: int) -> List[Dict]:
    """
    Generate flashcards using Gemini API.
    
    Args:
        subject (str): Subject name
        topic (str): Topic name
        num_cards (int): Number of flashcards
        
    Returns:
        List[Dict]: List of flashcard dictionaries
    """
    try:
        prompt = generate_flashcard_prompt(subject, topic, num_cards)
        response = ask_gemini(prompt)
        
        if not response:
            return generate_sample_flashcards(num_cards)
        
        # Parse JSON response
        try:
            # Find JSON array in response
            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                cards = json.loads(json_str)
                return cards[:num_cards]
        
        except json.JSONDecodeError:
            pass
        
        return generate_sample_flashcards(num_cards)
    
    except Exception as e:
        print(f"Flashcard Generation Error: {str(e)}")
        return generate_sample_flashcards(num_cards)

def generate_sample_flashcards(num_cards: int) -> List[Dict]:
    """
    Generate sample flashcards as fallback.
    
    Args:
        num_cards (int): Number of flashcards
        
    Returns:
        List[Dict]: List of sample flashcards
    """
    cards = []
    for i in range(num_cards):
        cards.append({
            'question': f'Question {i+1}?',
            'answer': f'Answer {i+1}',
            'difficulty': 'medium'
        })
    return cards
