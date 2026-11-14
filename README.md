# AI-Powered Career Path Assessment and Academic Forecasting System

## System Overview

A comprehensive Django-based application for assessing student skills and aptitudes, providing personalized career recommendations, and forecasting academic success in chosen career paths.

## Features

### 🎓 Core Features

1. **Adaptive Assessment Engine**
   - Skill assessment questions
   - Personality evaluation
   - Aptitude testing
   - Real-time score calculation
   - Adaptive difficulty based on responses

2. **Career Recommendations**
   - AI-powered career path matching
   - Compatibility scoring (0-100%)
   - Required skills identification
   - Course recommendations
   - Multiple career path suggestions

3. **Academic Forecasting**
   - Success rate prediction (0-100%)
   - Improvement area identification
   - Recommended course suggestions
   - Personalized learning path

4. **Job Market Matching**
   - Top 20 in-demand careers
   - Salary range information
   - Job growth percentages
   - Skill-to-career matching
   - Career compatibility analysis

5. **QR Code Profiling**
   - Unique student QR codes
   - Quick profile access
   - Printable profile format
   - Profile sharing capability

6. **Admin & Counselor Dashboard**
   - Student monitoring
   - Assessment tracking
   - Counselor notes and flagging
   - Analytics and reporting
   - Student performance insights

## Technology Stack

- **Backend**: Django 5.2.13 (Python 3.11+)
- **Database**: SQLite3
- **Frontend**: Bootstrap 5.3.3, Font Awesome 6.4.0
- **Additional Libraries**: qrcode[pil], Pillow

## Installation & Setup

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Installation Steps

1. **Navigate to project directory:**
```bash
cd careerpath
```

2. **Activate virtual environment (if using venv):**
```bash
# Windows
..\venv\Scripts\activate

# Linux/Mac
source ../venv/bin/activate
```

3. **Install dependencies:**
```bash
# Windows
pip install -r ..\requirements.txt

# Linux/Mac
pip install -r ../requirements.txt
```

For local development, the application uses an intentionally insecure fallback
`SECRET_KEY`. Before deploying, set a private `DJANGO_SECRET_KEY` environment
variable and configure Django's production security settings.

4. **Apply migrations:**
```bash
python manage.py migrate
```

5. **Populate initial data:**
```bash
python manage.py populate_initial_data
```

6. **Create superuser (admin account):**
```bash
python manage.py createsuperuser
```

7. **Run development server:**
```bash
python manage.py runserver 0.0.0.0:8000
```

8. **Access the application:**
- Main site: http://localhost:8000/
- Admin panel: http://localhost:8000/admin/

## Usage Guide

### 📱 Student Workflow

#### 1. Registration
- Visit homepage and register with student_id
- Fill in personal information
- Create secure password

#### 2. Take Assessment
- Login to dashboard
- Click "Start Assessment"
- Answer 14 questions covering:
  - Technical skills
  - Mathematical abilities
  - Communication skills
  - Personality traits
  - Logical reasoning
  - Aptitude levels

#### 3. View Results
- See assessment score breakdown
- Identify skill strengths
- Review initial career recommendations

#### 4. Career Recommendations
- Review top 3 recommended career paths
- Check required skills for each path
- View suggested courses
- Explore career details and success rates

#### 5. Academic Forecasting
- Select a specific career path
- System generates success prediction
- Review improvement areas
- Get recommended courses
- Identify skill gaps

#### 6. Job Market Matching
- Browse top 20 in-demand careers
- See current market salaries
- Check job growth trends
- Match personal skills to market demands
- Explore related career paths

#### 7. QR Profile
- Generate unique QR code
- Share profile via QR code
- Print profile information
- Quick-access student profile

### 👨‍💼 Admin/Counselor Workflow

#### 1. Access Admin Dashboard
- Login as staff member
- View overall statistics
- Monitor student progress
- See completed assessments

#### 2. Student List
- View all students
- Filter by assessment status
- Quick access to student profiles
- Sort by registration date

#### 3. Student Report
- View complete student profile
- Review assessment scores
- Check recommendations
- View academic forecast
- Add counselor notes
- Flag students for follow-up

#### 4. Analytics
- Track completion rates
- Monitor flagged students
- Review recent activities
- Generate performance reports

## Database Models

### Student Models
- **StudentUser**: Custom user model with student_id authentication
- **StudentSkillProfile**: Tracks student skills and competencies
- **StudentReport**: Counselor monitoring and notes

### Assessment Models
- **StudentAssessment**: Tracks assessment attempts
- **AssessmentQuestion**: Question bank with 14 initial questions
- **AssessmentResponse**: Individual question responses and scores

### Recommendation Models
- **CareerPath**: 14 predefined career paths
- **CareerRecommendation**: Generated recommendations (top 3 matches)
- **AcademicForecast**: Success predictions and improvement areas

### Career Models
- **InDemandCareer**: Top 20 in-demand careers with market data

## API Endpoints

### Student Endpoints
- `GET /` - Homepage
- `POST /login/` - User login
- `POST /register/` - User registration
- `GET /logout/` - User logout
- `GET /dashboard/` - Student dashboard
- `GET/POST /assessment/start/` - Assessment interface
- `GET /assessment/results/` - Assessment results
- `GET /career/recommendations/` - Career recommendations
- `GET /career/in-demand/` - In-demand careers list
- `GET /career/job-market-matching/` - Job matching
- `GET/POST /forecast/academic/` - Academic forecast form
- `GET /forecast/results/` - Forecast results
- `GET /profile/qr/` - QR profile

### Admin Endpoints
- `GET /admin/` - Django admin
- `GET /admin/dashboard/` - Counselor dashboard
- `GET /admin/students/` - Students list
- `GET /admin/student/<student_id>/` - Student report

## File Structure

```
careerpath/
├── manage.py
├── db.sqlite3
├── career/
│   ├── models.py           # 10 database models
│   ├── views.py            # 17+ view functions
│   ├── forms.py            # 3 form classes
│   ├── urls.py             # URL routing
│   ├── admin.py            # Django admin configuration
│   ├── management/
│   │   └── commands/
│   │       └── populate_initial_data.py
│   ├── migrations/         # Database migrations
│   └── templates/
│       ├── base.html
│       ├── home.html
│       ├── dashboard.html
│       ├── assessment/
│       │   ├── take_assessment.html
│       │   └── results.html
│       ├── career/
│       │   ├── recommendations.html
│       │   ├── in_demand_careers.html
│       │   └── job_market_matching.html
│       ├── forecast/
│       │   ├── academic_forecast.html
│       │   └── forecast_results.html
│       ├── profile/
│       │   └── qr_profile.html
│       ├── admin/
│       │   ├── counselor_dashboard.html
│       │   ├── students_list.html
│       │   └── student_report.html
│       └── registration/
│           ├── login.html
│           └── register.html
├── careerpath/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── templates/
    ├── base.html
    └── (inherited templates)
```

## Configuration

### Key Settings (settings.py)

```python
# Authentication
AUTH_USER_MODEL = 'career.StudentUser'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(BASE_DIR / 'db.sqlite3'),
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

## Testing Guide

### 1. User Registration Test

```
1. Go to http://localhost:8000/
2. Click "Register"
3. Fill in:
   - Student ID: TEST001
   - First Name: John
   - Last Name: Doe
   - Email: john@example.com
   - Password: SecurePass123!
4. Submit and verify registration successful
```

### 2. Assessment Test

```
1. Login with created account
2. Click "Start Assessment"
3. Answer all 14 questions
4. Submit assessment
5. Verify:
   - Score is calculated (0-100)
   - Results page shows breakdown
   - Recommendations appear
```

### 3. Career Recommendations Test

```
1. From results, click "View Recommendations"
2. Verify 3 career paths displayed
3. Check required skills visible
4. Click on career for details
```

### 4. Academic Forecast Test

```
1. Go to Forecast section
2. Select a career path
3. Submit form
4. Verify:
   - Success rate displayed
   - Improvement areas shown
   - Recommended courses listed
```

### 5. Admin Dashboard Test

```
1. Create superuser:
   python manage.py createsuperuser
2. Go to http://localhost:8000/admin/
3. Login with superuser credentials
4. Verify:
   - Student list visible
   - Assessment data accessible
   - Can add counselor notes
5. Go to counselor dashboard:
   - Should show analytics
   - Student list with filters
```

## Troubleshooting

### Common Issues

#### 1. "Module not found: qrcode"
```bash
pip install qrcode[pil]
```

#### 2. "No migrations for app 'career'"
```bash
python manage.py makemigrations career
python manage.py migrate
```

#### 3. "Unable to connect to database"
```bash
# Check database file exists
ls -la careerpath/db.sqlite3

# Reset database
rm db.sqlite3
python manage.py migrate
```

#### 4. "Port 8000 already in use"
```bash
python manage.py runserver 0.0.0.0:8001
```

## Performance Optimization

### Recommendations
1. Add database indexing for frequently queried fields
2. Implement caching for career recommendations
3. Use select_related() in views for foreign keys
4. Implement pagination for large student lists
5. Consider adding asynchronous task processing

## Security Considerations

1. **Custom Authentication**: Uses student_id instead of username
2. **Password Security**: Django's built-in password hashing
3. **CSRF Protection**: Enabled by default
4. **SQL Injection**: Protected via Django ORM
5. **HTTPS**: Recommended for production deployment

### Recommended Changes for Production
```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## Future Enhancements

1. **Advanced Analytics**
   - Student performance trends
   - Success rate improvements
   - Career path popularity tracking

2. **AI Improvements**
   - Personalized recommendation algorithm
   - Machine learning-based predictions
   - Adaptive difficulty questions

3. **UI Enhancements**
   - Dashboard charts and visualizations
   - PDF report generation
   - Mobile app version

4. **Integration Features**
   - LinkedIn profile linking
   - Job board integration
   - University course mapping

## Support & Documentation

### Key Files
- [TODO.md](TODO.md) - Outstanding tasks and improvements
- [models.py](career/models.py) - Database schema documentation
- [views.py](career/views.py) - View logic documentation
- [Admin Interface](http://localhost:8000/admin/) - Database management

### Admin Features
- Create/Edit/Delete students
- Manage career paths
- Add assessment questions
- Modify in-demand careers

## License

[Specify your license here]

## Contact

[Your contact information]

---

**Last Updated**: April 16, 2026
**System Status**: ✅ Fully Operational
**Database**: ✅ Populated with test data
**Server**: ✅ Running on localhost:8000
