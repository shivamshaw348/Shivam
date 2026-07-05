#!/usr/bin/env python3
"""
AI Student Assistant - Main Application Entry Point
A comprehensive web application for student learning assistance
using AI and modern web technologies.
"""

import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import timedelta

# Load environment variables
load_dotenv()

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name='development'):
    """
    Application factory function to create and configure the Flask app.
    
    Args:
        config_name (str): Configuration environment name
        
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 
        'sqlite:///instance/student_assistant.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    
    # Google Gemini API Key
    app.config['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')
    
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('instance', exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Register blueprints
    from app.routes import auth_bp, dashboard_bp, chat_bp, summarizer_bp, quiz_bp, flashcard_bp, planner_bp, progress_bp, notes_bp, profile_bp, admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(summarizer_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(flashcard_bp)
    app.register_blueprint(planner_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)
    
    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import Student
        return Student.query.get(int(user_id))
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Page not found'}, 404
    
    @app.errorhandler(500)
    def server_error(error):
        return {'error': 'Server error'}, 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
