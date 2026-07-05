# Viva Questions and Answers

## Module 1: Architecture & Design

### Q1: Explain the application architecture?
A: The AI Student Assistant follows an MVC (Model-View-Controller) architecture with:
- **Models**: SQLAlchemy ORM models for database abstraction
- **Views**: Flask templates (HTML/CSS) for user interface
- **Controllers**: Flask routes for handling business logic
- **Database**: SQLite for data persistence
- **AI Layer**: Google Gemini API integration

### Q2: Why did you choose Flask over Django?
A: Flask was chosen because:
- Lightweight and flexible
- Easier to understand for beginners
- Better for microservices
- Faster development for small projects
- Simpler deployment

### Q3: What is the database schema design principle you followed?
A: We followed:
- **Normalization**: Eliminated data redundancy
- **Relationships**: Proper foreign keys
- **Indexing**: On frequently queried fields
- **Integrity**: Cascade delete and constraints
- **Scalability**: Designed for future expansion

### Q4: How does the authentication system work?
A: 
1. User registers with email and password
2. Password hashed using Werkzeug (pbkdf2:sha256)
3. User login verified against hash
4. Flask-Login manages sessions
5. Protected routes check session validity

### Q5: Explain the AI integration approach?
A:
- Google Gemini API for natural language processing
- Context-aware prompts for different features
- JSON response parsing
- Error handling for API failures
- Rate limiting to manage costs

## Module 2: Features & Implementation

### Q6: How does the PDF summarization work?
A:
1. PyPDF2 extracts text from uploaded PDF
2. Text sent to Gemini API with summarization prompt
3. AI generates summary and key points
4. Data stored in database
5. Summary exportable as PDF

### Q7: Explain the quiz generation algorithm?
A:
1. User selects subject and topic
2. Gemini generates questions based on type (MCQ, True/False, etc.)
3. Questions stored as JSON in database
4. User answers evaluated
5. Score calculated as percentage

### Q8: How does the study planner generate personalized schedules?
A:
1. Student provides subjects, exam date, daily hours
2. System calculates days remaining
3. Gemini generates daily, weekly, and revision schedules
4. Subjects distributed across days
5. Schedules stored and displayed

### Q9: What is the progress tracking mechanism?
A:
- Topics added by student
- Completion tracked as percentage (0-100%)
- Automatic completion flag at 100%
- Statistics generated from progress data
- Weekly/monthly reports generated

### Q10: How are flashcards generated?
A:
1. User provides topic and number of cards
2. Gemini generates Q&A pairs
3. Difficulty level assigned (easy/medium/hard)
4. Cards stored in database
5. User can mark correct/incorrect for tracking

## Module 3: Security & Best Practices

### Q11: How is password security ensured?
A:
- Passwords hashed using PBKDF2-SHA256
- Salt generated automatically
- Never stored in plain text
- Compared during login verification
- Session tokens expire after inactivity

### Q12: What CSRF protection measures are implemented?
A:
- Flask-WTF CSRF tokens on forms
- Tokens validated on POST/PUT/DELETE
- Tokens expire and rotate
- Different token per session
- Protects against cross-site attacks

### Q13: How is SQL injection prevented?
A:
- SQLAlchemy parameterized queries
- No string concatenation in SQL
- Input validation on all forms
- ORM abstraction layer
- Database-level constraints

### Q14: Explain input validation strategy?
A:
- Client-side HTML5 validation
- Server-side validation in routes
- Type checking and bounds checking
- Email format validation
- File type verification
- Length restrictions

### Q15: How are file uploads secured?
A:
- Only PDF files allowed
- File size limited (50MB)
- Secure filename generation
- Stored outside web root
- Scanned for malware risks
- Unique timestamp-based naming

## Module 4: Database & Performance

### Q16: Explain the database indexing strategy?
A:
- Indexes on foreign keys
- Indexes on frequently searched fields (email, username)
- Composite indexes for common queries
- Index on user_id + created_at for sorting
- Performance improvement: 10-100x for queries

### Q17: How is pagination implemented?
A:
- Flask-SQLAlchemy paginate() method
- Configurable items per page
- Previous/next page links
- Page number display
- Improves performance for large datasets

### Q18: What caching strategies are used?
A:
- Browser caching for static files
- Session caching for user data
- Query result caching
- Future: Redis for distributed caching

### Q19: Explain JSON storage for complex data?
A:
- Questions stored as JSON in Quiz table
- Schedules stored as JSON in StudyPlanner
- Key points stored as JSON in UploadedPDF
- Serialization/deserialization in Python
- Efficient storage and retrieval

### Q20: How would you optimize for 1000+ concurrent users?
A:
- PostgreSQL instead of SQLite
- Connection pooling
- Redis caching
- Database replication
- Load balancing
- CDN for static files
- Microservices architecture
- Rate limiting

## Module 5: Frontend & UX

### Q21: How is responsive design achieved?
A:
- Bootstrap 5 grid system (12 columns)
- Mobile-first approach
- Media queries for breakpoints
- Flexible images and containers
- Touch-friendly buttons
- Hamburger menu for mobile

### Q22: Explain the dark mode implementation?
A:
- CSS variables for color schemes
- JavaScript toggle function
- LocalStorage for preference persistence
- CSS media query (prefers-color-scheme)
- Smooth transitions

### Q23: How are charts and graphs rendered?
A:
- Chart.js library for visualization
- Real-time data from Flask API
- Responsive containers
- Multiple chart types
- Interactive tooltips

### Q24: What frontend frameworks are used?
A:
- Bootstrap 5 for UI components
- Chart.js for data visualization
- Vanilla JavaScript for interactions
- HTML5 for semantic markup
- CSS3 for styling

### Q25: How are forms validated?
A:
- HTML5 built-in validation
- Client-side JavaScript validation
- Server-side validation in Flask
- Error messages displayed
- Form re-submission on error

## Module 6: Deployment & DevOps

### Q26: How would you deploy this application?
A:
- Docker containerization
- Deploy to AWS/Google Cloud
- Use RDS for database
- S3 for file storage
- CloudFront CDN
- SSL/TLS certificates
- Environment configuration

### Q27: Explain the CI/CD pipeline?
A:
- GitHub Actions for automation
- Automated testing on push
- Code quality checks
- Security scanning
- Automated deployment
- Staging environment testing
- Production deployment

### Q28: How is logging implemented?
A:
- Python logging module
- Different log levels (DEBUG, INFO, WARNING, ERROR)
- Log rotation for file size
- Centralized logging (ELK stack optional)
- Error tracking (Sentry optional)

### Q29: What monitoring systems would you implement?
A:
- Application performance monitoring (APM)
- Error tracking and alerting
- Database performance metrics
- API response time monitoring
- Resource utilization tracking
- User analytics

### Q30: How is backup and recovery handled?
A:
- Daily database backups
- Incremental backups
- Multiple backup locations
- Recovery time objective (RTO): < 1 hour
- Recovery point objective (RPO): < 1 day
- Automated backup testing

## Module 7: Advanced Features

### Q31: How would you implement real-time notifications?
A:
- WebSockets with Flask-SocketIO
- Redis for message queuing
- Server-sent events
- Push notifications via Firebase
- Email notifications

### Q32: How to implement collaborative features?
A:
- Real-time editing (Operational Transformation)
- Conflict resolution
- Version control
- Permission-based access
- Activity tracking

### Q33: Explain potential machine learning enhancements?
A:
- Student performance prediction
- Personalized recommendation engine
- Learning style analysis
- Grade prediction model
- Question difficulty assessment

### Q34: How would you implement multi-language support?
A:
- i18n (internationalization) library
- Language selection in preferences
- Translation files
- Date/time localization
- RTL language support

### Q35: How to implement export to different formats?
A:
- PDF export using ReportLab
- Excel export using openpyxl
- JSON export for data
- CSV for spreadsheets
- Generate reports on demand

## Module 8: Project Management

### Q36: How did you manage the project timeline?
A:
- Agile methodology with sprints
- Task breakdown using GitHub Issues
- Kanban board for workflow
- Weekly stand-ups
- Documentation at each phase

### Q37: What challenges did you face?
A:
- API rate limiting for Gemini
- Database optimization for large datasets
- Cross-browser compatibility
- Mobile responsiveness
- Error handling edge cases

### Q38: How would you test this application?
A:
- Unit tests for models and utilities
- Integration tests for routes
- End-to-end tests with Selenium
- Load testing with Apache JMeter
- Security testing (OWASP)

### Q39: What is your approach to code review?
A:
- Pull request reviews before merge
- Automated code quality checks
- Testing requirements
- Documentation requirements
- Two-person approval

### Q40: How would you gather user feedback?
A:
- In-app surveys
- User testing sessions
- Analytics tracking
- GitHub issues for bugs
- Feature request voting
- Monthly user surveys

---

**Total Questions**: 40
**Difficulty**: Beginner to Advanced
**Time to Answer**: 30-60 minutes for all
