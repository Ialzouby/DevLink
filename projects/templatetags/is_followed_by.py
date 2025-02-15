from django import template
from projects.models import Follow, UserProfile

register = template.Library()

@register.filter
def is_followed_by(profile_user, current_user):
    """Check if the current user follows profile_user."""
    if isinstance(profile_user, UserProfile):  # Ensure it's a User instance
        profile_user = profile_user.user  # Extract User from UserProfile

    return Follow.objects.filter(follower=current_user, following=profile_user).exists()
