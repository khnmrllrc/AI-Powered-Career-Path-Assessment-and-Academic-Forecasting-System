from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    StudentUser, StudentAssessment, AssessmentQuestion, AssessmentResponse,
    CareerPath, CareerRecommendation, AcademicForecast, InDemandCareer,
    StudentSkillProfile, StudentReport, AssessmentLibraryFile
)

@admin.register(StudentUser)
class StudentUserAdmin(UserAdmin):
    list_display = ['student_id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'date_joined']
    search_fields = ['student_id', 'username', 'email', 'first_name', 'last_name']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    ordering = ['student_id', 'username']
    fieldsets = UserAdmin.fieldsets + (
        ('Student Information', {
            'fields': ('student_id', 'middle_name', 'suffix', 'qr_code'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Student Information', {
            'fields': ('student_id', 'first_name', 'middle_name', 'last_name', 'suffix', 'email'),
        }),
    )


@admin.register(StudentAssessment)
class StudentAssessmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'status', 'total_score', 'completed_at']
    list_filter = ['status', 'completed_at']
    search_fields = ['student__student_id', 'student__email']
    readonly_fields = ['started_at', 'completed_at']


@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'question_type', 'category', 'order', 'is_active']
    list_filter = ['question_type', 'category', 'is_active']
    search_fields = ['question_text', 'category']
    ordering = ['order']


@admin.register(AssessmentLibraryFile)
class AssessmentLibraryFileAdmin(admin.ModelAdmin):
    list_display = ['title', 'course_category', 'filename', 'is_active', 'uploaded_by', 'created_at']
    list_filter = ['course_category', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'file']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['course_category', 'title']


@admin.register(AssessmentResponse)
class AssessmentResponseAdmin(admin.ModelAdmin):
    list_display = ['assessment', 'question', 'selected_option']
    search_fields = ['assessment__student__student_id', 'question__question_text']
    readonly_fields = ['assessment', 'question']


@admin.register(CareerPath)
class CareerPathAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'success_rate']
    list_filter = ['category']
    search_fields = ['name', 'description']


@admin.register(CareerRecommendation)
class CareerRecommendationAdmin(admin.ModelAdmin):
    list_display = ['student', 'compatibility_score', 'generated_at']
    search_fields = ['student__student_id', 'student__email']
    readonly_fields = ['generated_at']
    filter_horizontal = ['career_paths']


@admin.register(AcademicForecast)
class AcademicForecastAdmin(admin.ModelAdmin):
    list_display = ['student', 'selected_career_path', 'predicted_success_rate', 'forecast_date']
    list_filter = ['selected_career_path', 'forecast_date']
    search_fields = ['student__student_id', 'student__email']
    readonly_fields = ['forecast_date']


@admin.register(InDemandCareer)
class InDemandCareerAdmin(admin.ModelAdmin):
    list_display = ['rank', 'title', 'job_growth', 'average_salary']
    list_filter = ['rank', 'job_growth']
    search_fields = ['title', 'description']
    ordering = ['rank']
    filter_horizontal = ['related_careers']


@admin.register(StudentSkillProfile)
class StudentSkillProfileAdmin(admin.ModelAdmin):
    list_display = ['student']
    search_fields = ['student__student_id', 'student__email']
    readonly_fields = ['last_updated']


@admin.register(StudentReport)
class StudentReportAdmin(admin.ModelAdmin):
    list_display = ['student', 'assessment_score', 'is_flagged', 'updated_at']
    list_filter = ['is_flagged', 'created_at']
    search_fields = ['student__student_id', 'student__email']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['recommended_paths']
