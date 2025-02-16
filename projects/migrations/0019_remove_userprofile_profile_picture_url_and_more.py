# Generated by Django 5.1.3 on 2025-02-16 23:35

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0018_alter_feeditem_event_type_skillendorsement'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='profile_picture_url',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image'),
        ),
    ]
