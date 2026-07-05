"""Routes package initialization."""

from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.chat import chat_bp
from app.routes.summarizer import summarizer_bp
from app.routes.quiz import quiz_bp
from app.routes.flashcard import flashcard_bp
from app.routes.planner import planner_bp
from app.routes.progress import progress_bp
from app.routes.notes import notes_bp
from app.routes.profile import profile_bp
from app.routes.admin import admin_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'chat_bp',
    'summarizer_bp',
    'quiz_bp',
    'flashcard_bp',
    'planner_bp',
    'progress_bp',
    'notes_bp',
    'profile_bp',
    'admin_bp'
]
