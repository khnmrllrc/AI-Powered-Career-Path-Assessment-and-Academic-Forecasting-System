"""
Management command to populate initial test data for the career assessment system.
Usage: python manage.py populate_initial_data
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from career.models import CareerPath, AssessmentQuestion, InDemandCareer
import json

class Command(BaseCommand):
    help = 'Populate initial test data for career assessment system'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Populate Career Paths
            self.stdout.write(self.style.WARNING('Populating Career Paths...'))
            self.populate_career_paths()

            # Populate Assessment Questions
            self.stdout.write(self.style.WARNING('Populating Assessment Questions...'))
            self.populate_assessment_questions()

            # Populate In-Demand Careers
            self.stdout.write(self.style.WARNING('Populating In-Demand Careers...'))
            self.populate_in_demand_careers()

            self.stdout.write(self.style.SUCCESS('✓ Initial data population completed!'))

    def populate_career_paths(self):
        """Populate career paths with skills and courses"""
        career_data = [
            {
                'name': 'Software Developer',
                'category': 'it',
                'description': 'Design and develop software applications for various platforms.',
                'required_skills': ['Python', 'JavaScript', 'Problem Solving', 'Version Control'],
                'courses': ['Data Structures', 'Web Development', 'Database Design', 'Software Engineering'],
                'success_rate': 85
            },
            {
                'name': 'Data Scientist',
                'category': 'it',
                'description': 'Analyze complex datasets and create data-driven solutions.',
                'required_skills': ['Statistics', 'Python', 'Data Analysis', 'Machine Learning'],
                'courses': ['Data Mining', 'Statistics', 'Python', 'Machine Learning', 'SQL'],
                'success_rate': 78
            },
            {
                'name': 'Mechanical Engineer',
                'category': 'engineering',
                'description': 'Design and develop mechanical systems and machines.',
                'required_skills': ['CAD', 'Physics', 'Mathematics', 'Problem Solving'],
                'courses': ['Thermodynamics', 'Fluid Mechanics', 'Machine Design', 'Materials Science'],
                'success_rate': 81
            },
            {
                'name': 'Civil Engineer',
                'category': 'engineering',
                'description': 'Design and construct infrastructure projects.',
                'required_skills': ['AutoCAD', 'Structural Analysis', 'Mathematics', 'Project Management'],
                'courses': ['Structural Analysis', 'Geotechnics', 'Hydraulics', 'Construction Management'],
                'success_rate': 79
            },
            {
                'name': 'High School Teacher',
                'category': 'education',
                'description': 'Educate students in secondary education level.',
                'required_skills': ['Communication', 'Subject Knowledge', 'Patience', 'Leadership'],
                'courses': ['Pedagogy', 'Curriculum Design', 'Educational Psychology', 'Subject Specialization'],
                'success_rate': 82
            },
            {
                'name': 'Hotel Manager',
                'category': 'hospitality',
                'description': 'Manage hotel operations and guest services.',
                'required_skills': ['Customer Service', 'Leadership', 'Problem Solving', 'Financial Management'],
                'courses': ['Hospitality Management', 'Customer Service', 'Accounting', 'Event Planning'],
                'success_rate': 76
            },
            {
                'name': 'Entrepreneur',
                'category': 'entrepreneurship',
                'description': 'Start and manage your own business.',
                'required_skills': ['Business Acumen', 'Leadership', 'Risk Management', 'Innovation'],
                'courses': ['Business Planning', 'Marketing', 'Finance', 'Entrepreneurship'],
                'success_rate': 72
            },
            {
                'name': 'Commercial Pilot',
                'category': 'aviation',
                'description': 'Operate commercial aircraft and transport passengers.',
                'required_skills': ['Technical Skills', 'Decision Making', 'Communication', 'Precision'],
                'courses': ['Aerodynamics', 'Navigation', 'Meteorology', 'Aircraft Systems'],
                'success_rate': 88
            },
            {
                'name': 'Clinical Psychologist',
                'category': 'psychology',
                'description': 'Provide mental health services and psychological counseling.',
                'required_skills': ['Empathy', 'Active Listening', 'Analysis', 'Problem Solving'],
                'courses': ['Clinical Psychology', 'Research Methods', 'Abnormal Psychology', 'Ethics'],
                'success_rate': 80
            },
            {
                'name': 'Marine Biologist',
                'category': 'biology',
                'description': 'Study marine organisms and ocean ecosystems.',
                'required_skills': ['Research', 'Scientific Method', 'Analysis', 'Field Work'],
                'courses': ['Marine Biology', 'Ecology', 'Taxonomy', 'Environmental Science'],
                'success_rate': 74
            },
            {
                'name': 'Registered Nurse',
                'category': 'nursing',
                'description': 'Provide patient care and medical support in healthcare settings.',
                'required_skills': ['Compassion', 'Medical Knowledge', 'Technical Skills', 'Attention to Detail'],
                'courses': ['Anatomy', 'Pharmacology', 'Nursing Care', 'Patient Management'],
                'success_rate': 86
            },
            {
                'name': 'Criminal Investigator',
                'category': 'criminology',
                'description': 'Investigate crimes and collect forensic evidence.',
                'required_skills': ['Analysis', 'Attention to Detail', 'Communication', 'Critical Thinking'],
                'courses': ['Forensic Science', 'Criminal Law', 'Evidence Collection', 'Investigation Techniques'],
                'success_rate': 77
            },
            {
                'name': 'Physical Therapist',
                'category': 'physical_therapy',
                'description': 'Help patients recover from injuries and improve mobility.',
                'required_skills': ['Anatomy Knowledge', 'Empathy', 'Technical Skills', 'Problem Solving'],
                'courses': ['Human Anatomy', 'Physiology', 'Exercise Science', 'Rehabilitation'],
                'success_rate': 83
            },
            {
                'name': 'Tech Entrepreneur',
                'category': 'entrepreneurship',
                'description': 'Build innovative technology-based businesses and startups.',
                'required_skills': ['Programming', 'Business Acumen', 'Innovation', 'Leadership'],
                'courses': ['Product Development', 'Business Strategy', 'Finance', 'Technology Trends'],
                'success_rate': 70
            }
        ]

        for data in career_data:
            career, created = CareerPath.objects.get_or_create(
                name=data['name'],
                defaults={
                    'category': data['category'],
                    'description': data['description'],
                    'success_rate': data['success_rate']
                }
            )
            if created:
                career.set_required_skills(data['required_skills'])
                career.set_courses(data['courses'])
                career.save()
                self.stdout.write(f'  ✓ Created: {data["name"]}')
            else:
                self.stdout.write(f'  → Skipped: {data["name"]} (already exists)')

    def populate_assessment_questions(self):
        """Populate assessment questions"""
        questions_data = [
            # Skill Questions
            {
                'question_text': 'How comfortable are you with programming languages?',
                'question_type': 'skill',
                'category': 'Technical Skills',
                'options': ['Very uncomfortable', 'Somewhat uncomfortable', 'Neutral', 'Somewhat comfortable', 'Very comfortable'],
                'order': 1
            },
            {
                'question_text': 'Rate your mathematical abilities',
                'question_type': 'skill',
                'category': 'Academic Skills',
                'options': ['Poor', 'Below Average', 'Average', 'Above Average', 'Excellent'],
                'order': 2
            },
            {
                'question_text': 'How well do you communicate orally?',
                'question_type': 'skill',
                'category': 'Communication',
                'options': ['Very poor', 'Poor', 'Average', 'Good', 'Excellent'],
                'order': 3
            },
            {
                'question_text': 'Rate your written communication skills',
                'question_type': 'skill',
                'category': 'Communication',
                'options': ['Poor', 'Below Average', 'Average', 'Above Average', 'Excellent'],
                'order': 4
            },
            {
                'question_text': 'How are your analytical skills?',
                'question_type': 'skill',
                'category': 'Analytical Skills',
                'options': ['Very weak', 'Weak', 'Average', 'Strong', 'Very strong'],
                'order': 5
            },

            # Personality Questions
            {
                'question_text': 'I prefer working independently rather than in teams',
                'question_type': 'personality',
                'category': 'Work Style',
                'options': ['Strongly disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly agree'],
                'order': 6
            },
            {
                'question_text': 'I enjoy helping others and providing support',
                'question_type': 'personality',
                'category': 'Interpersonal',
                'options': ['Strongly disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly agree'],
                'order': 7
            },
            {
                'question_text': 'I am comfortable with high-pressure situations',
                'question_type': 'personality',
                'category': 'Stress Management',
                'options': ['Strongly disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly agree'],
                'order': 8
            },
            {
                'question_text': 'I like to take risks and try new things',
                'question_type': 'personality',
                'category': 'Risk Attitude',
                'options': ['Strongly disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly agree'],
                'order': 9
            },
            {
                'question_text': 'I prefer structured and organized environments',
                'question_type': 'personality',
                'category': 'Work Environment',
                'options': ['Strongly disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly agree'],
                'order': 10
            },

            # Aptitude Questions
            {
                'question_text': 'Solve: If 5 apples cost $2, how many apples can you buy with $10?',
                'question_type': 'aptitude',
                'category': 'Mathematics',
                'options': ['10', '15', '20', '25', '30'],
                'order': 11
            },
            {
                'question_text': 'What is the next number in this sequence: 2, 4, 8, 16, ?',
                'question_type': 'aptitude',
                'category': 'Logical Reasoning',
                'options': ['20', '24', '30', '32', '40'],
                'order': 12
            },
            {
                'question_text': 'Which word is spelled correctly?',
                'question_type': 'aptitude',
                'category': 'Language',
                'options': ['Occassion', 'Occasion', 'Ocasion', 'Occassion', 'Ocassioon'],
                'order': 13
            },
            {
                'question_text': 'Complete the analogy: Dog is to Bark as Cat is to __?',
                'question_type': 'aptitude',
                'category': 'Verbal Reasoning',
                'options': ['Run', 'Jump', 'Meow', 'Sleep', 'Eat'],
                'order': 14
            }
        ]

        for data in questions_data:
            question, created = AssessmentQuestion.objects.get_or_create(
                question_text=data['question_text'],
                question_type=data['question_type'],
                defaults={
                    'category': data['category'],
                    'order': data['order'],
                    'is_active': True
                }
            )
            if created:
                question.set_options(data['options'])
                question.save()
                self.stdout.write(f'  ✓ Created: {data["question_text"][:50]}...')
            else:
                self.stdout.write(f'  → Skipped: Question already exists')

    def populate_in_demand_careers(self):
        """Populate top 20 in-demand careers"""
        careers_data = [
            {
                'rank': 1,
                'title': 'Software Engineer',
                'description': 'Design and develop computer software applications',
                'required_skills': ['Python', 'JavaScript', 'Cloud Technologies', 'API Design'],
                'average_salary': 120000,
                'job_growth': 22
            },
            {
                'rank': 2,
                'title': 'Data Scientist',
                'description': 'Analyze large datasets and create data-driven solutions',
                'required_skills': ['Python', 'Machine Learning', 'Statistics', 'SQL'],
                'average_salary': 125000,
                'job_growth': 36
            },
            {
                'rank': 3,
                'title': 'Cloud Architect',
                'description': 'Design and implement cloud computing solutions',
                'required_skills': ['AWS', 'Azure', 'Cloud Security', 'Infrastructure Design'],
                'average_salary': 135000,
                'job_growth': 28
            },
            {
                'rank': 4,
                'title': 'Cybersecurity Analyst',
                'description': 'Protect computer networks and information systems',
                'required_skills': ['Network Security', 'Penetration Testing', 'Compliance', 'Encryption'],
                'average_salary': 115000,
                'job_growth': 33
            },
            {
                'rank': 5,
                'title': 'Full Stack Developer',
                'description': 'Develop both frontend and backend of web applications',
                'required_skills': ['Frontend (Vue/React)', 'Backend (Node/Python)', 'Database Design'],
                'average_salary': 110000,
                'job_growth': 24
            },
            {
                'rank': 6,
                'title': 'DevOps Engineer',
                'description': 'Manage development and production environments',
                'required_skills': ['Docker', 'Kubernetes', 'CI/CD', 'Linux'],
                'average_salary': 118000,
                'job_growth': 30
            },
            {
                'rank': 7,
                'title': 'AI/ML Engineer',
                'description': 'Develop artificial intelligence and machine learning solutions',
                'required_skills': ['TensorFlow', 'Python', 'Deep Learning', 'Statistics'],
                'average_salary': 130000,
                'job_growth': 44
            },
            {
                'rank': 8,
                'title': 'Registered Nurse',
                'description': 'Provide patient care in healthcare settings',
                'required_skills': ['Patient Care', 'Medical Knowledge', 'Communication', 'Empathy'],
                'average_salary': 80000,
                'job_growth': 16
            },
            {
                'rank': 9,
                'title': 'Mechanical Engineer',
                'description': 'Design and develop mechanical systems and machines',
                'required_skills': ['CAD', 'Physics', 'Problem Solving', 'Materials Science'],
                'average_salary': 95000,
                'job_growth': 9
            },
            {
                'rank': 10,
                'title': 'UX/UI Designer',
                'description': 'Design user interfaces and experiences for digital products',
                'required_skills': ['Figma', 'User Research', 'Wireframing', 'CSS/HTML'],
                'average_salary': 105000,
                'job_growth': 13
            },
            {
                'rank': 11,
                'title': 'Database Administrator',
                'description': 'Manage and maintain database systems',
                'required_skills': ['SQL', 'Database Design', 'Backup Recovery', 'Performance Tuning'],
                'average_salary': 105000,
                'job_growth': 8
            },
            {
                'rank': 12,
                'title': 'IT System Administrator',
                'description': 'Manage and maintain computer systems and networks',
                'required_skills': ['Linux/Windows', 'Networking', 'System Security', 'Troubleshooting'],
                'average_salary': 85000,
                'job_growth': 5
            },
            {
                'rank': 13,
                'title': 'Blockchain Developer',
                'description': 'Develop blockchain and cryptocurrency applications',
                'required_skills': ['Solidity', 'Smart Contracts', 'Cryptography', 'Web3'],
                'average_salary': 140000,
                'job_growth': 32
            },
            {
                'rank': 14,
                'title': 'Environmental Science Specialist',
                'description': 'Analyze and protect environmental systems',
                'required_skills': ['Data Analysis', 'Environmental Science', 'Field Research', 'Report Writing'],
                'average_salary': 75000,
                'job_growth': 8
            },
            {
                'rank': 15,
                'title': 'Product Manager',
                'description': 'Lead product development and strategy',
                'required_skills': ['Leadership', 'Market Analysis', 'Communication', 'Agile Methodologies'],
                'average_salary': 120000,
                'job_growth': 6
            },
            {
                'rank': 16,
                'title': 'Solutions Architect',
                'description': 'Design enterprise technology solutions',
                'required_skills': ['System Design', 'Technical Leadership', 'Cloud Platforms', 'Architecture'],
                'average_salary': 130000,
                'job_growth': 7
            },
            {
                'rank': 17,
                'title': 'Quality Assurance Engineer',
                'description': 'Test and ensure software quality and functionality',
                'required_skills': ['Testing Frameworks', 'Automation', 'Bug Tracking', 'SQL'],
                'average_salary': 90000,
                'job_growth': 12
            },
            {
                'rank': 18,
                'title': 'Mobile App Developer',
                'description': 'Develop applications for mobile devices',
                'required_skills': ['React Native/Flutter', 'Mobile UI', 'API Integration', 'Performance'],
                'average_salary': 105000,
                'job_growth': 18
            },
            {
                'rank': 19,
                'title': 'Network Engineer',
                'description': 'Design and maintain computer networks',
                'required_skills': ['Cisco', 'Network Design', 'Routing/Switching', 'Security Protocols'],
                'average_salary': 95000,
                'job_growth': 6
            },
            {
                'rank': 20,
                'title': 'Digital Marketing Specialist',
                'description': 'Develop and implement digital marketing strategies',
                'required_skills': ['SEO/SEM', 'Social Media', 'Analytics', 'Content Strategy'],
                'average_salary': 70000,
                'job_growth': 10
            }
        ]

        for data in careers_data:
            career, created = InDemandCareer.objects.get_or_create(
                rank=data['rank'],
                defaults={
                    'title': data['title'],
                    'description': data['description'],
                    'average_salary': data['average_salary'],
                    'job_growth': data['job_growth']
                }
            )
            if created:
                career.set_required_skills(data['required_skills'])
                career.save()
                self.stdout.write(f'  ✓ Created Rank #{data["rank"]}: {data["title"]}')
            else:
                self.stdout.write(f'  → Skipped: Rank #{data["rank"]} already exists')
