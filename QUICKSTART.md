# Quick Start Guide - Career Assessment System

## 🚀 Get Started in 5 Minutes

### Step 1: Prerequisites
- Python 3.11 installed
- VS Code or terminal access
- Project folder: `AI-Powered-Career-Path-Assessment-and-Academic-Forecasting-System`

### Step 2: Start the Server
```bash
cd careerpath
python manage.py runserver 0.0.0.0:8000
```

✅ You should see: "Starting development server at http://0.0.0.0:8000/"

### Step 3: Access the Application
Open your browser and go to: **http://localhost:8000/**

## 📋 What's Ready to Use

### ✅ Already Populated
- ✅ 14 Career Paths (IT, Engineering, Education, Healthcare, etc.)
- ✅ 14 Assessment Questions (Skills, Personality, Aptitude)
- ✅ 20 In-Demand Careers (with salary and job growth data)
- ✅ Database fully migrated and configured

### ✅ Available Features
1. **Student Registration & Login**
2. **Assessment Engine** - 14 comprehensive questions
3. **Career Recommendations** - AI-powered matching
4. **Academic Forecasting** - Success prediction
5. **Job Market Matching** - Top 20 careers
6. **QR Code Profiling** - Generate unique codes
7. **Admin Dashboard** - Counselor monitoring
8. **Student Reports** - Detailed analytics

## 👤 Test Account Walkthrough

### 1. Register a Student
- Go to http://localhost:8000/
- Click **"Register"**
- Fill in:
  ```
  Student ID: TEST001
  First Name: John
  Last Name: Doe
  Email: john@test.com
  Password: TestPass123
  ```
- Click **"Register"**

### 2. Login
- Use same credentials
- Click **"Login"**

### 3. Take Assessment
- Click **"Start Assessment"**
- Answer all 14 questions
- Click **"Submit Assessment"**
- View your score and initial recommendations

### 4. View Career Recommendations
- Click **"View Career Recommendations"**
- See top 3 matches with compatibility scores
- Check required skills for each path

### 5. Academic Forecast
- Select a career path
- Fill form and submit
- View success prediction and improvement areas

### 6. Job Market Matching
- Browse top 20 in-demand careers
- See salary ranges and job growth
- Compare with your skills

### 7. QR Profile
- Click **"View QR Profile"**
- See your unique QR code
- Project link: http://localhost:8000/student/{your-code}/results/

## 🔐 Admin Access

### Create Admin Account
```bash
python manage.py createsuperuser
```

Follow prompts to create admin account:
```
Username: admin
Email: admin@test.com
Password: AdminPass123
```

### Access Admin Panel
- Go to http://localhost:8000/admin/
- Login with admin credentials

### Admin Features Available
1. **Manage Students** - View/edit student profiles
2. **Career Paths** - Add/edit career information
3. **Assessment Questions** - Manage question bank
4. **In-Demand Careers** - Update market data
5. **Student Reports** - Add counselor notes
6. **Analytics Dashboard** - View statistics

### Counselor Dashboard
- Go to http://localhost:8000/admin/dashboard/
- View student progress
- Monitor assessment completion
- Manage student reports

## 🛠️ Useful Commands

### Database Management
```bash
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (WARNING: deletes all data)
rm db.sqlite3
python manage.py migrate
python manage.py populate_initial_data
```

### Data Population
```bash
# Populate with test data
python manage.py populate_initial_data
```

### Django Shell (Interactive)
```bash
python manage.py shell

# Example: Check student count
from career.models import StudentUser
StudentUser.objects.count()
```

## 📊 System Statistics

### Current Data
| Component | Count | Status |
|-----------|-------|--------|
| Career Paths | 14 | ✅ Ready |
| Assessment Questions | 14 | ✅ Ready |
| In-Demand Careers | 20 | ✅ Ready |
| Students | 0 | Ready for registration |
| Assessments | 0 | Ready to start |

## 🔗 Quick Links

| Feature | URL |
|---------|-----|
| 🏠 Home | http://localhost:8000/ |
| 🔑 Login | http://localhost:8000/login/ |
| 📝 Register | http://localhost:8000/register/ |
| 📊 Dashboard | http://localhost:8000/dashboard/ |
| 📝 Assessment | http://localhost:8000/assessment/start/ |
| 💼 Careers | http://localhost:8000/career/recommendations/ |
| 📈 Forecast | http://localhost:8000/forecast/academic/ |
| 💹 Job Market | http://localhost:8000/career/job-market-matching/ |
| 🔗 QR Profile | http://localhost:8000/profile/qr/ |
| 👨‍💼 Admin Panel | http://localhost:8000/admin/ |
| 📋 Counselor Dashboard | http://localhost:8000/admin/dashboard/ |
| 👥 Student List | http://localhost:8000/admin/students/ |

## ⚡ Key Features Explained

### 1. Assessment Scoring
- **Skill Questions**: 1-5 rating scale
- **Personality Questions**: Agree/Disagree scale
- **Aptitude Questions**: Multiple choice
- **Total Questions**: 14
- **Average Time**: 15-20 minutes

### 2. Recommendation Engine
- Analyzes 5 skill areas
- Evaluates 5 personality traits
- Assesses 4 aptitude dimensions
- Generates compatibility score (0-100%)
- Returns top 3 career matches

### 3. Academic Forecasting
- Success rate prediction based on skills
- Identifies 3-5 improvement areas
- Recommends 4-5 relevant courses
- Compares against career requirements

### 4. QR Code System
- Unique code per student
- Embed profile URL
- Shareable format
- Printable
- Quick access to profile

## 🐛 Troubleshooting

### Port 8000 Already in Use
```bash
python manage.py runserver 0.0.0.0:8001
```

### Database Locked
```bash
# Stop server (Ctrl+C) and restart
python manage.py runserver 0.0.0.0:8000
```

### Missing Templates
```bash
python manage.py check
```

### ModuleNotFoundError
```bash
pip install -r requirements.txt
```

## 📚 Full Documentation

For comprehensive documentation, see:
- **README.md** - Complete system documentation
- **models.py** - Database schema details
- **views.py** - View logic documentation
- **urls.py** - URL routing

## ✨ Next Steps

1. ✅ Register test student
2. ✅ Complete assessment
3. ✅ Review recommendations
4. ✅ Generate forecast
5. ✅ View QR profile
6. ✅ Access admin dashboard
7. ✅ Add counselor notes
8. ⏳ Invite real students
9. ⏳ Monitor progress
10. ⏳ Generate reports

## 🎯 System is Ready!

Your Career Assessment System is **fully functional** and ready to use. 

**Current Status**: ✅ OPERATIONAL
- Database: ✅ Configured
- Server: ✅ Running
- Data: ✅ Populated
- Features: ✅ Ready

Start by registering a test account and taking the assessment!

---

**Need Help?**
- Check full README.md for detailed documentation
- Review Django admin panel at http://localhost:8000/admin/
- Check server logs in terminal for error messages
