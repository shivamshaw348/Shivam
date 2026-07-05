"""Database models for AI Student Assistant."""

from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

class Student(UserMixin, db.Model):
    """Student user model."""
    __tablename__ = 'student'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    school = db.Column(db.String(100))
    class_name = db.Column(db.String(20))
    profile_picture = db.Column(db.String(200), default='default.jpg')
    dark_mode = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    notes = db.relationship('StudentNote', backref='student', lazy=True, cascade='all, delete-orphan')
    chat_history = db.relationship('ChatHistory', backref='student', lazy=True, cascade='all, delete-orphan')
    quizzes = db.relationship('Quiz', backref='student', lazy=True, cascade='all, delete-orphan')
    flashcards = db.relationship('Flashcard', backref='student', lazy=True, cascade='all, delete-orphan')
    planners = db.relationship('StudyPlanner', backref='student', lazy=True, cascade='all, delete-orphan')
    progress = db.relationship('Progress', backref='student', lazy=True, cascade='all, delete-orphan')
    pdfs = db.relationship('UploadedPDF', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Student {self.username}>'

class StudentNote(db.Model):
    """Model for student notes."""
    __tablename__ = 'student_note'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False, index=True)
    subject = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(200))
    pinned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Note {self.title}>'

class ChatHistory(db.Model):
    """Model for chat history."""
    __tablename__ = 'chat_history'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False, index=True)
    subject = db.Column(db.String(50), nullable=False)
    user_message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    helpful = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Chat {self.id}>'

class Quiz(db.Model):
    """Model for quizzes."""
    __tablename__ = 'quiz'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False, index=True)
    subject = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    questions = db.Column(db.Text, nullable=False)  # JSON
    user_answers = db.Column(db.Text)  # JSON
    score = db.Column(db.Float)
    total_questions = db.Column(db.Integer)
    attempted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def get_questions(self):
        """Get questions as list."""
        return json.loads(self.questions) if self.questions else []
    
    def set_questions(self, questions):
        """Set questions from list."""
        self.questions = json.dumps(questions)
    
    def __repr__(self):
        return f'<Quiz {self.title}>'

class Flashcard(db.Model):
    """Model for flashcards."""
    __tablename__ = 'flashcard'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False, index=True)
    subject = db.Column(db.String(50), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard
    correct_count = db.Column(db.Integer, default=0)
    incorrect_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_reviewed = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Flashcard {self.question[:50]}>'

class StudyPlanner(db.Model):
    """Model for study plans."""
    __tablename__ = 'study_planner'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False, index=True)
    subjects = db.Column(db.Text, nullable=False)  # JSON array
    exam_date = db.Column(db.Date, nullable=False)
    daily_hours = db.Column(db.Float, nullable=False)
    daily_schedule = db.Column(db.Text)  # JSON
    weekly_schedule = db.Column(db.Text)  # JSON
    revision_schedule = db.Column(db.Text)  # JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_subjects(self):
        """Get subjects as list."""
        return json.loads(self.subjects) if self.subjects else []
    
    def set_subjects(self, subjects):
        """Set subjects from list."""
        self.subjects = json.dumps(subjects)
    
    def __repr__(self):
        return f'<StudyPlanner {self.id}>'

class Progress(db.Model):
    """Model for progress tracking."""
    __tablename__ = 'progress'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False, index=True)
    subject = db.Column(db.String(50), nullable=False)
    topic = db.Column(db.String(200), nullable=False)
    completion_percentage = db.Column(db.Float, default=0.0)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Progress {self.topic}>'

class UploadedPDF(db.Model):
    """Model for uploaded PDFs."""
    __tablename__ = 'uploaded_pdf'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False, index=True)
    filename = db.Column(db.String(200), nullable=False)
    filepath = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer)
    page_count = db.Column(db.Integer)
    summary = db.Column(db.Text)
    key_points = db.Column(db.Text)  # JSON
    extracted_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PDF {self.filename}>'
