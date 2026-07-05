# AI Student Assistant

A comprehensive web application for Class 11 students to enhance their learning experience using AI and modern web technologies.

## Features

### Core Features
- **AI Chat Tutor**: Ask academic questions and get instant AI responses
- **PDF Summarizer**: Upload study materials and get AI-generated summaries
- **Quiz Generator**: Auto-generate quizzes with multiple question types
- **Flashcards**: Create and practice flashcards for quick revision
- **Study Planner**: Get personalized study schedules and timetables
- **Progress Tracker**: Monitor your learning progress with charts and analytics
- **Subject Notes**: Organize and manage notes by subject
- **Admin Panel**: Manage users, uploads, and view statistics

### Subject Support
- English
- Physics
- Chemistry
- Mathematics
- Biology
- Geography
- History
- Economics
- Artificial Intelligence

## Tech Stack

- **Backend**: Python 3, Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Authentication**: Flask-Login
- **AI**: Google Gemini API
- **PDF Processing**: PyPDF2
- **Database Migration**: Alembic (optional)

## Installation Guide

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Google Gemini API Key

### Step 1: Clone the Repository
```bash
git clone https://github.com/shivamshaw348/Shivam.git
cd Shivam
```

### Step 2: Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Create .env file
cp .env.example .env
```

Edit `.env` and add:
```
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key
DATABASE_URL=sqlite:///instance/student_assistant.db
```

### Step 5: Initialize Database
```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
>>>     db.create_all()
>>> exit()
```

### Step 6: Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
Shivam/
├── app/
│   ├── __init__.py
│   ├── models.py                 # Database models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py               # Authentication routes
│   │   ├── dashboard.py          # Dashboard routes
│   │   ├── chat.py               # AI Chat routes
│   │   ├── summarizer.py         # PDF Summarizer routes
│   │   ├── quiz.py               # Quiz Generator routes
│   │   ├── flashcard.py          # Flashcard routes
│   │   ├── planner.py            # Study Planner routes
│   │   ├── progress.py           # Progress Tracker routes
│   │   ├── notes.py              # Subject Notes routes
│   │   ├── profile.py            # Profile routes
│   │   └── admin.py              # Admin routes
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── pdf_processor.py      # PDF processing utilities
│   │   ├── quiz_generator.py     # Quiz generation utilities
│   │   ├── flashcard_generator.py # Flashcard generation
│   │   ├── planner_generator.py  # Study plan generation
│   │   └── validators.py         # Input validation
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── dashboard/
│   │   │   └── index.html
│   │   ├── chat/
│   │   │   └── index.html
│   │   ├── summarizer/
│   │   │   ├── index.html
│   │   │   └── view_summary.html
│   │   ├── quiz/
│   │   │   ├── index.html
│   │   │   └── view_quiz.html
│   │   ├── flashcard/
│   │   │   └── index.html
│   │   ├── planner/
│   │   │   └── index.html
│   │   ├── progress/
│   │   │   └── index.html
│   │   ├── notes/
│   │   │   ├── index.html
│   │   │   ├── create.html
│   │   │   ├── edit.html
│   │   │   └── view.html
│   │   ├── profile/
│   │   │   ├── index.html
│   │   │   ├── edit.html
│   │   │   ├── settings.html
│   │   │   └── change_password.html
│   │   └── admin/
│   │       ├── dashboard.html
│   │       ├── users.html
│   │       ├── uploads.html
│   │       └── statistics.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── script.js
├── instance/
│   └── student_assistant.db      # SQLite database
├── uploads/                       # Uploaded PDFs
├── config.py                      # Configuration settings
├── app.py                         # Main application entry point
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
└── README.md                      # This file
```

## Usage Guide

### Registration & Login
1. Visit `http://localhost:5000/auth/register`
2. Fill in your details (name, email, school, class)
3. Create a password
4. Click Register
5. Login with your email and password

### AI Chat
1. Click on "AI Chat" in the sidebar
2. Select subject from dropdown
3. Type your question
4. Get instant AI-powered response
5. View chat history

### PDF Summarizer
1. Go to "PDF Summarizer"
2. Upload a PDF file
3. Select subject
4. System extracts text and generates summary
5. View key points and export as PDF

### Quiz Generator
1. Navigate to "Quiz Generator"
2. Select subject and topic
3. Choose quiz type (MCQ, True/False, etc.)
4. Answer all questions
5. Submit and view score

### Flashcards
1. Go to "Flashcards"
2. Select subject and topic
3. Generate flashcards
4. Click to flip cards
5. Mark as correct/incorrect for tracking

### Study Planner
1. Click "Study Planner"
2. Select subjects and exam date
3. Enter daily study hours
4. AI generates personalized schedule
5. View daily, weekly, and revision plans

### Progress Tracker
1. Go to "Progress Tracker"
2. Add topics to track
3. Update completion percentage with slider
4. View progress charts and statistics
5. Get weekly/monthly reports

## Database Models

### Student
- Username, Email, Password
- Name, School, Class
- Profile Picture, Theme
- Created/Updated timestamps

### StudentNote
- Subject, Title, Content
- Tags, Pinned status
- Created/Updated timestamps

### ChatHistory
- Student ID, Subject
- User message, AI response
- Timestamp, Helpful feedback

### Quiz
- Subject, Title
- Questions (JSON), Score
- Attempted status, Dates

### Flashcard
- Subject, Question, Answer
- Difficulty level
- Correct/Incorrect counts

### StudyPlanner
- Subjects, Exam date
- Daily hours, Schedules
- Revision schedule

### Progress
- Subject, Topic
- Completion percentage
- Completed date

### UploadedPDF
- Filename, Filepath
- Subject, File size
- Page count, Summary
- Key points (JSON)

## Security Features

- Password hashing with Werkzeug
- CSRF protection
- Secure session cookies
- Input validation and sanitization
- User authentication with Flask-Login
- Protected routes requiring login
- Admin-only functionalities

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout

### Chat
- `POST /chat/send` - Send chat message
- `GET /chat/history` - Get chat history
- `POST /chat/clear` - Clear chat
- `POST /chat/<id>/feedback` - Send feedback

### PDF Summarizer
- `POST /summarizer/upload` - Upload PDF
- `GET /summarizer/<id>` - View summary
- `POST /summarizer/<id>/export` - Export as PDF
- `POST /summarizer/<id>/delete` - Delete PDF

### Quiz
- `POST /quiz/generate` - Generate quiz
- `GET /quiz/<id>` - View quiz
- `POST /quiz/<id>/submit` - Submit answers
- `POST /quiz/<id>/delete` - Delete quiz

### Flashcards
- `POST /flashcard/generate` - Generate flashcards
- `GET /flashcard/<id>` - View card
- `POST /flashcard/<id>/feedback` - Record feedback
- `POST /flashcard/<id>/delete` - Delete card

### Study Planner
- `POST /planner/create` - Create plan
- `GET /planner/view` - View plan
- `POST /planner/update` - Update plan

### Progress
- `POST /progress/add` - Add topic
- `POST /progress/<id>/update` - Update progress
- `GET /progress/stats` - Get statistics
- `GET /progress/weekly-report` - Weekly report

### Notes
- `POST /notes/create` - Create note
- `GET /notes/<id>` - View note
- `POST /notes/<id>/edit` - Edit note
- `POST /notes/<id>/delete` - Delete note
- `POST /notes/<id>/pin` - Pin/unpin note

### Admin
- `GET /admin/` - Admin dashboard
- `GET /admin/users` - View all users
- `POST /admin/users/<id>/delete` - Delete user
- `GET /admin/uploads` - View all uploads
- `GET /admin/statistics` - View statistics

## Environment Variables

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-change-in-production

# Database
DATABASE_URL=sqlite:///instance/student_assistant.db

# Google Gemini API
GEMINI_API_KEY=your-api-key-here

# Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=52428800

# Application Settings
PAGES_PER_PAGE=20
```

## Troubleshooting

### Database Error
```bash
# Delete old database and recreate
rm instance/student_assistant.db
python app.py
```

### Import Error
```bash
# Reinstall requirements
pip install --upgrade -r requirements.txt
```

### Gemini API Not Working
- Check API key in `.env`
- Verify API is enabled in Google Cloud Console
- Check rate limits

### Port Already in Use
```bash
# Change port in app.py
app.run(port=5001)
```

## Performance Optimization

- Database indexing on frequently queried fields
- Pagination for large datasets
- Lazy loading of relationships
- Static file caching
- Efficient AI API calls

## Future Enhancements

- Email verification for registration
- Forgot password functionality
- Social media integration
- Video tutorials
- Discussion forums
- Real-time collaboration
- Mobile app
- Offline mode
- Export notes as PDF
- Grade prediction

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Create an issue on GitHub
- Email: support@aiassistant.edu

## Authors

- **Shivam Shaw** - Initial work

## Acknowledgments

- Google Gemini API
- Bootstrap 5
- Flask community
- Contributors and testers

## Disclaimer

This project is developed for educational purposes as a Class 11 school capstone project. Use responsibly and ensure proper attribution.

---

**Version**: 1.0.0
**Last Updated**: 2026-07-05
**Status**: Production Ready
