# Generated by Django 5.1.3 on 2025-02-20 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0020_userprofile_profile_picture_url_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='github_link',
            field=models.URLField(max_length=2000),
        ),
        migrations.AlterField(
            model_name='project',
            name='skill_requirements',
            field=models.CharField(max_length=2000),
        ),
        migrations.AlterField(
            model_name='trainingpost',
            name='link',
            field=models.URLField(blank=True, max_length=2048, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='banner_picture_url',
            field=models.URLField(blank=True, max_length=2048, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture_url',
            field=models.URLField(blank=True, max_length=2048, null=True),
        ),
    ]
