"""
Form and input validators.
"""

import re

def validate_email(email):
    """
    Validate email address.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """
    Validate password strength.
    
    Args:
        password (str): Password to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if len(password) < 6:
        return False, 'Password must be at least 6 characters long'
    
    if not any(char.isdigit() for char in password):
        return False, 'Password must contain at least one digit'
    
    if not any(char.isupper() for char in password):
        return False, 'Password must contain at least one uppercase letter'
    
    return True, ''

def validate_username(username):
    """
    Validate username format.
    
    Args:
        username (str): Username to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if len(username) < 3:
        return False, 'Username must be at least 3 characters long'
    
    if len(username) > 20:
        return False, 'Username must be at most 20 characters long'
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, 'Username can only contain letters, numbers, and underscores'
    
    return True, ''

def sanitize_input(text):
    """
    Sanitize user input to prevent XSS.
    
    Args:
        text (str): Text to sanitize
        
    Returns:
        str: Sanitized text
    """
    # Remove dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&']
    for char in dangerous_chars:
        text = text.replace(char, '')
    return text
