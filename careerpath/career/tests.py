import uuid
import base64
import qrcode
from io import BytesIO
from unittest.mock import ANY, patch

from PIL import Image
from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import (
    AcademicForecast,
    AssessmentQuestion,
    AssessmentResponse,
    CareerPath,
    CareerRecommendation,
    AssessmentLibraryFile,
    StudentAssessment,
    StudentSkillProfile,
    StudentUser,
)


class LoginViewTests(TestCase):
    def test_student_can_login_with_student_id(self):
        user = StudentUser.objects.create_user(
            username='21000123456',
            student_id='21000123456',
            email='student@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='Student',
        )

        response = self.client.post(reverse('login'), {
            'username': user.student_id,
            'password': 'TestPass123!',
        })

        self.assertRedirects(response, reverse('dashboard'))

    def test_legacy_plain_text_password_is_upgraded_on_login(self):
        user = StudentUser.objects.create(
            username='21000654321',
            student_id='21000654321',
            email='legacy@example.com',
            password='legacy123',
            first_name='Legacy',
            last_name='Student',
        )

        response = self.client.post(reverse('login'), {
            'username': user.student_id,
            'password': 'legacy123',
        })

        self.assertRedirects(response, reverse('dashboard'))
        user.refresh_from_db()
        self.assertNotEqual(user.password, 'legacy123')
        self.assertTrue(user.check_password('legacy123'))


class AssessmentHistoryTests(TestCase):
    def setUp(self):
        self.student = StudentUser.objects.create_user(
            username='21000111222',
            student_id='21000111222',
            email='history@example.com',
            password='TestPass123!',
        )
        self.abandoned = StudentAssessment.objects.create(
            student=self.student,
            status='abandoned',
            career_category='it',
        )
        self.client.force_login(self.student)

    def test_abandoned_assessment_is_shown_on_results_page(self):
        response = self.client.get(reverse('assessment_results'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Assessment Abandoned')
        self.assertContains(response, 'Abandoned')
        self.assertEqual(list(response.context['assessment_history']), [self.abandoned])

    def test_abandoned_assessment_is_shown_in_dashboard_history(self):
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Assessment History')
        self.assertEqual(list(response.context['assessment_history']), [self.abandoned])


class AssessmentLibraryTests(TestCase):
    def setUp(self):
        self.staff = StudentUser.objects.create_user(
            username='staff-library',
            student_id='staff-library',
            email='staff-library@example.com',
            password='TestPass123!',
            is_staff=True,
        )
        self.client.force_login(self.staff)

    def test_categories_without_files_are_marked_unavailable(self):
        response = self.client.get(reverse('assessment_tests_admin'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Not available at the moment.')

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_active_file_is_available_during_matching_assessment(self):
        student = StudentUser.objects.create_user(
            username='student-library',
            student_id='student-library',
            email='student-library@example.com',
            password='TestPass123!',
        )
        question = AssessmentQuestion(
            question_text='Which tool do you prefer?',
            question_type='skill',
            category='Technical Skills',
            career_categories='["it"]',
            order=1,
        )
        question.set_options(['Option A', 'Option B'])
        question.save()
        assessment = StudentAssessment.objects.create(
            student=student,
            career_category='it',
            status='in_progress',
        )
        library_file = AssessmentLibraryFile.objects.create(
            title='IT Study Guide',
            course_category='it',
            description='Review this before answering.',
            file=SimpleUploadedFile('study-guide.txt', b'study guide'),
            is_active=True,
            uploaded_by=self.staff,
        )
        self.addCleanup(lambda: library_file.file.delete(save=False))
        self.client.force_login(student)

        response = self.client.get(reverse('start_assessment'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'IT Study Guide')
        download = self.client.get(reverse('download_assessment_library_file', args=[library_file.id]))
        self.assertEqual(download.status_code, 200)
        self.assertEqual(b''.join(download.streaming_content), b'study guide')

class PublicAssessmentResultsTests(TestCase):
    def setUp(self):
        self.student = StudentUser.objects.create_user(
            username='21000987654',
            student_id='21000987654',
            email='qrstudent@example.com',
            password='TestPass123!',
            first_name='QR',
            last_name='Student',
            qr_code=uuid.uuid4(),
        )
        self.assessment = StudentAssessment.objects.create(
            student=self.student,
            status='completed',
            total_score=10,
        )
        self.question = AssessmentQuestion(
            question_text='Which activity do you enjoy most?',
            question_type='skill',
            category='IT',
            order=1,
        )
        self.question.set_options([
            {'text': 'Solving problems', 'points': {'Problem solving': 10}},
            {'text': 'Writing stories', 'points': {'Writing': 5}},
        ])
        self.question.save()
        AssessmentResponse.objects.create(
            assessment=self.assessment,
            question=self.question,
            selected_option=0,
            points_earned='{"Problem solving": 10}',
        )

        self.career_path = CareerPath.objects.create(
            name='Data Analyst',
            category='it',
            description='Analyze data to support decisions.',
            required_skills='["Problem solving"]',
            courses='["Python foundations"]',
        )
        self.recommendation = CareerRecommendation.objects.create(
            student=self.student,
            recommendation_text='Your analytical skills are a strong match.',
            compatibility_score=92.5,
        )
        self.recommendation.career_paths.add(self.career_path)

        self.skill_profile = StudentSkillProfile.objects.create(student=self.student)
        self.skill_profile.set_skills({'Problem solving': 90})
        self.skill_profile.set_strengths([['Problem solving', 90]])
        self.skill_profile.set_weaknesses(['Time management'])
        self.skill_profile.save()

        self.forecast = AcademicForecast.objects.create(
            student=self.student,
            selected_career_path=self.career_path,
            predicted_success_rate=87.5,
        )
        self.forecast.set_recommended_subjects(['Statistics'])
        self.forecast.set_improvement_areas(['Time management'])
        self.forecast.save()

    def test_qr_profile_links_to_public_results(self):
        self.client.force_login(self.student)

        response = self.client.get(reverse('qr_profile'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['qr_results_url'],
            f"http://testserver{reverse('public_assessment_results', args=[self.student.qr_code])}",
        )

    @override_settings(QR_PUBLIC_BASE_URL='https://career.example.com/')
    def test_qr_profile_uses_configured_public_url(self):
        self.client.force_login(self.student)

        response = self.client.get(reverse('qr_profile'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['qr_results_url'],
            f"https://career.example.com"
            f"{reverse('public_assessment_results', args=[self.student.qr_code])}",
        )

    @override_settings(ALLOWED_HOSTS=['[::1]'])
    @patch('career.views.get_lan_ip_address', return_value='192.168.1.25')
    def test_qr_profile_uses_network_address_for_localhost(self, _get_lan_ip_address):
        self.client.force_login(self.student)

        response = self.client.get(
            reverse('qr_profile'),
            HTTP_HOST='[::1]:8000',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['qr_results_url'],
            f"http://192.168.1.25:8000"
            f"{reverse('public_assessment_results', args=[self.student.qr_code])}",
        )

    @override_settings(ALLOWED_HOSTS=['public.example.com'])
    def test_qr_profile_keeps_https_behind_cloudflare(self):
        self.client.force_login(self.student)

        response = self.client.get(
            reverse('qr_profile'),
            HTTP_HOST='public.example.com',
            HTTP_X_FORWARDED_PROTO='https',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['qr_results_url'],
            f"https://public.example.com"
            f"{reverse('public_assessment_results', args=[self.student.qr_code])}",
        )

    def test_generated_qr_code_is_a_valid_png(self):
        target_url = (
            f"http://testserver"
            f"{reverse('public_assessment_results', args=[self.student.qr_code])}"
        )

        qr_data_uri = self.student.generate_qr_code(target_url)

        self.assertTrue(qr_data_uri.startswith('data:image/png;base64,'))
        image_data = base64.b64decode(qr_data_uri.split(',', 1)[1])
        image = Image.open(BytesIO(image_data))
        self.assertEqual(image.format, 'PNG')
        self.assertGreater(image.width, 200)
        image.verify()

    def test_generated_qr_code_encodes_the_public_results_url(self):
        """Ensure the scannable payload is the same URL shown to the student."""
        target_url = (
            'https://career.example.com'
            f"{reverse('public_assessment_results', args=[self.student.qr_code])}"
        )
        original_add_data = qrcode.QRCode.add_data

        with patch(
            'career.models.qrcode.QRCode.add_data',
            autospec=True,
            side_effect=original_add_data,
        ) as add_data:
            self.student.generate_qr_code(target_url)

        add_data.assert_called_once_with(ANY, target_url)

    def test_public_qr_results_show_full_assessment_and_forecast(self):
        response = self.client.get(
            reverse('public_assessment_results', args=[self.student.qr_code])
        )

        self.assertEqual(response.status_code, 200)
        for result in (
            'Which activity do you enjoy most?',
            'Solving problems',
            'Problem solving: 10',
            'Problem solving',
            'Time management',
            'Data Analyst',
            'Your analytical skills are a strong match.',
            'Python foundations',
            'Statistics',
            '87.5%',
        ):
            self.assertContains(response, result)

    def test_legacy_qr_url_displays_assessment_results(self):
        response = self.client.get(
            reverse('legacy_public_assessment_results', args=[self.student.qr_code])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Assessment Results')
        self.assertContains(response, 'Solving problems')
        self.assertContains(response, 'Data Analyst')
        self.assertContains(response, '87.5%')
