"""PDF processing utilities."""

import PyPDF2
from typing import Optional
from app.utils.gemini_api import ask_gemini, generate_summary_prompt

def extract_text_from_pdf(filepath: str) -> Optional[str]:
    """
    Extract text from PDF file.
    
    Args:
        filepath (str): Path to PDF file
        
    Returns:
        str: Extracted text or None if error
    """
    try:
        text = ""
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        
        return text if text else None
    
    except Exception as e:
        print(f"PDF Extraction Error: {str(e)}")
        return None

def generate_summary(text: str) -> Optional[str]:
    """
    Generate summary from extracted text.
    
    Args:
        text (str): Text to summarize
        
    Returns:
        str: Generated summary or None if error
    """
    try:
        prompt = generate_summary_prompt(text)
        summary = ask_gemini(prompt)
        return summary
    
    except Exception as e:
        print(f"Summary Generation Error: {str(e)}")
        return None

def get_page_count(filepath: str) -> Optional[int]:
    """
    Get number of pages in PDF.
    
    Args:
        filepath (str): Path to PDF file
        
    Returns:
        int: Number of pages or None if error
    """
    try:
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            return len(pdf_reader.pages)
    
    except Exception as e:
        print(f"Page Count Error: {str(e)}")
        return None
