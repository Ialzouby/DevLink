from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import UserProfile, Project, Comment

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        UserProfile.objects.get_or_create(user=instance)  # Ensure UserProfile always exists
        instance.userprofile.save()

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