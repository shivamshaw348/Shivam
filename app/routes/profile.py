"""Profile routes."""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Student
from werkzeug.utils import secure_filename
import os
from datetime import datetime

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/')
@login_required
def index():
    """
    User profile page.
    """
    return render_template('profile/index.html', user=current_user)

@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """
    Edit profile information.
    """
    if request.method == 'POST':
        try:
            current_user.first_name = request.form.get('first_name', current_user.first_name)
            current_user.last_name = request.form.get('last_name', current_user.last_name)
            current_user.school = request.form.get('school', current_user.school)
            current_user.class_name = request.form.get('class', current_user.class_name)
            
            # Handle profile picture upload
            if 'profile_picture' in request.files:
                file = request.files['profile_picture']
                if file and file.filename != '':
                    filename = secure_filename(f"profile_{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
                    os.makedirs('uploads/profiles', exist_ok=True)
                    filepath = os.path.join('uploads/profiles', filename)
                    file.save(filepath)
                    current_user.profile_picture = filename
            
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Profile updated'})
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return render_template('profile/edit.html', user=current_user)

@profile_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """
    User settings page.
    """
    if request.method == 'POST':
        try:
            dark_mode = request.get_json().get('dark_mode', False)
            current_user.dark_mode = dark_mode
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Settings updated'})
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return render_template('profile/settings.html', user=current_user)

@profile_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Change password.
    """
    if request.method == 'POST':
        try:
            old_password = request.form.get('old_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            if not current_user.check_password(old_password):
                return jsonify({'error': 'Current password is incorrect'}), 400
            
            if len(new_password) < 8:
                return jsonify({'error': 'New password must be at least 8 characters'}), 400
            
            if new_password != confirm_password:
                return jsonify({'error': 'Passwords do not match'}), 400
            
            current_user.set_password(new_password)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Password changed successfully'})
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return render_template('profile/change_password.html')
