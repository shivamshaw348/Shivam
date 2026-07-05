"""PDF Summarizer routes."""

from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import UploadedPDF
from app.utils.pdf_processor import extract_text_from_pdf, generate_summary
import os
import json
from datetime import datetime

summarizer_bp = Blueprint('summarizer', __name__, url_prefix='/summarizer')

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@summarizer_bp.route('/')
@login_required
def index():
    """
    PDF Summarizer interface.
    """
    # Get uploaded PDFs
    pdfs = UploadedPDF.query.filter_by(student_id=current_user.id).order_by(
        UploadedPDF.created_at.desc()
    ).all()
    
    subjects = ['Physics', 'Chemistry', 'Mathematics', 'Biology', 'English', 'History', 'Geography', 'Economics', 'Artificial Intelligence']
    
    return render_template('summarizer/index.html', pdfs=pdfs, subjects=subjects)

@summarizer_bp.route('/upload', methods=['POST'])
@login_required
def upload_pdf():
    """
    Upload and process PDF file.
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        subject = request.form.get('subject', 'General').strip()
        
        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files allowed'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        upload_folder = 'uploads'
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Extract text
        extracted_text = extract_text_from_pdf(filepath)
        if not extracted_text:
            return jsonify({'error': 'Failed to extract text from PDF'}), 500
        
        # Generate summary
        summary = generate_summary(extracted_text)
        
        # Extract key points
        key_points = extract_key_points(extracted_text)
        
        # Get file size
        file_size = os.path.getsize(filepath)
        
        # Save to database
        pdf = UploadedPDF(
            student_id=current_user.id,
            filename=file.filename,
            filepath=filepath,
            subject=subject,
            file_size=file_size,
            summary=summary,
            key_points=json.dumps(key_points),
            extracted_text=extracted_text
        )
        db.session.add(pdf)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'pdf_id': pdf.id,
            'message': 'PDF uploaded and processed successfully'
        })
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@summarizer_bp.route('/<int:pdf_id>')
@login_required
def view_summary(pdf_id):
    """
    View PDF summary.
    """
    pdf = UploadedPDF.query.filter_by(id=pdf_id, student_id=current_user.id).first()
    
    if not pdf:
        return jsonify({'error': 'PDF not found'}), 404
    
    key_points = json.loads(pdf.key_points) if pdf.key_points else []
    
    return render_template('summarizer/view_summary.html', pdf=pdf, key_points=key_points)

@summarizer_bp.route('/<int:pdf_id>/delete', methods=['POST'])
@login_required
def delete_pdf(pdf_id):
    """
    Delete uploaded PDF.
    """
    try:
        pdf = UploadedPDF.query.filter_by(id=pdf_id, student_id=current_user.id).first()
        if not pdf:
            return jsonify({'error': 'PDF not found'}), 404
        
        # Delete file
        if os.path.exists(pdf.filepath):
            os.remove(pdf.filepath)
        
        # Delete from database
        db.session.delete(pdf)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'PDF deleted'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def extract_key_points(text, num_points=5):
    """
    Extract key points from text.
    """
    # Simple implementation - split by sentences and get top ones
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    # Return first num_points sentences as key points
    return sentences[:min(num_points, len(sentences))]
