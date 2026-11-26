from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('career', '0005_assessmentlibraryfile')]

    operations = [
        migrations.AlterField(
            model_name='studentassessment',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessments', to='career.studentuser'),
        ),
    ]
