# Generated by Django 5.1.1 on 2024-10-18 23:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_remove_userprofile_profile_picture_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/'),
        ),
    ]
