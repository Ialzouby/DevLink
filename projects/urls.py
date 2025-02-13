from django.urls import path, include
from . import views
from .views import register, profile, network, landing_page, feed_view, like_feed_item, comment_on_feed_item
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import help_page
from .views import settings_page, delete_account
from .views import training, add_post, add_comment, like_post

urlpatterns = [
    path('', landing_page, name='landing'),
    #path('register/', views.register, name='register'),
    path('profile/<str:username>/', profile, name='profile'),
    #path('logout/', auth_views.LogoutView.as_view(template_name='projects/logout.html'), name='logout'), 
    path('project/', views.project, name='project-list'),  # URL for listing projects (adjust if needed)
    path('project/<int:project_id>/', views.project, name='project'),  # URL for viewing a specific project
    path('comment/delete/<int:pk>/', views.delete_comment, name='comment-delete'),  # URL for deleting a comment
    path('network/', network, name='network'),
    path('create_project/', views.create_project, name='create_project'),
    path('topic/<str:topic>/', views.home, name='filtered_projects'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('messages/<str:username>/', views.message_thread, name='message_thread'),
    path('messages/start/<str:username>/', views.message_thread, name='start_message'),
    path('conversations/', views.active_conversations, name='active_conversations'),
    path('notifications/', views.notifications_view, name='notifications_view'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('notification/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('check-username-email/', views.check_username_email, name='check_username_email'),
    path('landing/', landing_page, name='landing'),
    path('home/', views.home, name='home'),
    path('project/<int:project_id>/toggle-status/', views.toggle_project_status, name='toggle_project_status'),
    path('project/<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('help/', help_page, name='help'),
    path('settings/', settings_page, name='settings'),
    path('delete-account/', delete_account, name='delete_account'),
    path('project/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    path('search_users/', views.search_users, name='search_users'),
    path('message-thread-partial/<str:recipient_username>/', views.message_thread_partial, name='message_thread_partial'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),
    path('profile/<str:username>/upload-banner/', views.upload_banner, name='upload_banner'),
    path('feed/', feed_view, name='feed'),
    path('feed/<int:feed_item_id>/like/', like_feed_item, name='like_feed_item'),
    path('feed/<int:feed_item_id>/comment/', comment_on_feed_item, name='comment_on_feed_item'),
    path("training/", training, name="training"),
    path("training/add_post/", add_post, name="add_post"),
    path("training/comment/<int:post_id>/", add_comment, name="add_comment"),
    path("training/like/<int:post_id>/", like_post, name="like_post"),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)