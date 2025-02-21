"""
URL configuration for DevLink project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.contrib import admin 
from django.contrib.auth import views as auth_views
from allauth.account import views as allauth_views
from projects import views as custom_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/register/', custom_views.register, name='register'), 
    path('accounts/logout/', auth_views.LogoutView.as_view(template_name='account/logout.html'), name='logout'), 
    path('accounts/login/', auth_views.LoginView.as_view(template_name='account/login.html'), name='login'),

    path('accounts/', include('allauth.urls')), 


    path('', include('projects.urls')),
    path('conversations/', custom_views.active_conversations, name='active_conversations'),
    
]
