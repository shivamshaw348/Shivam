"""
User profile management routes.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Student
from werkzeug.utils import secure_filename
import os
from datetime import datetime

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """
    Check if file extension is allowed.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_bp.route('/')
@login_required
def index():
    """
    Display user profile.
    """
    return render_template('profile/index.html', user=current_user)

@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """
    Edit user profile.
    """
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        school = request.form.get('school', '').strip()
        class_grade = request.form.get('class_grade', '').strip()
        
        if not all([first_name, last_name]):
            flash('First name and last name are required', 'danger')
            return redirect(url_for('profile.edit'))
        
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.school = school
        current_user.class_grade = class_grade
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"profile_{current_user.id}.{file.filename.rsplit('.', 1)[1]}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                current_user.profile_picture = filename
        
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile.index'))
    
    return render_template('profile/edit.html', user=current_user)

@profile_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """
    User settings.
    """
    if request.method == 'POST':
        theme = request.form.get('theme', 'light')
        current_user.theme = theme
        db.session.commit()
        
        flash('Settings updated', 'success')
        return redirect(url_for('profile.settings'))
    
    return render_template('profile/settings.html', user=current_user)

@profile_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Change user password.
    """
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        new_password_confirm = request.form.get('new_password_confirm', '')
        
        if not all([current_password, new_password, new_password_confirm]):
            flash('All fields are required', 'danger')
            return redirect(url_for('profile.change_password'))
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('profile.change_password'))
        
        if new_password != new_password_confirm:
            flash('New passwords do not match', 'danger')
            return redirect(url_for('profile.change_password'))
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return redirect(url_for('profile.change_password'))
        
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Password changed successfully', 'success')
        return redirect(url_for('profile.index'))
    
    return render_template('profile/change_password.html')
