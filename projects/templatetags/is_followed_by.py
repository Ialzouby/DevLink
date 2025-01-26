from django import template
from projects.models import Follow

register = template.Library()

@register.filter
def is_followed_by(profile_user, current_user):
    """
    Check if current_user is following the profile_user.
    """
    if current_user.is_authenticated:
        return Follow.objects.filter(
            follower=current_user, following=profile_user
        ).exists()
    return False