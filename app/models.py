"""
Database models for the AI Student Assistant application.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class Student(UserMixin, db.Model):
    """
    Student user model for authentication and profile management.
    """
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    school = db.Column(db.String(120), nullable=True)
    class_grade = db.Column(db.String(10), nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)
    theme = db.Column(db.String(20), default='light')  # light or dark
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    notes = db.relationship('StudentNote', backref='student', lazy=True, cascade='all, delete-orphan')
    chat_history = db.relationship('ChatHistory', backref='student', lazy=True, cascade='all, delete-orphan')
    quizzes = db.relationship('Quiz', backref='student', lazy=True, cascade='all, delete-orphan')
    flashcards = db.relationship('Flashcard', backref='student', lazy=True, cascade='all, delete-orphan')
    planner = db.relationship('StudyPlanner', backref='student', lazy=True, cascade='all, delete-orphan')
    progress = db.relationship('Progress', backref='student', lazy=True, cascade='all, delete-orphan')
    uploads = db.relationship('UploadedPDF', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """
        Hash and set the student's password.
        
        Args:
            password (str): Plain text password
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Verify password against hash.
        
        Args:
            password (str): Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Student {self.username}>'

class StudentNote(db.Model):
    """
    Model for storing student notes by subject.
    """
    __tablename__ = 'student_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    subject = db.Column(db.String(80), nullable=False)  # Subject name
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(255), nullable=True)  # Comma-separated tags
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_pinned = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Note {self.title} - {self.subject}>'

class ChatHistory(db.Model):
    """
    Model for storing AI chat conversation history.
    """
    __tablename__ = 'chat_history'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    subject = db.Column(db.String(80), nullable=True)
    user_message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    is_helpful = db.Column(db.Boolean, nullable=True)  # Feedback
    
    def __repr__(self):
        return f'<Chat {self.student_id} - {self.timestamp}>'

class Quiz(db.Model):
    """
    Model for storing generated quizzes.
    """
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    subject = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    questions_data = db.Column(db.Text, nullable=False)  # JSON format
    score = db.Column(db.Float, nullable=True)
    total_questions = db.Column(db.Integer, default=20)
    attempted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def get_questions(self):
        """Parse JSON questions data"""
        return json.loads(self.questions_data) if self.questions_data else []
    
    def set_questions(self, questions):
        """Store questions as JSON"""
        self.questions_data = json.dumps(questions)
    
    def __repr__(self):
        return f'<Quiz {self.title} - {self.subject}>'

class Flashcard(db.Model):
    """
    Model for storing flashcards.
    """
    __tablename__ = 'flashcards'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    subject = db.Column(db.String(80), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard
    correct_count = db.Column(db.Integer, default=0)
    incorrect_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<Flashcard {self.question[:50]}...>'

class StudyPlanner(db.Model):
    """
    Model for storing study plans and schedules.
    """
    __tablename__ = 'study_planner'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    subjects = db.Column(db.Text, nullable=False)  # JSON list
    exam_date = db.Column(db.DateTime, nullable=False)
    daily_hours = db.Column(db.Integer, nullable=False)
    daily_schedule = db.Column(db.Text, nullable=True)  # JSON format
    weekly_schedule = db.Column(db.Text, nullable=True)  # JSON format
    revision_schedule = db.Column(db.Text, nullable=True)  # JSON format
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_subjects(self):
        """Parse subjects JSON"""
        return json.loads(self.subjects) if self.subjects else []
    
    def set_subjects(self, subjects):
        """Store subjects as JSON"""
        self.subjects = json.dumps(subjects)
    
    def __repr__(self):
        return f'<StudyPlanner {self.student_id} - {self.exam_date}>'

class Progress(db.Model):
    """
    Model for tracking student progress.
    """
    __tablename__ = 'progress'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    subject = db.Column(db.String(80), nullable=False)
    topic = db.Column(db.String(200), nullable=False)
    completion_percentage = db.Column(db.Float, default=0)
    completed = db.Column(db.Boolean, default=False)
    completed_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('student_id', 'subject', 'topic'),)
    
    def __repr__(self):
        return f'<Progress {self.student_id} - {self.topic}>'

class UploadedPDF(db.Model):
    """
    Model for storing uploaded PDF file information.
    """
    __tablename__ = 'uploaded_pdfs'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False, unique=True)
    subject = db.Column(db.String(80), nullable=True)
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    page_count = db.Column(db.Integer, nullable=True)
    summary = db.Column(db.Text, nullable=True)
    key_points = db.Column(db.Text, nullable=True)  # JSON format
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<UploadedPDF {self.filename}>'

class Admin(db.Model):
    """
    Admin user model for administrative functions.
    """
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Admin {self.username}>'
