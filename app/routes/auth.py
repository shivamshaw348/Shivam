"""Authentication routes."""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Student
from app.utils.validators import validate_email, validate_password

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route.
    
    GET: Display registration form
    POST: Process registration form
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        school = request.form.get('school', '').strip()
        class_name = request.form.get('class', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        # Validation
        if not all([username, email, first_name, last_name, password]):
            flash('All fields are required!', 'error')
            return redirect(url_for('auth.register'))
        
        if not validate_email(email):
            flash('Invalid email format!', 'error')
            return redirect(url_for('auth.register'))
        
        if not validate_password(password):
            flash('Password must be at least 8 characters long!', 'error')
            return redirect(url_for('auth.register'))
        
        if password != password_confirm:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('auth.register'))
        
        # Check if user exists
        if Student.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return redirect(url_for('auth.register'))
        
        if Student.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return redirect(url_for('auth.register'))
        
        # Create new student
        try:
            student = Student(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                school=school,
                class_name=class_name,
                is_admin=True if Student.query.count() == 0 else False  # First user is admin
            )
            student.set_password(password)
            
            db.session.add(student)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'error')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route.
    
    GET: Display login form
    POST: Process login form
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Email and password are required!', 'error')
            return redirect(url_for('auth.login'))
        
        # Find student by email
        student = Student.query.filter_by(email=email).first()
        
        if student and student.check_password(password):
            login_user(student, remember=request.form.get('remember'))
            flash(f'Welcome back, {student.first_name}!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.index'))
        
        else:
            flash('Invalid email or password!', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """
    User logout route.
    """
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
