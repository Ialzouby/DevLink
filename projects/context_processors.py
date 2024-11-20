"""
context_processors.py
This module contains context processors  for the project. 

Functions:
    notification_processor(request): Returns unread notifications for the authenticated user.
"""

from .models import Notification

def notification_processor(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-timestamp')
        return {'notifications': notifications}
    return {}
