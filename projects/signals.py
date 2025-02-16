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
from django.urls import reverse 

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
        content=(
            f"<a href='{reverse('profile', kwargs={'username': user_requesting.username})}' "
            f"class='username-link'>{user_requesting.username}</a> has requested to join your project "
            f"'<strong>{instance.project.title}</strong>'"
        )
    )

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import (
    UserProfile, 
    Project, 
    Comment, 
    Message, 
    JoinRequest, 
    Notification, 
    FeedItem
)
from .models import Follow  # if you have a Follow model for user follow events

User = get_user_model()


@receiver(post_save, sender=Project)
def create_feeditem_for_project_creation(sender, instance, created, **kwargs):
    """
    When a Project is created, create a feed item
    for the owner's 'project_created' event.
    """
    if created:
        FeedItem.objects.create(
            user=instance.owner,
            event_type='project_created',
            project=instance,
            content=f"{instance.owner.username} created a new project: {instance.title}",
        )


@receiver(m2m_changed, sender=Project.members.through)
def create_feeditem_for_project_join(sender, instance, action, pk_set, **kwargs):
    """
    When a user joins a project (via M2M 'post_add'),
    create a feed item for each user who joined.
    """
    if action == 'post_add':
        for user_id in pk_set:
            user_obj = User.objects.get(id=user_id)
            # Create feed item for user joining project
            FeedItem.objects.create(
                user=user_obj,
                event_type='project_joined',
                project=instance,
                content=f"{user_obj.username} joined project: {instance.title}",
            )


@receiver(post_save, sender=Project)
def create_feeditem_for_project_completion(sender, instance, created, **kwargs):
    """
    If the project is newly marked completed (not on creation)
    we create a feed item. We'll detect it by checking
    if the 'completed' field changed from False to True.
    """
    if not created:  # This is an update
        # 'completed' might have changed. In practice, you'd 
        # track old vs new value, or define a separate signal/logic for toggling.
        # For simplicity, assume the user toggles completed from the view:
        if instance.completed:
            # It's newly completed
            FeedItem.objects.get_or_create(
                user=instance.owner,
                event_type='project_completed',
                project=instance,
                content=f"{instance.owner.username} marked project '{instance.title}' as completed.",
            )


@receiver(post_save, sender=Comment)
def create_feeditem_for_comment(sender, instance, created, **kwargs):
    """
    When a user comments on a project, create a feed item
    for that user with 'comment_added' event.
    """
    if created:
        FeedItem.objects.create(
            user=instance.user,
            event_type='comment_added',
            project=instance.project,
            content=f"{instance.user.username} commented on '{instance.project.title}': {instance.content}",
        )


@receiver(post_save, sender=Follow)
def create_feeditem_for_follow(sender, instance, created, **kwargs):
    """
    When a user follows another user, create feed item.
    """
    if created:
        follower = instance.follower
        following = instance.following
        FeedItem.objects.create(
            user=follower,
            event_type='followed_user',
            content=f"{follower.username} started following {following.username}",
        )


from .models import TrainingPost, FeedItem

@receiver(post_save, sender=TrainingPost)
def create_feeditem_for_training_post(sender, instance, created, **kwargs):
    """
    When a user posts in training, create a feed item
    so it appears in the main feed.
    """
    if created:
        FeedItem.objects.create(
            user=instance.user,
            event_type='training_posted',
            content=f"{instance.user.username} posted a new resource in training: '{instance.title}'",
        )




from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Follow

@receiver(post_save, sender=Follow)
def send_follow_notification(sender, instance, created, **kwargs):
    if created:
        followed_user = instance.following  # The user being followed
        follower_user = instance.follower  # The user who followed them

        subject = "You've got a new follower!"
        from_email = "DevLink <devlink.notifications@gmail.com>"
        recipient_list = [followed_user.email]

        # Load the HTML template
        html_message = render_to_string("emails/follow_notification.html", {
            "followed_user": followed_user,
            "follower_user": follower_user,
        })

        # Convert HTML to plain text (fallback for email clients that don't support HTML)
        plain_message = strip_tags(html_message)

        # Create the email message object
        email = EmailMultiAlternatives(subject, plain_message, from_email, recipient_list)
        email.attach_alternative(html_message, "text/html")  # Attach the HTML version

        # Send the email
        email.send()
