"""Subject Notes routes."""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import StudentNote

notes_bp = Blueprint('notes', __name__, url_prefix='/notes')

@notes_bp.route('/')
@login_required
def index():
    """
    Subject Notes interface.
    """
    # Get all notes
    notes = StudentNote.query.filter_by(student_id=current_user.id).order_by(
        StudentNote.created_at.desc()
    ).all()
    
    subjects = ['Physics', 'Chemistry', 'Mathematics', 'Biology', 'English', 'History', 'Geography', 'Economics', 'Artificial Intelligence']
    
    return render_template('notes/index.html', notes=notes, subjects=subjects)

@notes_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    Create new note.
    """
    if request.method == 'POST':
        try:
            data = request.get_json()
            subject = data.get('subject', '').strip()
            title = data.get('title', '').strip()
            content = data.get('content', '').strip()
            tags = data.get('tags', '').strip()
            
            if not subject or not title or not content:
                return jsonify({'error': 'Subject, title, and content are required'}), 400
            
            note = StudentNote(
                student_id=current_user.id,
                subject=subject,
                title=title,
                content=content,
                tags=tags
            )
            db.session.add(note)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'note_id': note.id,
                'message': 'Note created successfully'
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    subjects = ['Physics', 'Chemistry', 'Mathematics', 'Biology', 'English', 'History', 'Geography', 'Economics', 'Artificial Intelligence']
    return render_template('notes/create.html', subjects=subjects)

@notes_bp.route('/<int:note_id>')
@login_required
def view(note_id):
    """
    View note.
    """
    note = StudentNote.query.filter_by(id=note_id, student_id=current_user.id).first()
    
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    
    return render_template('notes/view.html', note=note)

@notes_bp.route('/<int:note_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(note_id):
    """
    Edit note.
    """
    note = StudentNote.query.filter_by(id=note_id, student_id=current_user.id).first()
    
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            note.subject = data.get('subject', note.subject)
            note.title = data.get('title', note.title)
            note.content = data.get('content', note.content)
            note.tags = data.get('tags', note.tags)
            
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Note updated'})
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    subjects = ['Physics', 'Chemistry', 'Mathematics', 'Biology', 'English', 'History', 'Geography', 'Economics', 'Artificial Intelligence']
    return render_template('notes/edit.html', note=note, subjects=subjects)

@notes_bp.route('/<int:note_id>/delete', methods=['POST'])
@login_required
def delete(note_id):
    """
    Delete note.
    """
    try:
        note = StudentNote.query.filter_by(id=note_id, student_id=current_user.id).first()
        if not note:
            return jsonify({'error': 'Note not found'}), 404
        
        db.session.delete(note)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Note deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/<int:note_id>/pin', methods=['POST'])
@login_required
def toggle_pin(note_id):
    """
    Pin/unpin note.
    """
    try:
        note = StudentNote.query.filter_by(id=note_id, student_id=current_user.id).first()
        if not note:
            return jsonify({'error': 'Note not found'}), 404
        
        note.pinned = not note.pinned
        db.session.commit()
        
        return jsonify({'success': True, 'pinned': note.pinned})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/search')
@login_required
def search():
    """
    Search notes.
    """
    query = request.args.get('q', '').strip()
    subject = request.args.get('subject')
    
    search_query = StudentNote.query.filter_by(student_id=current_user.id)
    
    if subject:
        search_query = search_query.filter_by(subject=subject)
    
    if query:
        search_query = search_query.filter(
            db.or_(
                StudentNote.title.ilike(f'%{query}%'),
                StudentNote.content.ilike(f'%{query}%')
            )
        )
    
    notes = search_query.order_by(StudentNote.created_at.desc()).all()
    
    return jsonify([
        {
            'id': note.id,
            'subject': note.subject,
            'title': note.title,
            'content': note.content[:100] + '...' if len(note.content) > 100 else note.content,
            'tags': note.tags,
            'pinned': note.pinned,
            'created_at': note.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for note in notes
    ])
