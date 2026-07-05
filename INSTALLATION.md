# Installation and Setup Guide

## System Requirements

- Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- Python 3.8 or higher
- 500MB free disk space
- 2GB RAM minimum
- Internet connection for AI features

## Step-by-Step Installation

### 1. Download and Install Python

**Windows:**
- Download from https://www.python.org/downloads/
- Run installer and check "Add Python to PATH"
- Verify: `python --version`

**macOS:**
```bash
brew install python3
```

**Linux:**
```bash
sudo apt-get install python3 python3-pip
```

### 2. Get Gemini API Key

1. Visit https://makersuite.google.com/app/apikey
2. Click "Get an API key"
3. Create new API key
4. Copy and save the key

### 3. Clone Repository

```bash
git clone https://github.com/shivamshaw348/Shivam.git
cd Shivam
```

### 4. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Environment

**Create `.env` file:**
```bash
cp .env.example .env
```

**Edit `.env` with your settings:**
```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-12345
GEMINI_API_KEY=your-api-key-here
DATABASE_URL=sqlite:///instance/student_assistant.db
UPLOAD_FOLDER=uploads
```

### 7. Initialize Database

```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### 8. Run Application

```bash
python app.py
```

Open browser and go to: `http://localhost:5000`

## First Time Setup

### Create Admin Account

1. Click "Register"
2. Fill in details:
   - First Name: Admin
   - Last Name: User
   - Email: admin@example.com
   - Username: admin
   - Password: Admin@123
3. Click Register
4. Login with the credentials

Note: First user registered automatically gets admin access.

### Test Features

1. **AI Chat**: Ask "What is photosynthesis?"
2. **Upload PDF**: Upload any study material PDF
3. **Generate Quiz**: Create a sample quiz
4. **Create Note**: Add a test note
5. **Study Planner**: Create a plan for exam preparation

## Troubleshooting

### Issue: "Python not found"
**Solution:**
- Reinstall Python with "Add to PATH" checked
- Restart terminal/command prompt
- Use `python3` instead of `python`

### Issue: "Module not found"
**Solution:**
```bash
# Ensure virtual environment is activated
# Reinstall requirements
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: "Database locked"
**Solution:**
```bash
# Delete database and recreate
rm instance/student_assistant.db
python app.py
```

### Issue: "Gemini API error"
**Solution:**
- Check API key in `.env`
- Verify API is enabled in Google Cloud
- Check internet connection
- Check API quota

### Issue: "Port 5000 already in use"
**Solution:**
```bash
# Use different port
# Edit app.py line: app.run(port=5001)
```

## Running on Different Ports

```bash
# Edit app.py
# Change: app.run(port=5000)
# To: app.run(port=YOUR_PORT)

python app.py
```

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Using Heroku

1. Create `Procfile`:
```
web: gunicorn app:app
```

2. Deploy:
```bash
git push heroku main
```

### Using Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

Build and run:
```bash
docker build -t ai-student-assistant .
docker run -p 8000:8000 ai-student-assistant
```

## Updating Application

```bash
# Pull latest changes
git pull origin main

# Upgrade dependencies
pip install --upgrade -r requirements.txt

# Restart application
python app.py
```

## Backup Database

```bash
# Copy database file
cp instance/student_assistant.db backup_$(date +%Y%m%d).db
```

## Reset Application

```bash
# Delete database
rm instance/student_assistant.db

# Delete uploaded files
rm -rf uploads/*

# Recreate database
python app.py
```

## Getting Help

1. Check README.md
2. Review error messages
3. Check GitHub issues
4. Contact support

---

For more information, see README.md
