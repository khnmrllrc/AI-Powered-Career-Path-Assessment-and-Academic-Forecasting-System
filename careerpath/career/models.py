from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import qrcode
from io import BytesIO
import base64
import json

COURSE_CATEGORY_CHOICES = [
    ('it', 'Information Technology'),
    ('engineering', 'Engineering'),
    ('education', 'Education'),
    ('hospitality', 'Hospitality Management (BSHRM)'),
    ('entrepreneurship', 'Entrepreneurship'),
    ('aviation', 'Aviation (Pilot)'),
    ('psychology', 'Psychology'),
    ('biology', 'Biology'),
    ('nursing', 'Nursing'),
    ('criminology', 'Criminology'),
    ('physical_therapy', 'Physical Therapy'),
    ('adtech', 'Agricultural Technology (ADTech)'),
    ('business', 'Business'),
    ('science', 'Science'),
]

class StudentUser(AbstractUser):
    student_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField('first name', max_length=30, blank=True)
    middle_name = models.CharField(max_length=50, blank=True)
    suffix = models.CharField(max_length=10, blank=True)
    email = models.EmailField(unique=True)
    qr_code = models.UUIDField(null=True, blank=True, unique=True)
    
    # Override username to ensure it's never empty (required, non-null, unique)
    username = models.CharField(
        max_length=150,
        unique=True,
        null=False,
        blank=False,
        error_messages={'unique': 'A user with that username already exists.'},
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def generate_qr_code(self, target_url=None):
        """Generate QR code for the student's assessment results page."""
        if not self.qr_code:
            self.qr_code = uuid.uuid4()
            self.save(update_fields=['qr_code'])

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=12,
            border=4,
        )
        qr.add_data(target_url or f"/student/{self.qr_code}/results/")
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"


class CareerPath(models.Model):
    """Predefined career paths"""
    CATEGORIES = COURSE_CATEGORY_CHOICES
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORIES)
    description = models.TextField()
    required_skills = models.TextField(default='[]', help_text="JSON list of required skills")
    courses = models.TextField(default='[]', help_text="JSON list of recommended courses")
    success_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_required_skills(self):
        try:
            return json.loads(self.required_skills)
        except:
            return []
    
    def set_required_skills(self, skills):
        self.required_skills = json.dumps(skills)
    
    def get_courses(self):
        try:
            return json.loads(self.courses)
        except:
            return []
    
    def set_courses(self, courses):
        self.courses = json.dumps(courses)


class AssessmentQuestion(models.Model):
    """Questions for the assessment"""
    QUESTION_TYPES = [
        ('skill', 'Skill Assessment'),
        ('personality', 'Personality'),
        ('aptitude', 'Aptitude'),
    ]
    
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    category = models.CharField(max_length=50)  # Science, IT, Engineering, etc.
    options = models.TextField(help_text="JSON list of options")
    order = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['question_text', 'question_type']
    
    def __str__(self):
        return f"{self.category} - {self.question_text[:50]}"
    
    def get_options(self):
        try:
            return json.loads(self.options)
        except:
            return []

    def get_normalized_options(self):
        normalized = []

        for option in self.get_options():
            if isinstance(option, dict):
                normalized.append({
                    'text': option.get('text', ''),
                    'points': option.get('points', {}) if isinstance(option.get('points', {}), dict) else {},
                })
            else:
                normalized.append({
                    'text': str(option),
                    'points': {},
                })

        return normalized
    
    def set_options(self, options):
        self.options = json.dumps(options)


class AssessmentLibraryFile(models.Model):
    """Files that counselors can distribute as assessment materials."""
    title = models.CharField(max_length=150)
    course_category = models.CharField(max_length=50, choices=COURSE_CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='assessment_library/')
    is_active = models.BooleanField(default=True)
    uploaded_by = models.ForeignKey(
        StudentUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_assessment_files',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['course_category', 'title']

    def __str__(self):
        return f"{self.title} ({self.get_course_category_display()})"

    @property
    def filename(self):
        return self.file.name.rsplit('/', 1)[-1] if self.file else ''


class StudentAssessment(models.Model):
    """Student's assessment attempt"""
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    student = models.OneToOneField(StudentUser, on_delete=models.CASCADE, related_name='assessment')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    total_score = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student} - {self.status}"


class AssessmentResponse(models.Model):
    """Student's response to each question"""
    assessment = models.ForeignKey(StudentAssessment, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE)
    selected_option = models.IntegerField()  # Index of selected option
    points_earned = models.TextField(default='{}', help_text="JSON dict of points")
    
    class Meta:
        unique_together = ['assessment', 'question']
    
    def __str__(self):
        return f"{self.assessment} - Q{self.question.order}"
    
    def get_points_earned(self):
        try:
            return json.loads(self.points_earned)
        except:
            return {}
    
    def set_points_earned(self, points):
        self.points_earned = json.dumps(points)


class CareerRecommendation(models.Model):
    """AI-generated career recommendations for student"""
    student = models.OneToOneField(StudentUser, on_delete=models.CASCADE, related_name='career_recommendation')
    career_paths = models.ManyToManyField(CareerPath)
    recommendation_text = models.TextField()
    compatibility_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    generated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student} - Recommendations"


class AcademicForecast(models.Model):
    """Academic success prediction"""
    student = models.OneToOneField(StudentUser, on_delete=models.CASCADE, related_name='academic_forecast')
    selected_career_path = models.ForeignKey(CareerPath, on_delete=models.SET_NULL, null=True)
    predicted_success_rate = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    improvement_areas = models.TextField(default='[]', help_text="JSON list of areas to improve")
    recommended_subjects = models.TextField(default='[]', help_text="JSON list of recommended subjects")
    forecast_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student} - Forecast for {self.selected_career_path}"
    
    def get_improvement_areas(self):
        try:
            return json.loads(self.improvement_areas)
        except:
            return []
    
    def set_improvement_areas(self, areas):
        self.improvement_areas = json.dumps(areas)
    
    def get_recommended_subjects(self):
        try:
            return json.loads(self.recommended_subjects)
        except:
            return []
    
    def set_recommended_subjects(self, subjects):
        self.recommended_subjects = json.dumps(subjects)


class InDemandCareer(models.Model):
    """Top in-demand careers in the job market"""
    SALARY_RANGES = [
        ('entry', 'Entry Level (0-2 years)'),
        ('mid', 'Mid Level (2-5 years)'),
        ('senior', 'Senior Level (5+ years)'),
    ]
    
    rank = models.IntegerField(unique=True)  # Top 1-20
    title = models.CharField(max_length=100)
    description = models.TextField()
    required_skills = models.TextField(default='[]', help_text="JSON list of required skills")
    average_salary = models.CharField(max_length=100)
    job_growth = models.CharField(max_length=50)  # e.g., "15% per year"
    related_careers = models.ManyToManyField(CareerPath, blank=True)
    
    class Meta:
        ordering = ['rank']
    
    def __str__(self):
        return f"#{self.rank} - {self.title}"
    
    def get_required_skills(self):
        try:
            return json.loads(self.required_skills)
        except:
            return []
    
    def set_required_skills(self, skills):
        self.required_skills = json.dumps(skills)


class StudentSkillProfile(models.Model):
    """Student's identified skills"""
    student = models.OneToOneField(StudentUser, on_delete=models.CASCADE, related_name='skill_profile')
    skills = models.TextField(default='{}', help_text="JSON dict of skills")
    strengths = models.TextField(default='[]', help_text="JSON list of strengths")
    weaknesses = models.TextField(default='[]', help_text="JSON list of weaknesses")
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student} - Skills"
    
    def get_skills(self):
        try:
            return json.loads(self.skills)
        except:
            return {}
    
    def set_skills(self, skills_dict):
        self.skills = json.dumps(skills_dict)
    
    def get_strengths(self):
        try:
            return json.loads(self.strengths)
        except:
            return []
    
    def set_strengths(self, strengths_list):
        self.strengths = json.dumps(strengths_list)
    
    def get_weaknesses(self):
        try:
            return json.loads(self.weaknesses)
        except:
            return []
    
    def set_weaknesses(self, weaknesses_list):
        self.weaknesses = json.dumps(weaknesses_list)


class StudentReport(models.Model):
    """Comprehensive student report for counselors/admins"""
    student = models.OneToOneField(StudentUser, on_delete=models.CASCADE, related_name='student_report')
    assessment_score = models.FloatField(null=True, blank=True)
    recommended_paths = models.ManyToManyField(CareerPath)
    counselor_notes = models.TextField(blank=True)
    is_flagged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Report - {self.student}"
