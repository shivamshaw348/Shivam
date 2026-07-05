"""AI Chat routes."""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import ChatHistory
from app.utils.gemini_api import ask_gemini
from datetime import datetime

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/')
@login_required
def index():
    """
    AI Chat interface.
    """
    # Get chat history grouped by subject
    chat_history = ChatHistory.query.filter_by(student_id=current_user.id).order_by(
        ChatHistory.created_at.desc()
    ).all()
    
    # Get unique subjects
    subjects = ['Physics', 'Chemistry', 'Mathematics', 'Biology', 'English', 'History', 'Geography', 'Economics', 'Artificial Intelligence']
    
    return render_template('chat/index.html', chat_history=chat_history, subjects=subjects)

@chat_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    """
    Send chat message and get AI response.
    """
    data = request.get_json()
    message = data.get('message', '').strip()
    subject = data.get('subject', 'General').strip()
    
    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    try:
        # Create prompt with subject context
        prompt = f"""You are an expert tutor for {subject}. Answer the following question:
        
Question: {message}

Provide a clear, concise, and educational answer."""
        
        # Get AI response
        ai_response = ask_gemini(prompt)
        
        if not ai_response:
            return jsonify({'error': 'Failed to get response from AI'}), 500
        
        # Save to database
        chat = ChatHistory(
            student_id=current_user.id,
            subject=subject,
            user_message=message,
            ai_response=ai_response
        )
        db.session.add(chat)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'chat_id': chat.id,
            'response': ai_response,
            'timestamp': chat.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@chat_bp.route('/history')
@login_required
def get_history():
    """
    Get chat history.
    """
    subject = request.args.get('subject')
    
    query = ChatHistory.query.filter_by(student_id=current_user.id)
    if subject:
        query = query.filter_by(subject=subject)
    
    chats = query.order_by(ChatHistory.created_at.desc()).all()
    
    return jsonify([
        {
            'id': chat.id,
            'subject': chat.subject,
            'message': chat.user_message,
            'response': chat.ai_response,
            'timestamp': chat.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for chat in chats
    ])

@chat_bp.route('/clear', methods=['POST'])
@login_required
def clear_chat():
    """
    Clear chat history.
    """
    try:
        ChatHistory.query.filter_by(student_id=current_user.id).delete()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Chat history cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/<int:chat_id>/feedback', methods=['POST'])
@login_required
def send_feedback(chat_id):
    """
    Send feedback on chat response.
    """
    try:
        chat = ChatHistory.query.filter_by(id=chat_id, student_id=current_user.id).first()
        if not chat:
            return jsonify({'error': 'Chat not found'}), 404
        
        helpful = request.get_json().get('helpful')
        chat.helpful = helpful
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Feedback recorded'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
