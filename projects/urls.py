from django.urls import path
from . import views
from .views import register, profile, network
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('profile/<str:username>/', profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='projects/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='projects/logout.html'), name='logout'), 
    path('project/', views.project, name='project-list'),  # URL for listing projects (adjust if needed)
    path('project/<int:project_id>/', views.project, name='project'),  # URL for viewing a specific project
    path('comment/delete/<int:pk>/', views.delete_comment, name='comment-delete'),  # URL for deleting a comment
    path('network/', network, name='network'),
    path('create_project/', views.create_project, name='create_project'),
    path('projects/', views.project_list, name='project_list'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)