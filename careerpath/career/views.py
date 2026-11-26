from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, FileResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.db.models import Avg, Count, Q
from datetime import datetime
import json
import socket
import uuid
from pathlib import Path
from urllib.parse import urlsplit


from django.db import IntegrityError
from .forms import (
    LoginForm,
    RegisterForm,
    AssessmentQuestionForm,
    AssessmentCategoryForm,
    AssessmentLibraryFileForm,
    CareerPathSelectionForm,
    CounselorNotesForm,
)
from .models import (
    StudentUser, StudentAssessment, AssessmentResponse, AssessmentQuestion,
    CareerRecommendation, AcademicForecast, InDemandCareer, StudentSkillProfile,
    StudentReport, CareerPath, AssessmentLibraryFile, COURSE_CATEGORY_CHOICES
)

LOGO_PATH = Path(__file__).resolve().parent / 'static' / 'career' / 'aclc-logo.png'


def get_lan_ip_address():
    """Return the IPv4 address used for outbound network traffic."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as network_socket:
            network_socket.connect(('8.8.8.8', 80))
            return network_socket.getsockname()[0]
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except OSError:
            return '127.0.0.1'


def get_qr_results_url(request, student):
    """Build a QR URL using the configured public address or LAN fallback."""
    path = reverse('public_assessment_results', args=[student.qr_code])
    if settings.QR_PUBLIC_BASE_URL:
        return f"{settings.QR_PUBLIC_BASE_URL.rstrip('/')}{path}"

    host = request.get_host()
    parsed_host = urlsplit(f'//{host}')
    hostname = parsed_host.hostname

    if hostname in {'localhost', '127.0.0.1', '0.0.0.0', '::1'}:
        hostname = get_lan_ip_address()
        host = f'{hostname}:{parsed_host.port}' if parsed_host.port else hostname
        return f'{request.scheme}://{host}{path}'

    return request.build_absolute_uri(path)

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


def aclc_logo(request):
    """Serve the ACLC logo without depending on staticfiles configuration."""
    if not LOGO_PATH.exists():
        raise Http404('Logo file not found.')
    return FileResponse(LOGO_PATH.open('rb'), content_type='image/png')

from django.contrib.auth import logout as auth_logout

@require_http_methods(["POST"])
def logout_view(request):
    auth_logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')

@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        submitted_student_id = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = StudentUser.objects.filter(
            Q(student_id=submitted_student_id) |
            Q(username=submitted_student_id) |
            Q(email__iexact=submitted_student_id)
        ).first()

        auth_username = user.username if user and user.username else submitted_student_id
        form = LoginForm(request, data={
            'username': auth_username,
            'password': password,
        })

        if form.is_valid():
            authenticated_user = form.get_user()
            login(request, authenticated_user)
            messages.success(request, 'Login successful!')
            return redirect('dashboard')

        if user and user.check_password(password):
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('dashboard')

        if user and user.password == password:
            user.set_password(password)
            if not user.username:
                user.username = user.student_id or user.email
            user.save(update_fields=['password', 'username'])
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('dashboard')

        if not user:
            form.add_error('username', 'No account found for that Student ID, username, or email.')
        else:
            form.add_error('password', 'Invalid student ID or password.')

        if not form.errors:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

@never_cache
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # Create associated records
                StudentSkillProfile.objects.create(student=user)
                StudentReport.objects.create(student=user)
                
                messages.success(request, 'Registration successful! Please login.')
                return redirect('login')
            except IntegrityError:
                messages.error(request, 'Registration failed. Student ID or email already exists. Please use different values.')
                form.add_error(None, 'Database error: Student ID or email already taken.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required(login_url='login')
def dashboard(request):
    """Main dashboard for student"""
    student = request.user

    if student.is_staff:
        return redirect('counselor_dashboard')
    
    # Get assessment status
    assessment = StudentAssessment.objects.filter(student=student).order_by('-started_at', '-pk').first()
    assessment_history = StudentAssessment.objects.filter(
        student=student,
        status__in=['completed', 'abandoned'],
    ).order_by('-started_at', '-pk')
    assessment_complete = bool(assessment and assessment.status == 'completed')
    
    # Get recommendations
    recommendation = CareerRecommendation.objects.filter(student=student).first() if assessment_complete else None
    
    # Get forecast
    forecast = AcademicForecast.objects.filter(student=student).first() if assessment_complete else None
    
    # Get top in-demand careers
    top_careers = InDemandCareer.objects.all()[:5]
    
    # Get skill profile
    skill_profile = StudentSkillProfile.objects.filter(student=student).first() if assessment_complete else None
    
    context = {
        'assessment': assessment,
        'assessment_history': assessment_history,
        'recommendation': recommendation,
        'forecast': forecast,
        'top_careers': top_careers,
        'skill_profile': skill_profile,
    }
    return render(request, 'dashboard.html', context)


@login_required(login_url='login')
@never_cache
def start_assessment(request):
    """Start or resume assessment"""
    student = request.user
    
    # Get or create assessment
    assessment = StudentAssessment.objects.filter(student=student, status='in_progress').order_by('-started_at').first()
    if assessment is None or not assessment.career_category:
        available_categories = get_available_assessment_categories()
        category_form = AssessmentCategoryForm(available_categories, request.POST or None)
        if request.method == 'POST' and category_form.is_valid():
            if assessment is None:
                assessment = StudentAssessment(student=student)
            assessment.career_category = category_form.cleaned_data['career_category']
            assessment.save()
            return redirect('start_assessment')
        return render(request, 'assessment/select_category.html', {
            'form': category_form,
            'available_categories': available_categories,
        })
    
    # Get first unanswered question
    answered_questions = AssessmentResponse.objects.filter(
        assessment=assessment
    ).values_list('question_id', flat=True)
    
    next_question = AssessmentQuestion.objects.filter(is_active=True).exclude(
        id__in=answered_questions
    )
    next_question = next(
        (question for question in next_question.order_by('?')
         if assessment.career_category in question.get_career_categories()),
        None,
    )
    
    if not next_question:
        # All questions answered - complete assessment
        assessment.status = 'completed'
        assessment.completed_at = datetime.now()
        assessment.total_score = calculate_assessment_score(assessment)
        assessment.save()
        
        # Generate recommendations
        generate_career_recommendations(student, assessment)
        
        messages.success(request, 'Assessment completed!')
        return redirect('assessment_results')
    
    if request.method == 'POST':
        if request.POST.get('action') == 'abandon':
            assessment.status = 'abandoned'
            assessment.save(update_fields=['status'])
            messages.info(request, 'Assessment left unfinished. Your saved answers are kept in this attempt.')
            return redirect('dashboard')

        form = AssessmentQuestionForm(next_question, request.POST)
        if form.is_valid():
            selected_option = int(form.cleaned_data['answer'])
            options = next_question.get_normalized_options()
            selected_points = {}

            if 0 <= selected_option < len(options):
                selected_points = options[selected_option].get('points', {})
            if not selected_points:
                selected_points = score_assessment_answer(next_question, selected_option)
            
            # Save response
            AssessmentResponse.objects.update_or_create(
                assessment=assessment,
                question=next_question,
                defaults={
                    'selected_option': selected_option,
                    'points_earned': json.dumps(selected_points)
                }
            )
            
            messages.success(request, f'Question {next_question.order} saved!')
            return redirect('start_assessment')
    else:
        form = AssessmentQuestionForm(next_question)
    
    total_questions = len(get_assessment_questions_for_category(assessment.career_category))
    answered_count = answered_questions.count()
    assessment_library_files = AssessmentLibraryFile.objects.filter(
        course_category=assessment.career_category,
        is_active=True,
    ).order_by('title')

    context = {
        'form': form,
        'question': next_question,
        'current_question': answered_count + 1,
        'total_questions': total_questions,
        'career_category': assessment.get_career_category_display(),
        'assessment_library_files': assessment_library_files,
    }
    return render(request, 'assessment/take_assessment.html', context)


def get_assessment_questions_for_category(career_category):
    return [
        question for question in AssessmentQuestion.objects.filter(is_active=True)
        if career_category in question.get_career_categories()
    ]


def get_available_assessment_categories():
    question_categories = {
        category
        for question in AssessmentQuestion.objects.filter(is_active=True)
        for category in question.get_career_categories()
    }
    available_path_categories = set(CareerPath.objects.values_list('category', flat=True))
    return question_categories & available_path_categories


@login_required(login_url='login')
def assessment_results(request, assessment_id=None):
    """Display assessment results"""
    student = request.user
    attempts = StudentAssessment.objects.filter(
        student=student,
        status__in=['completed', 'abandoned'],
    ).order_by('-started_at', '-pk')
    completed_attempts = attempts.filter(status='completed')
    assessment = get_object_or_404(attempts, pk=assessment_id) if assessment_id else (
        completed_attempts.first() or attempts.first()
    )
    latest_assessment = StudentAssessment.objects.filter(student=student).order_by('-started_at', '-pk').first()
    
    if not assessment:
        messages.warning(request, 'Please start an assessment first.')
        return redirect('start_assessment')
    
    is_latest_completed = assessment == latest_assessment
    recommendation = CareerRecommendation.objects.filter(student=student).first() if is_latest_completed else None
    skill_profile = StudentSkillProfile.objects.filter(student=student).first() if is_latest_completed else None
    
    context = {
        'assessment': assessment,
        'recommendation': recommendation,
        'skill_profile': skill_profile,
        'assessment_history': attempts,
    }
    return render(request, 'assessment/results.html', context)


@login_required(login_url='login')
def view_career_recommendations(request):
    """View career recommendations"""
    student = request.user
    latest_assessment = StudentAssessment.objects.filter(student=student).order_by('-started_at', '-pk').first()
    if not latest_assessment or latest_assessment.status != 'completed':
        messages.warning(request, 'Complete an assessment before viewing career recommendations.')
        return redirect('start_assessment')

    recommendation = CareerRecommendation.objects.filter(student=student).first()
    
    if not recommendation:
        messages.warning(request, 'No recommendations yet. Please complete the assessment.')
        return redirect('start_assessment')
    
    # Get related in-demand careers
    career_paths = recommendation.career_paths.all()
    related_in_demand = InDemandCareer.objects.filter(
        related_careers__in=career_paths
    ).distinct()
    
    context = {
        'recommendation': recommendation,
        'career_paths': career_paths,
        'related_in_demand': related_in_demand,
    }
    return render(request, 'career/recommendations.html', context)


@login_required(login_url='login')
@never_cache
def academic_forecast(request):
    """Generate or view academic forecast"""
    student = request.user
    latest_assessment = StudentAssessment.objects.filter(student=student).order_by('-started_at', '-pk').first()
    if not latest_assessment or latest_assessment.status != 'completed':
        messages.warning(request, 'Complete an assessment before generating an academic forecast.')
        return redirect('start_assessment')
    
    if request.method == 'POST':
        form = CareerPathSelectionForm(request.POST)
        if form.is_valid():
            selected_path = form.cleaned_data['career_path']
            
            # Generate forecast
            forecast, created = AcademicForecast.objects.update_or_create(
                student=student,
                defaults={
                    'selected_career_path': selected_path,
                    'predicted_success_rate': generate_success_prediction(student, selected_path),
                }
            )
            
            # Set improvement areas and recommended subjects
            improvement_areas = get_improvement_areas(student, selected_path)
            forecast.set_improvement_areas(improvement_areas)
            forecast.set_recommended_subjects(selected_path.get_courses())
            forecast.save()
            
            messages.success(request, 'Academic forecast generated!')
            return redirect('view_academic_forecast')
    else:
        form = CareerPathSelectionForm()
    
    context = {'form': form}
    return render(request, 'forecast/academic_forecast.html', context)


@login_required(login_url='login')
def view_academic_forecast(request):
    """View academic forecast results"""
    student = request.user
    latest_assessment = StudentAssessment.objects.filter(student=student).order_by('-started_at', '-pk').first()
    if not latest_assessment or latest_assessment.status != 'completed':
        messages.warning(request, 'Complete an assessment before viewing an academic forecast.')
        return redirect('start_assessment')

    forecast = AcademicForecast.objects.filter(student=student).first()
    
    if not forecast:
        messages.warning(request, 'No forecast yet. Please select a career path.')
        return redirect('academic_forecast')
    
    context = {
        'forecast': forecast,
        'improvement_areas': forecast.get_improvement_areas(),
        'recommended_subjects': forecast.get_recommended_subjects(),
        'required_skills': forecast.selected_career_path.get_required_skills() if forecast.selected_career_path else []
    }
    return render(request, 'forecast/forecast_results.html', context)


@login_required(login_url='login')
def qr_profile(request):
    """Display student QR profile"""
    student = request.user

    if not student.qr_code:
        student.qr_code = uuid.uuid4()
        student.save(update_fields=['qr_code'])
    
    # Get all student data
    assessment = StudentAssessment.objects.filter(student=student).order_by('-started_at', '-pk').first()
    has_completed_latest = bool(assessment and assessment.status == 'completed')
    recommendation = CareerRecommendation.objects.filter(student=student).first() if has_completed_latest else None
    forecast = AcademicForecast.objects.filter(student=student).first() if has_completed_latest else None
    qr_results_url = get_qr_results_url(request, student)
    
    context = {
        'qr_code': student.generate_qr_code(qr_results_url),
        'qr_results_url': qr_results_url,
        'assessment': assessment,
        'recommendation': recommendation,
        'forecast': forecast,
    }
    return render(request, 'profile/qr_profile.html', context)


def public_assessment_results(request, qr_code):
    """Public QR destination for a student's completed assessment results."""
    student = get_object_or_404(StudentUser, qr_code=qr_code)
    assessment = StudentAssessment.objects.filter(student=student).order_by('-started_at', '-pk').first()
    if assessment and assessment.status != 'completed':
        assessment = None
    recommendation = CareerRecommendation.objects.filter(student=student).first() if assessment else None
    forecast = AcademicForecast.objects.filter(student=student).first() if assessment else None
    skill_profile = StudentSkillProfile.objects.filter(student=student).first() if assessment else None

    response_details = []
    if assessment:
        for response in assessment.responses.select_related('question').order_by('question__order'):
            options = response.question.get_normalized_options()
            selected_answer = (
                options[response.selected_option]['text']
                if 0 <= response.selected_option < len(options)
                else 'Answer unavailable'
            )
            response_details.append({
                'response': response,
                'selected_answer': selected_answer,
                'points_earned': response.get_points_earned(),
            })

    context = {
        'student': student,
        'assessment': assessment,
        'response_details': response_details,
        'recommendation': recommendation,
        'career_paths': recommendation.career_paths.all() if recommendation else [],
        'forecast': forecast,
        'skill_profile': skill_profile,
        'skills': skill_profile.get_skills() if skill_profile else {},
        'strengths': skill_profile.get_strengths() if skill_profile else [],
        'weaknesses': skill_profile.get_weaknesses() if skill_profile else [],
        'improvement_areas': forecast.get_improvement_areas() if forecast else [],
        'recommended_subjects': forecast.get_recommended_subjects() if forecast else [],
        'forecast_required_skills': (
            forecast.selected_career_path.get_required_skills()
            if forecast and forecast.selected_career_path else []
        ),
    }
    return render(request, 'profile/public_assessment_results.html', context)


@login_required(login_url='login')
def view_in_demand_careers(request):
    """View top in-demand careers"""
    careers = InDemandCareer.objects.all()
    
    context = {'careers': careers}
    return render(request, 'career/in_demand_careers.html', context)


@login_required(login_url='login')
def job_market_matching(request):
    """Match student skills with in-demand careers"""
    student = request.user
    latest_assessment = StudentAssessment.objects.filter(student=student).order_by('-started_at', '-pk').first()
    if not latest_assessment or latest_assessment.status != 'completed':
        messages.warning(request, 'Complete an assessment before viewing personalized job matches.')
        return redirect('start_assessment')

    skill_profile = StudentSkillProfile.objects.filter(student=student).first()
    
    if not skill_profile or not skill_profile.get_skills():
        messages.warning(request, 'Please complete the assessment to see job matches.')
        return redirect('start_assessment')
    
    # Get matching careers
    all_careers = InDemandCareer.objects.all()
    matched_careers = []
    
    for career in all_careers:
        match_score = calculate_skill_match(skill_profile.get_skills(), career.required_skills)
        matched_careers.append({
            'career': career,
            'match_score': match_score,
            'required_skills': career.get_required_skills(),
        })
    
    # Sort by match score
    matched_careers.sort(key=lambda x: x['match_score'], reverse=True)
    
    context = {'matched_careers': matched_careers}
    return render(request, 'career/job_market_matching.html', context)


# ===== ADMIN/COUNSELOR VIEWS =====

@login_required(login_url='login')
def counselor_dashboard(request):
    """Counselor dashboard for monitoring students"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    # Get statistics
    total_students = StudentUser.objects.filter(is_superuser=False, is_staff=False).count()
    completed_assessments = StudentAssessment.objects.filter(status='completed').count()
    flagged_reports = StudentReport.objects.filter(is_flagged=True).count()
    
    # Get recent reports
    recent_reports = StudentReport.objects.all().order_by('-updated_at')[:10]
    
    context = {
        'total_students': total_students,
        'completed_assessments': completed_assessments,
        'flagged_reports': flagged_reports,
        'recent_reports': recent_reports,
    }
    return render(request, 'admin/counselor_dashboard.html', context)


@login_required(login_url='login')
@never_cache
def student_report(request, student_id):
    """View detailed student report"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    student = get_object_or_404(StudentUser, id=student_id)
    report = StudentReport.objects.get(student=student)
    assessment = StudentAssessment.objects.filter(student=student).order_by('-started_at', '-pk').first()
    recommendation = CareerRecommendation.objects.filter(student=student).first()
    forecast = AcademicForecast.objects.filter(student=student).first()
    
    if request.method == 'POST':
        form = CounselorNotesForm(request.POST)
        if form.is_valid():
            report.counselor_notes = form.cleaned_data['notes']
            report.is_flagged = form.cleaned_data['is_flagged']
            report.save()
            messages.success(request, 'Notes updated successfully!')
    else:
        form = CounselorNotesForm(initial={
            'notes': report.counselor_notes,
            'is_flagged': report.is_flagged,
        })
    
    context = {
        'student': student,
        'report': report,
        'assessment': assessment,
        'recommendation': recommendation,
        'forecast': forecast,
        'forecast_improvement_areas': forecast.get_improvement_areas() if forecast else [],
        'forecast_recommended_subjects': forecast.get_recommended_subjects() if forecast else [],
        'form': form,
    }
    return render(request, 'admin/student_report.html', context)


@login_required(login_url='login')
def students_list(request):
    """List all students for counselor/admin"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    students = StudentUser.objects.filter(is_superuser=False, is_staff=False).order_by('-date_joined')
    
    # Filter by assessment status
    status = request.GET.get('status')
    if status:
        if status == 'completed':
            students = students.filter(assessments__status='completed').distinct()
        elif status == 'pending':
            students = students.filter(
                Q(assessments__status='in_progress') | Q(assessments__isnull=True)
            )
    
    context = {'students': students}
    return render(request, 'admin/students_list.html', context)


@login_required(login_url='login')
@never_cache
def assessment_tests_admin(request):
    """Staff interface for managing assessment library files."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')

    library_form = AssessmentLibraryFileForm(initial={'is_active': True})

    if request.method == 'POST' and request.POST.get('form_type') == 'library_file':
        library_form = AssessmentLibraryFileForm(request.POST, request.FILES)
        if library_form.is_valid():
            library_file = library_form.save(commit=False)
            library_file.uploaded_by = request.user
            library_file.save()
            messages.success(request, f'"{library_file.title}" was added to the assessment library.')
            return redirect('/counselor/assessment-tests/')
        messages.error(request, 'Please correct the library file form below.')
    elif request.method == 'POST':
        messages.error(request, 'Adding assessment tests is disabled on this page.')
        return redirect('/counselor/assessment-tests/')

    files_by_category = {label: [] for _, label in COURSE_CATEGORY_CHOICES}
    for library_file in AssessmentLibraryFile.objects.select_related('uploaded_by'):
        files_by_category.setdefault(library_file.get_course_category_display(), []).append(library_file)

    context = {
        'library_form': library_form,
        'files_by_category': files_by_category,
        'file_count': AssessmentLibraryFile.objects.count(),
        'active_file_count': AssessmentLibraryFile.objects.filter(is_active=True).count(),
        'library_category_count': sum(bool(files) for files in files_by_category.values()),
    }
    return render(request, 'admin/assessment_tests.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
@csrf_protect
def toggle_assessment_library_file_status(request, file_id):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')

    library_file = get_object_or_404(AssessmentLibraryFile, id=file_id)
    library_file.is_active = not library_file.is_active
    library_file.save(update_fields=['is_active'])

    status_label = 'activated' if library_file.is_active else 'archived'
    messages.success(request, f'"{library_file.title}" {status_label}.')
    return redirect('/counselor/assessment-tests/')


@login_required(login_url='login')
def download_assessment_library_file(request, file_id):
    """Download an active library file for the student's selected category."""
    library_file = get_object_or_404(
        AssessmentLibraryFile,
        pk=file_id,
        is_active=True,
    )
    has_matching_assessment = StudentAssessment.objects.filter(
        student=request.user,
        status='in_progress',
        career_category=library_file.course_category,
    ).exists()
    if not has_matching_assessment:
        raise Http404('This assessment material is not available for your assessment.')

    return FileResponse(
        library_file.file.open('rb'),
        as_attachment=True,
        filename=library_file.filename,
    )


# ===== HELPER FUNCTIONS =====

def calculate_assessment_score(assessment):
    """Calculate total assessment score"""
    responses = AssessmentResponse.objects.filter(assessment=assessment)
    total_score = 0
    
    for response in responses:
        points = response.get_points_earned()
        if isinstance(points, dict):
            total_score += sum(points.values())
    
    return total_score


def generate_career_recommendations(student, assessment):
    """Generate AI-based career recommendations"""
    # Aggregate skill scores from responses
    skill_scores = {}
    responses = AssessmentResponse.objects.filter(assessment=assessment)
    
    for response in responses:
        points = response.get_points_earned()
        if isinstance(points, dict):
            for skill, score in points.items():
                skill_scores[skill] = skill_scores.get(skill, 0) + score
    
    # Find matching career paths
    career_paths = CareerPath.objects.filter(category=assessment.career_category)
    recommendations = []
    
    for path in career_paths:
        match_score = 0
        required_skills = path.get_required_skills()
        matched_skills = []
        
        for skill in required_skills:
            if skill in skill_scores:
                match_score += skill_scores[skill]
                matched_skills.append(skill)
        
        if match_score > 0:
            recommendations.append((path, match_score, matched_skills))
    
    # Sort and take top 3
    recommendations.sort(key=lambda x: (x[1], len(x[2])), reverse=True)
    top_paths = [x[0] for x in recommendations[:3]]
    
    # Calculate compatibility score
    if recommendations:
        best_match = recommendations[0][1]
        compatibility_score = min(100, (best_match / max(1, len(recommendations[0][0].get_required_skills()) * 5)) * 100)
    else:
        compatibility_score = 0
    
    # Update skill profile
    skill_profile, _ = StudentSkillProfile.objects.get_or_create(student=student)
    skill_profile.set_skills(skill_scores)
    strength_list = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)[:5]
    skill_profile.set_strengths(strength_list)
    skill_profile.save()
    
    # Create or update recommendation
    recommendation, _ = CareerRecommendation.objects.update_or_create(
        student=student,
        defaults={
            'recommendation_text': generate_recommendation_text(recommendations[:3], skill_scores),
            'compatibility_score': min(compatibility_score, 100),
        }
    )
    recommendation.career_paths.set(top_paths)


def score_assessment_answer(question, selected_option):
    """Translate an answer into career skill evidence for the recommendation engine."""
    category = question.category.lower()
    text = question.question_text.lower()
    skills_by_category = {
        'technical skills': ['Python', 'JavaScript', 'Programming', 'Problem Solving'],
        'academic skills': ['Mathematics', 'Statistics', 'Physics', 'Analytical Thinking'],
        'communication': ['Communication', 'Report Writing', 'Customer Service', 'Teaching'],
        'analytical skills': ['Analysis', 'Problem Solving', 'Critical Thinking', 'Attention to Detail'],
        'work style': ['Research', 'Analysis', 'Problem Solving'],
        'interpersonal': ['Empathy', 'Compassion', 'Customer Service', 'Teaching'],
        'stress management': ['Decision Making', 'Attention to Detail', 'Problem Solving'],
        'risk attitude': ['Risk Management', 'Innovation', 'Business Acumen'],
        'work environment': ['Organization', 'Attention to Detail', 'Compliance'],
        'mathematics': ['Mathematics', 'Statistics', 'Problem Solving'],
        'logical reasoning': ['Logical Reasoning', 'Analysis', 'Critical Thinking'],
        'language': ['Communication', 'Report Writing'],
        'verbal reasoning': ['Communication', 'Analysis'],
    }
    skills = skills_by_category.get(category, [])

    # The aptitude questions have one correct option. Give correct answers full
    # evidence and incorrect answers a small amount so the result stays useful.
    correct_answers = {
        'solve: if 5 apples': 3,
        'what is the next number': 3,
        'which word is spelled correctly': 1,
        'complete the analogy': 2,
    }
    correct_index = next((index for prompt, index in correct_answers.items() if text.startswith(prompt)), None)
    if correct_index is not None:
        value = 5 if selected_option == correct_index else 1
    else:
        # Self-ratings use the selected level (1 to 5) as evidence strength.
        value = min(5, max(1, selected_option + 1))

    return {skill: value for skill in skills}


def generate_recommendation_text(recommendations, skill_scores):
    """Explain which answer signals support the suggested career paths."""
    if not recommendations:
        return (
            'Your answers did not strongly match the skills listed for a specific career path yet. '
            'Review your skill profile and explore the available paths to find areas you would like to develop.'
        )

    strongest_skills = sorted(skill_scores.items(), key=lambda item: item[1], reverse=True)[:3]
    strength_text = ', '.join(skill for skill, _ in strongest_skills)
    path_reasons = []
    for path, _score, matched_skills in recommendations:
        path_reasons.append(f"{path.name} (matches: {', '.join(matched_skills[:3])})")

    opening = f"Your strongest assessment signals were {strength_text}. " if strength_text else ''
    return opening + 'Career paths that align with those answers: ' + '; '.join(path_reasons) + '.'


def generate_success_prediction(student, career_path):
    """Predict student's success in a career path"""
    assessment = StudentAssessment.objects.filter(student=student).order_by('-started_at', '-pk').first()
    skill_profile = StudentSkillProfile.objects.filter(student=student).first()
    
    if not assessment or not skill_profile:
        return 50.0
    
    # Calculate based on skill matching and assessment score
    base_score = 50
    
    # Add points based on skill match
    skill_match = calculate_skill_match(skill_profile.get_skills(), career_path.required_skills)
    base_score += skill_match / 2
    
    # Add points based on assessment performance
    if assessment.total_score:
        base_score += min((assessment.total_score / 1000) * 10, 20)  # Max 20 points
    
    return min(base_score, 100)


def get_improvement_areas(student, career_path):
    """Identify areas for improvement"""
    skill_profile = StudentSkillProfile.objects.filter(student=student).first()
    
    if not skill_profile:
        return career_path.get_required_skills()
    
    improvements = []
    required_skills = career_path.get_required_skills()
    student_skills = skill_profile.get_skills()
    
    for req_skill in required_skills:
        if req_skill not in student_skills or student_skills.get(req_skill, 0) < 60:
            improvements.append(req_skill)
    
    return improvements[:5]


def calculate_skill_match(student_skills, required_skills_json_str):
    """Calculate percentage match between student skills and required skills"""
    if isinstance(required_skills_json_str, str):
        import json
        try:
            required_skills = json.loads(required_skills_json_str)
        except:
            required_skills = []
    else:
        required_skills = required_skills_json_str
    
    if not required_skills:
        return 0
    
    matches = 0
    for skill in required_skills:
        if skill in student_skills:
            matches += 1
    
    return (matches / len(required_skills)) * 100
