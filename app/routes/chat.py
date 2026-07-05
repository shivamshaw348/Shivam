"""
AI Chat routes for student-AI conversations.
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import ChatHistory
import google.generativeai as genai
from datetime import datetime

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

def get_gemini_client():
    """
    Initialize and return Gemini API client.
    """
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError('GEMINI_API_KEY not configured')
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-pro')

@chat_bp.route('/')
@login_required
def index():
    """
    Display AI chat interface.
    """
    return render_template('chat/index.html')

@chat_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    """
    Send message to AI and get response.
    """
    data = request.get_json()
    user_message = data.get('message', '').strip()
    subject = data.get('subject', 'General')
    
    if not user_message:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    if len(user_message) > 2000:
        return jsonify({'error': 'Message too long (max 2000 characters)'}), 400
    
    try:
        # Get response from Gemini API
        client = get_gemini_client()
        prompt = f"You are an AI tutor helping a Class 11 student with {subject}. Answer this question helpfully and concisely: {user_message}"
        response = client.generate_content(prompt)
        ai_response = response.text
        
        # Save to chat history
        chat = ChatHistory(
            student_id=current_user.id,
            subject=subject,
            user_message=user_message,
            ai_response=ai_response
        )
        db.session.add(chat)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': f'Error generating response: {str(e)}'}), 500

@chat_bp.route('/history')
@login_required
def get_history():
    """
    Get chat history for current user.
    """
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    chats = ChatHistory.query.filter_by(student_id=current_user.id).order_by(
        ChatHistory.timestamp.desc()
    ).paginate(page=page, per_page=per_page)
    
    data = {
        'chats': [
            {
                'id': chat.id,
                'subject': chat.subject,
                'user_message': chat.user_message[:100],
                'timestamp': chat.timestamp.isoformat(),
                'is_helpful': chat.is_helpful
            }
            for chat in chats.items
        ],
        'total': chats.total,
        'pages': chats.pages
    }
    
    return jsonify(data)

@chat_bp.route('/clear', methods=['POST'])
@login_required
def clear_chat():
    """
    Clear chat history for current user.
    """
    ChatHistory.query.filter_by(student_id=current_user.id).delete()
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Chat history cleared'})

@chat_bp.route('/<int:chat_id>/feedback', methods=['POST'])
@login_required
def send_feedback(chat_id):
    """
    Send feedback on AI response.
    """
    chat = ChatHistory.query.get_or_404(chat_id)
    
    if chat.student_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    is_helpful = data.get('is_helpful')
    
    chat.is_helpful = is_helpful
    db.session.commit()
    
    return jsonify({'success': True})
