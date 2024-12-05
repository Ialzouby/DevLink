# Generated by Django 5.1.3 on 2024-12-05 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_project_skills'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='skills',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='skills',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]