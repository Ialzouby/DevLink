from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='projects/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='projects/logout.html'), name='logout'),
    path('project/', views.project, name='project-list'),  # URL for listing projects (adjust if needed)
    path('project/<int:project_id>/', views.project, name='project'),  # URL for viewing a specific project
    path('comment/delete/<int:pk>/', views.delete_comment, name='comment-delete'),  # URL for deleting a comment
]
