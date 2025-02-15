# middlewares.py (or wherever you store middleware)
from django.shortcuts import redirect
from django.urls import reverse
from django.shortcuts import redirect
from django.urls import reverse

from django.shortcuts import redirect
from django.urls import reverse

class RedirectAuthenticatedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Generate restricted paths inside the request context
        restricted_paths = [
            reverse('login'),  # Ensure this matches your URL name in urls.py
            reverse('register'),
        ]

        if request.user.is_authenticated and request.path in restricted_paths:
            return redirect('feed')  # Redirect authenticated users to home

        return self.get_response(request)


class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If not logged in, or it's an anonymous user, do nothing
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Excluded paths: we typically allow the user to log out 
        # and access the "edit profile" page itself—otherwise they'd get stuck.
        # Adjust or remove 'logout' if you want to block that, too.
        allowed_paths = [
            reverse('edit_profile'),  # The form to complete profile
            reverse('account_logout'), # So they can log out if they refuse
        ]

        # If the request is for an allowed path, proceed
        if request.path in allowed_paths:
            return self.get_response(request)

        # Otherwise, check if the profile is complete
        user_profile = getattr(request.user, 'userprofile', None)
        if user_profile and not user_profile.is_complete():
            # Force them to the edit page
            return redirect('edit_profile')

        # If already complete (or no profile), just proceed
        return self.get_response(request)
