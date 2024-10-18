from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('project/', views.project, name='project'),
    path('project/<int:project_id>/', views.project, name='project'),
]
