"""
PDF processing utilities for text extraction and summarization.
"""

from PyPDF2 import PdfReader
import google.generativeai as genai
from flask import current_app
import json

def process_pdf(filepath):
    """
    Extract text and metadata from PDF file.
    
    Args:
        filepath (str): Path to PDF file
        
    Returns:
        tuple: (extracted_text, page_count)
    """
    try:
        reader = PdfReader(filepath)
        page_count = len(reader.pages)
        text = ""
        
        for page in reader.pages:
            text += page.extract_text()
        
        return text, page_count
    
    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")

def generate_summary(text, subject):
    """
    Generate AI summary of PDF text.
    
    Args:
        text (str): Extracted text from PDF
        subject (str): Subject name
        
    Returns:
        dict: Summary data with key points, definitions, formulas
    """
    try:
        api_key = current_app.config.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError('GEMINI_API_KEY not configured')
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Generate summary
        summary_prompt = f"""
        Summarize the following text about {subject} in 3-4 paragraphs. 
        Be concise and focus on key concepts.
        
        Text: {text[:3000]}
        """
        
        summary_response = model.generate_content(summary_prompt)
        summary = summary_response.text
        
        # Extract key points
        keypoints_prompt = f"""
        Extract 5-7 key points from the following text about {subject}.
        Format as a JSON array of strings.
        
        Text: {text[:3000]}
        
        Return only valid JSON array, no extra text.
        """
        
        keypoints_response = model.generate_content(keypoints_prompt)
        try:
            key_points = json.loads(keypoints_response.text)
        except:
            key_points = ["Key point 1", "Key point 2", "Key point 3"]
        
        return {
            'summary': summary,
            'key_points': key_points,
            'definitions': [],
            'formulas': []
        }
    
    except Exception as e:
        raise Exception(f"Error generating summary: {str(e)}")

def export_summary_pdf(pdf_model):
    """
    Export summary as PDF file.
    
    Args:
        pdf_model: UploadedPDF model instance
        
    Returns:
        str: Path to exported PDF
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.units import inch
        import os
        from flask import current_app
        
        # Create PDF
        output_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            f'summary_{pdf_model.id}.pdf'
        )
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor='#0066cc',
            spaceAfter=30,
            alignment=1
        )
        elements.append(Paragraph(f"Summary: {pdf_model.filename}", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Summary
        if pdf_model.summary:
            elements.append(Paragraph("<b>Summary</b>", styles['Heading2']))
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(pdf_model.summary, styles['BodyText']))
            elements.append(Spacer(1, 0.3*inch))
        
        # Key Points
        if pdf_model.key_points:
            elements.append(Paragraph("<b>Key Points</b>", styles['Heading2']))
            elements.append(Spacer(1, 0.1*inch))
            key_points = json.loads(pdf_model.key_points)
            for point in key_points:
                elements.append(Paragraph(f"• {point}", styles['BodyText']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        doc.build(elements)
        
        return output_path
    
    except Exception as e:
        raise Exception(f"Error exporting PDF: {str(e)}")
