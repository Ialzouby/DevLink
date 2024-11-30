# Generated by Django 5.1.3 on 2024-11-30 00:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_project_completed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='topic',
            field=models.CharField(choices=[('Web Development', 'Web Development'), ('Software Engineering', 'Software Engineering'), ('AI', 'AI'), ('Data Science', 'Data Science'), ('Cybersecurity', 'Cybersecurity'), ('Robotics', 'Robotics')], max_length=100),
        ),
    ]
