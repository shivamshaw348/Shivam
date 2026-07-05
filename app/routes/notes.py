"""
Student notes management routes.
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import StudentNote
from datetime import datetime

notes_bp = Blueprint('notes', __name__, url_prefix='/notes')

SUBJECTS = [
    'English', 'Physics', 'Chemistry', 'Mathematics',
    'Biology', 'Geography', 'History', 'Economics', 'Artificial Intelligence'
]

@notes_bp.route('/')
@login_required
def index():
    """
    Display all student notes.
    """
    page = request.args.get('page', 1, type=int)
    subject = request.args.get('subject', '')
    search = request.args.get('search', '')
    
    query = StudentNote.query.filter_by(student_id=current_user.id)
    
    if subject:
        query = query.filter_by(subject=subject)
    
    if search:
        query = query.filter(
            db.or_(
                StudentNote.title.ilike(f'%{search}%'),
                StudentNote.content.ilike(f'%{search}%'),
                StudentNote.tags.ilike(f'%{search}%')
            )
        )
    
    notes = query.order_by(StudentNote.updated_at.desc()).paginate(page=page, per_page=10)
    
    return render_template('notes/index.html',
                         notes=notes,
                         subjects=SUBJECTS,
                         current_subject=subject,
                         search_query=search)

@notes_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    Create a new note.
    """
    if request.method == 'POST':
        data = request.get_json() or request.form
        subject = data.get('subject', '').strip()
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        tags = data.get('tags', '').strip()
        
        if not all([subject, title, content]):
            if request.is_json:
                return jsonify({'error': 'Subject, title, and content are required'}), 400
            flash('Please fill in all required fields', 'danger')
            return redirect(url_for('notes.create'))
        
        note = StudentNote(
            student_id=current_user.id,
            subject=subject,
            title=title,
            content=content,
            tags=tags
        )
        
        db.session.add(note)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'note_id': note.id})
        
        flash('Note created successfully', 'success')
        return redirect(url_for('notes.view', note_id=note.id))
    
    return render_template('notes/create.html', subjects=SUBJECTS)

@notes_bp.route('/<int:note_id>')
@login_required
def view(note_id):
    """
    View a specific note.
    """
    note = StudentNote.query.get_or_404(note_id)
    
    if note.student_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return render_template('notes/view.html', note=note)

@notes_bp.route('/<int:note_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(note_id):
    """
    Edit an existing note.
    """
    note = StudentNote.query.get_or_404(note_id)
    
    if note.student_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'POST':
        data = request.get_json() or request.form
        note.subject = data.get('subject', note.subject).strip()
        note.title = data.get('title', note.title).strip()
        note.content = data.get('content', note.content).strip()
        note.tags = data.get('tags', note.tags).strip()
        note.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True})
        
        flash('Note updated successfully', 'success')
        return redirect(url_for('notes.view', note_id=note.id))
    
    return render_template('notes/edit.html', note=note, subjects=SUBJECTS)

@notes_bp.route('/<int:note_id>/delete', methods=['POST'])
@login_required
def delete(note_id):
    """
    Delete a note.
    """
    note = StudentNote.query.get_or_404(note_id)
    
    if note.student_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(note)
    db.session.commit()
    
    if request.is_json:
        return jsonify({'success': True, 'message': 'Note deleted'})
    
    flash('Note deleted successfully', 'success')
    return redirect(url_for('notes.index'))

@notes_bp.route('/<int:note_id>/pin', methods=['POST'])
@login_required
def pin_note(note_id):
    """
    Pin or unpin a note.
    """
    note = StudentNote.query.get_or_404(note_id)
    
    if note.student_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    note.is_pinned = not note.is_pinned
    db.session.commit()
    
    return jsonify({'success': True, 'is_pinned': note.is_pinned})
