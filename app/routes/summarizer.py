"""
PDF summarizer routes for document processing and summarization.
"""

from flask import Blueprint, render_template, request, jsonify, current_app, send_file
from flask_login import login_required, current_user
from app import db
from app.models import UploadedPDF
from app.utils.pdf_processor import process_pdf, generate_summary, export_summary_pdf
import os
from werkzeug.utils import secure_filename
import google.generativeai as genai
import json

summarizer_bp = Blueprint('summarizer', __name__, url_prefix='/summarizer')

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """
    Check if file extension is allowed.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@summarizer_bp.route('/')
@login_required
def index():
    """
    Display PDF summarizer interface.
    """
    pdfs = UploadedPDF.query.filter_by(student_id=current_user.id).order_by(
        UploadedPDF.uploaded_at.desc()
    ).all()
    
    return render_template('summarizer/index.html', pdfs=pdfs)

@summarizer_bp.route('/upload', methods=['POST'])
@login_required
def upload_pdf():
    """
    Handle PDF file upload and processing.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    subject = request.form.get('subject', 'General')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    if file.content_length > current_app.config['MAX_CONTENT_LENGTH']:
        return jsonify({'error': 'File too large'}), 400
    
    try:
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract text from PDF
        text, page_count = process_pdf(filepath)
        
        # Generate summary using Gemini
        summary_data = generate_summary(text, subject)
        
        # Save to database
        pdf = UploadedPDF(
            student_id=current_user.id,
            filename=file.filename,
            filepath=filepath,
            subject=subject,
            file_size=os.path.getsize(filepath),
            page_count=page_count,
            summary=summary_data.get('summary'),
            key_points=json.dumps(summary_data.get('key_points', []))
        )
        db.session.add(pdf)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'pdf_id': pdf.id,
            'message': 'PDF uploaded and processed successfully'
        })
    
    except Exception as e:
        return jsonify({'error': f'Error processing PDF: {str(e)}'}), 500

@summarizer_bp.route('/<int:pdf_id>')
@login_required
def view_summary(pdf_id):
    """
    Display summary for a specific PDF.
    """
    pdf = UploadedPDF.query.get_or_404(pdf_id)
    
    if pdf.student_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    key_points = json.loads(pdf.key_points) if pdf.key_points else []
    
    return render_template('summarizer/view_summary.html',
                         pdf=pdf,
                         key_points=key_points)

@summarizer_bp.route('/<int:pdf_id>/export', methods=['POST'])
@login_required
def export_pdf(pdf_id):
    """
    Export summary as PDF.
    """
    pdf = UploadedPDF.query.get_or_404(pdf_id)
    
    if pdf.student_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        output_path = export_summary_pdf(pdf)
        return send_file(output_path, as_attachment=True, download_name=f'summary_{pdf.id}.pdf')
    except Exception as e:
        return jsonify({'error': f'Error exporting PDF: {str(e)}'}), 500

@summarizer_bp.route('/<int:pdf_id>/delete', methods=['POST'])
@login_required
def delete_pdf(pdf_id):
    """
    Delete uploaded PDF and associated data.
    """
    pdf = UploadedPDF.query.get_or_404(pdf_id)
    
    if pdf.student_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        if os.path.exists(pdf.filepath):
            os.remove(pdf.filepath)
        db.session.delete(pdf)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'PDF deleted'})
    except Exception as e:
        return jsonify({'error': f'Error deleting PDF: {str(e)}'}), 500

from datetime import datetime
