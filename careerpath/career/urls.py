from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.home, name='home'),
    path('branding/aclc-logo/', views.aclc_logo, name='aclc_logo'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard & Main
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Assessment
    path('assessment/start/', views.start_assessment, name='start_assessment'),
    path('assessment/results/', views.assessment_results, name='assessment_results'),
    path('assessment/results/<int:assessment_id>/', views.assessment_results, name='assessment_result_detail'),
    
    # Career Recommendations
    path('career/recommendations/', views.view_career_recommendations, name='view_career_recommendations'),
    path('career/in-demand/', views.view_in_demand_careers, name='view_in_demand_careers'),
    path('career/job-market-matching/', views.job_market_matching, name='job_market_matching'),
    
    # Academic Forecasting
    path('forecast/academic/', views.academic_forecast, name='academic_forecast'),
    path('forecast/results/', views.view_academic_forecast, name='view_academic_forecast'),
    
    # QR Profile
    path('profile/qr/', views.qr_profile, name='qr_profile'),
    path('student/<uuid:qr_code>/', views.public_assessment_results, name='legacy_public_assessment_results'),
    path('student/<uuid:qr_code>/results/', views.public_assessment_results, name='public_assessment_results'),
    
    # Counselor/Admin Routes
    path('counselor/dashboard/', views.counselor_dashboard, name='counselor_dashboard'),
    path('counselor/students/', views.students_list, name='students_list'),
    path('counselor/student/<int:student_id>/', views.student_report, name='student_report'),
    path('counselor/assessment-tests/', views.assessment_tests_admin, name='assessment_tests_admin'),
    path('counselor/assessment-tests/library/<int:file_id>/toggle/', views.toggle_assessment_library_file_status, name='toggle_assessment_library_file_status'),
]
