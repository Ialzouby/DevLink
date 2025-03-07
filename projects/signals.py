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
from allauth.socialaccount.signals import social_account_added
from allauth.socialaccount.models import SocialAccount
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile
from allauth.socialaccount.signals import social_account_added, social_account_updated
from allauth.socialaccount.models import SocialAccount
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import requests
import logging
logger = logging.getLogger(__name__)

def get_google_user_info(access_token):
    url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {"alt": "json", "access_token": access_token}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return {}

from allauth.socialaccount.signals import social_account_added
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount
from django.shortcuts import redirect
import logging

logger = logging.getLogger(__name__)

@receiver(social_account_added)
def link_social_account(sender, request, sociallogin, **kwargs):
    """
    When a social account is added, link it to the existing user account if the email exists.
    If the Google account already exists for a user, handle it properly.
    """
    user = sociallogin.user
    try:
        existing_user = get_user_model().objects.get(email=user.email)
        # Check if the Google account is already linked
        if not SocialAccount.objects.filter(user=existing_user, provider='google', uid=sociallogin.account.uid).exists():
            # Link the account if not already linked
            sociallogin.connect(request, existing_user)
            logger.debug(f"Linked Google account for existing user: {existing_user.username}")
        else:
            logger.debug(f"Google account already linked for user: {existing_user.username}")

        # Redirect to home or wherever after linking
        return redirect('/home/')  # Change this to your desired redirect

    except get_user_model().DoesNotExist:
        logger.error(f"No user found with email {user.email}")
        # Handle case where user does not exist in the system (sign-up or other logic)

from allauth.socialaccount.signals import pre_social_login
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.shortcuts import redirect

from allauth.socialaccount.signals import pre_social_login
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.shortcuts import redirect

@receiver(pre_social_login)
def handle_existing_user(request, sociallogin, **kwargs):
    """
    Before the social login happens, check if the user exists and link if needed.
    """
    user = sociallogin.user
    try:
        existing_user = get_user_model().objects.get(email=user.email)
        
        # Link the social account if it's not already linked
        if not SocialAccount.objects.filter(user=existing_user, provider='google', uid=sociallogin.account.uid).exists():
            sociallogin.connect(request, existing_user)
            return redirect('/home/')  # Adjust as needed
    except get_user_model().DoesNotExist:
        # If user doesn't exist, proceed with the normal signup flow
        return None  # Allauth will continue with the usual sign-up process


import requests
from django.core.files.base import ContentFile
import logging
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.signals import social_account_added
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile
# Ensure your get_google_user_info is defined

logger = logging.getLogger(__name__)
User = get_user_model()

@receiver(social_account_added, sender=SocialAccount)
def populate_user_profile_from_google(sender, request, sociallogin, **kwargs):
    user = sociallogin.user
    access_token = sociallogin.token.token

    google_data = get_google_user_info(access_token)
    logger.info("Google Data: %s", google_data)

    google_email = google_data.get("email")
    google_first_name = google_data.get("given_name", "")
    google_last_name = google_data.get("family_name", "")
    google_picture = google_data.get("picture", "")

    # Update the User model
    if google_email and not user.email:
        user.email = google_email
    if not user.first_name:
        user.first_name = google_first_name
    if not user.last_name:
        user.last_name = google_last_name
    user.save()

    # Get or create the UserProfile
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    if not user_profile.first_name:
        user_profile.first_name = google_first_name
    if not user_profile.last_name:
        user_profile.last_name = google_last_name

    # Download and save the Google profile image into the ImageField
    if google_picture and not user_profile.profile_picture:
        try:
            response = requests.get(google_picture)
            if response.status_code == 200:
                user_profile.profile_picture.save(
                    f"{user.username}_google.jpg",
                    ContentFile(response.content),
                    save=False
                )
        except Exception as e:
            logger.error("Error fetching Google profile image: %s", e)
    
    user_profile.save()

    if created:
        send_welcome_email(user=user)



@receiver(social_account_added, sender=SocialAccount)
def google_welcome_email_on_add(sender, request, sociallogin, **kwargs):
    # This fires only once, when the user first links their Google account
    user = sociallogin.user
    if sociallogin.account.provider == "google":
        send_google_welcome_email(user)

@receiver(social_account_updated, sender=SocialAccount)
def google_welcome_email_on_update(sender, request, sociallogin, **kwargs):
    # This fires each time the user re-logs in or updates their Google account
    # If you only want it once, skip this. Or you can check if user is new somehow.
    pass

def send_google_welcome_email(user):
    # Example logic to send your own email
    subject = "Welcome to DevLink (Google Sign-up)!"
    from_email = "DevLink <devlink.notifications@gmail.com>"
    recipient_list = [user.email]  # Ensure user.email is set

    # Render a dedicated Google template or reuse your normal one
    html_message = render_to_string("emails/welcome_email.html", {"user": user})
    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(subject, plain_message, from_email, recipient_list)
    email.attach_alternative(html_message, "text/html")
    email.send()


User = get_user_model()
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        print(f"🚀 Sending welcome email to: {instance.email}")  # Debugging output

        user = instance
        subject = "Welcome to DevLink!"
        from_email = "DevLink <devlink.notifications@gmail.com>"
        recipient_list = [user.email]

        html_message = render_to_string("emails/welcome_email.html", {"user": user})
        plain_message = strip_tags(html_message)

        email = EmailMultiAlternatives(subject, plain_message, from_email, recipient_list)
        email.attach_alternative(html_message, "text/html")

        email.send()
        print(f"✅ Welcome email sent successfully to {user.email}")  # Debugging output


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
        # Get recipient (the other user in the chat)
        recipient = instance.chat.participants.exclude(id=instance.sender.id).first()
        
        if recipient and not Notification.objects.filter(user=recipient, related_message=instance).exists():
            Notification.objects.create(
                user=recipient,
                related_message=instance,
                content=f"New message from {instance.sender.username}",
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


import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TrainingPost, FeedItem
from .utils import get_link_metadata  # ✅ Ensure you have a function to fetch metadata

logger = logging.getLogger(__name__)

@receiver(post_save, sender=TrainingPost)
def create_feeditem_for_training_post(sender, instance, created, **kwargs):
    """
    When a user posts in training, create a feed item
    so it appears in the main feed, including the post link preview.
    """
    if created:
        content = f"{instance.user.username} posted a new resource in training: '{instance.title}'"
        if instance.link:
            content += f" <a href='{instance.link}' target='_blank' class='feed-training-link'>View Resource</a>"

        # ✅ Fetch link metadata (title, description, image)
        metadata = get_link_metadata(instance.link) if instance.link else None

        logger.info(f"🔹 Training Post Created - Title: {instance.title}, Link: {instance.link}, Metadata: {metadata}")

        # ✅ Create FeedItem with the link preview
        feed_item = FeedItem.objects.create(
            user=instance.user,
            event_type='training_posted',
            content=content,
            link=instance.link,
            link_preview=metadata  # ✅ Store metadata (if available)
        )

        logger.info(f"✅ FeedItem Created - Content: {feed_item.content}, Link: {feed_item.link}, Preview: {feed_item.link_preview}")


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


from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import FeedItem, TrainingPost, TrainingLike, TrainingComment
import json

@receiver(post_save, sender=FeedItem)
def update_feed_cache_on_create(sender, instance, created, **kwargs):
    """Update cache when a new feed item is added, without deleting all cached data."""
    if created:
        cache_key = "feed_page_1"
        cached_feed = cache.get(cache_key)

        if cached_feed:
            cached_feed = json.loads(cached_feed)  # Convert from JSON
            cached_feed.insert(0, {
                "id": instance.id,
                "user": {
                    "username": instance.user.username,
                    "profile_picture": instance.user.userprofile.profile_picture.url if instance.user.userprofile.profile_picture else "https://via.placeholder.com/55",
                },
                "event_type": instance.event_type,
                "content": instance.content,
                "created_at": instance.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "likes_count": instance.likes.count(),
                "comments_count": instance.feed_comments.count(),
            })

            # Keep cache length fixed (avoid bloating cache)
            cached_feed = cached_feed[:50]  # ✅ Only keep last 50 items in cache

            # Save updated feed to cache
            cache.set(cache_key, json.dumps(cached_feed), timeout=300)  # Cache for 5 minutes

@receiver(post_save, sender=TrainingPost)
def update_training_post_cache_on_create(sender, instance, created, **kwargs):
    """Update cache when a new training post is added."""
    if created:
        cache_key = "feed_page_1"
        cached_feed = cache.get(cache_key)

        if cached_feed:
            cached_feed = json.loads(cached_feed)
            cached_feed.insert(0, {
                "id": instance.id,
                "user": {
                    "username": instance.user.username,
                    "profile_picture": instance.user.userprofile.profile_picture.url if instance.user.userprofile.profile_picture else "https://via.placeholder.com/55",
                },
                "event_type": "training_post",
                "content": instance.content,
                "created_at": instance.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "likes_count": instance.likes.count(),
                "comments_count": instance.comments.count(),
            })

            cached_feed = cached_feed[:50]
            cache.set(cache_key, json.dumps(cached_feed), timeout=300)

@receiver(post_delete, sender=FeedItem)
@receiver(post_delete, sender=TrainingPost)
def remove_deleted_post_from_cache(sender, instance, **kwargs):
    """Remove deleted feed/training post from cache instead of clearing everything."""
    cache_key = "feed_page_1"
    cached_feed = cache.get(cache_key)

    if cached_feed:
        cached_feed = json.loads(cached_feed)
        cached_feed = [item for item in cached_feed if item["id"] != instance.id]

        cache.set(cache_key, json.dumps(cached_feed), timeout=300)

@receiver(post_save, sender=Comment)
def notify_project_owner_on_comment(sender, instance, created, **kwargs):
    """
    When a user comments on a project, notify the project owner.
    """
    if created and instance.user != instance.project.owner:  # Avoid self-notification
        Notification.objects.create(
            user=instance.project.owner,  # Project owner receives the notification
            content=f"<a href='{reverse('profile', kwargs={'username': instance.user.username})}' class='username-link'>{instance.user.username}</a> commented on your project '<strong>{instance.project.title}</strong>'",
            is_read=False,
            timestamp=timezone.now()
        )
