from django.contrib.auth.models import User
from django.db.models.signals import post_save, m2m_changed
from .models import UserProfile, Project, Comment, Message, JoinRequest, Notification
from allauth.socialaccount.signals import social_account_added
from allauth.socialaccount.models import SocialAccount
from django.dispatch import receiver
from django.utils import timezone
from allauth.socialaccount.signals import social_account_added, social_account_updated
from django.dispatch import receiver
from django.core.files.base import ContentFile
from .models import UserProfile
from cloudinary.uploader import upload
from django.dispatch import receiver
from django.shortcuts import redirect
from allauth.socialaccount.signals import social_account_added
import requests


from django.dispatch import receiver
from django.shortcuts import redirect
from allauth.socialaccount.signals import social_account_added, social_account_updated
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile

User = get_user_model()
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
# Signal to add points when a user joins a project
@receiver(m2m_changed, sender=Project.members.through)
def update_points_on_project_joining(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for user_id in pk_set:
            user_profile = UserProfile.objects.get(user_id=user_id)
            user_profile.points += 10  # Add points for joining a project
            user_profile.save()

# Signal to add points for creating a project
@receiver(post_save, sender=Project)
def update_points_on_project_creation(sender, instance, created, **kwargs):
    if created:
        user_profile = instance.owner.userprofile
        user_profile.points += 20  # Add points for listing a project
        user_profile.save()

# Signal to add points for commenting
@receiver(post_save, sender=Comment)
def update_points_on_comment(sender, instance, created, **kwargs):
    if created:
        user_profile = instance.user.userprofile
        user_profile.points += 5  # Add points for commenting
        user_profile.save()

# Signal to add points for having a profile picture
@receiver(post_save, sender=UserProfile)
def update_points_for_profile_picture(sender, instance, **kwargs):
    if instance.profile_picture and not instance.points >= 50:  # Add points once
        instance.points += 50  # Award points for having a profile picture
        instance.save()


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    if created:
        # Check if a notification for this message already exists
        if not Notification.objects.filter(user=instance.recipient, related_message=instance).exists():
            Notification.objects.create(
                user=instance.recipient,
                related_message=instance,
                is_read=False,
                timestamp=timezone.now()
            )

# signals.py
@receiver(post_save, sender=JoinRequest)
def notify_project_owner_on_join_request(sender, instance, created, **kwargs):
    if created:
        project_owner = instance.project.owner
        user_requesting = instance.user
        Notification.objects.create(
            user=project_owner,
            is_read=False,
            timestamp=timezone.now(),
            content=f"{user_requesting.username} has requested to join your project '{instance.project.title}'"
        )

