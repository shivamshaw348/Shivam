"""
Authentication routes for registration, login, and logout.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Student
from functools import wraps

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def anonymous_required(f):
    """
    Decorator to prevent logged-in users from accessing auth pages.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
@anonymous_required
def register():
    """
    Handle student registration.
    
    Methods:
        GET: Display registration form
        POST: Process registration form submission
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        school = request.form.get('school', '').strip()
        class_grade = request.form.get('class_grade', '').strip()
        
        # Validation
        if not all([username, email, password, first_name, last_name]):
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('auth.register'))
        
        if password != password_confirm:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('auth.register'))
        
        if Student.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('auth.register'))
        
        if Student.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Create new student
        student = Student(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            school=school,
            class_grade=class_grade
        )
        student.set_password(password)
        
        db.session.add(student)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
@anonymous_required
def login():
    """
    Handle student login.
    
    Methods:
        GET: Display login form
        POST: Process login credentials
    """
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not email or not password:
            flash('Please enter email and password.', 'danger')
            return redirect(url_for('auth.login'))
        
        student = Student.query.filter_by(email=email).first()
        
        if student and student.check_password(password) and student.is_active:
            login_user(student, remember=remember)
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """
    Handle student logout.
    """
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
