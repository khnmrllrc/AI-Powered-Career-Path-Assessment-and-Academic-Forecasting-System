import json

from django.db import migrations, models


CAREER_CATEGORY_CHOICES = [
    ('it', 'Information Technology'), ('engineering', 'Engineering'),
    ('education', 'Education'), ('hospitality', 'Hospitality Management (BSHRM)'),
    ('entrepreneurship', 'Entrepreneurship'), ('aviation', 'Aviation (Pilot)'),
    ('psychology', 'Psychology'), ('biology', 'Biology'), ('nursing', 'Nursing'),
    ('criminology', 'Criminology'), ('physical_therapy', 'Physical Therapy'),
    ('adtech', 'Agricultural Technology (ADTech)'), ('business', 'Business'),
    ('science', 'Science'),
]

QUESTION_CAREER_CATEGORY_MAP = {
    'Technical Skills': ['it', 'engineering', 'aviation'],
    'Academic Skills': ['engineering', 'aviation', 'biology', 'nursing', 'physical_therapy', 'adtech', 'science'],
    'Communication': ['education', 'hospitality', 'entrepreneurship', 'aviation', 'psychology', 'nursing', 'criminology', 'physical_therapy', 'business'],
    'Analytical Skills': ['it', 'engineering', 'entrepreneurship', 'psychology', 'biology', 'criminology', 'adtech', 'business', 'science'],
    'Work Style': ['it', 'education', 'entrepreneurship', 'psychology', 'biology', 'adtech', 'business', 'science'],
    'Interpersonal': ['education', 'hospitality', 'psychology', 'nursing', 'physical_therapy'],
    'Stress Management': ['hospitality', 'aviation', 'nursing', 'criminology', 'physical_therapy'],
    'Risk Attitude': ['entrepreneurship', 'business', 'adtech'],
    'Work Environment': ['education', 'hospitality', 'nursing', 'criminology', 'business'],
    'Mathematics': ['engineering', 'aviation', 'biology', 'adtech', 'science'],
    'Logical Reasoning': ['it', 'engineering', 'aviation', 'criminology', 'science'],
    'Language': ['education', 'psychology', 'biology', 'business'],
    'Verbal Reasoning': ['education', 'psychology', 'criminology', 'business'],
}


def tag_existing_questions(apps, schema_editor):
    AssessmentQuestion = apps.get_model('career', 'AssessmentQuestion')
    for question in AssessmentQuestion.objects.all().iterator():
        categories = QUESTION_CAREER_CATEGORY_MAP.get(question.category, [])
        question.career_categories = json.dumps(categories)
        question.save(update_fields=['career_categories'])


class Migration(migrations.Migration):
    dependencies = [('career', '0006_allow_assessment_history')]

    operations = [
        migrations.AddField(
            model_name='assessmentquestion',
            name='career_categories',
            field=models.TextField(default='[]', help_text='JSON list of career categories this question supports'),
        ),
        migrations.AddField(
            model_name='studentassessment',
            name='career_category',
            field=models.CharField(blank=True, choices=CAREER_CATEGORY_CHOICES, default='', max_length=50),
        ),
        migrations.RunPython(tag_existing_questions, migrations.RunPython.noop),
    ]
