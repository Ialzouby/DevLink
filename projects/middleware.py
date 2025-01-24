from django.shortcuts import redirect
from django.urls import reverse

class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Allow access to certain paths without redirection
        excluded_paths = [
            reverse('edit_profile'),
            reverse('logout'),
        ]
        if request.path in excluded_paths:
            return self.get_response(request)

        # Check if the profile is incomplete
        user_profile = getattr(request.user, 'userprofile', None)
        if user_profile and not user_profile.is_complete():
            if request.path != reverse('edit_profile'):  # Avoid infinite redirect loop
                return redirect('edit_profile')

        return self.get_response(request)
