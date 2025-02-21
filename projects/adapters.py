from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.contrib.auth import get_user_model

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def new_user(self, request, sociallogin):
        # Custom logic for user creation
        user = super().new_user(request, sociallogin)
        # Additional custom user processing
        return user

    def is_open_for_signup(self, request, sociallogin):
        return True  # Automatically allow signup for users logging in with Google

    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user
        if user.id:
            return  # User is already authenticated

        User = get_user_model()
        try:
            existing_user = User.objects.get(email=user.email)
            sociallogin.connect(request, existing_user)  # Link accounts
            raise ImmediateHttpResponse(redirect('/home/'))  # Redirect to home
        except User.DoesNotExist:
            pass  # Continue with signup
