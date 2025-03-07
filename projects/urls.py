from django.urls import path, include
from . import views
from .views import (
register, profile, network, landing_page, feed_view, like_feed_item,
comment_on_feed_item, help_page,settings_page, delete_account, training,
add_post, add_comment, like_post, add_skill, endorse_skill, delete_training_post, edit_training_post,
fetch_link_metadata, search_users2, start_chat, get_messages, send_message,
)
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

urlpatterns = [
    # --------------------------------------------------
    # Authentication (Commented Out)
    # --------------------------------------------------
    # path('register/', views.register, name='register'),
    # path('logout/', auth_views.LogoutView.as_view(template_name='projects/logout.html'), name='logout'),

    # --------------------------------------------------
    # Landing, Home, and Feed
    # --------------------------------------------------
    path('', landing_page, name='landing'),
    path('landing/', landing_page, name='landing'),
    path('home/', views.feed_view, name='home'),  # Now "home" loads the feed
    path('feed/', feed_view, name='feed'),
    path('projects/', views.home, name='projects'),  # New URL for projects
    path('topic/<str:topic>/', views.home, name='filtered_projects'),
    path('messaging/', views.active_conversations, name='active_conversations'),

    # --------------------------------------------------
    # Project Related URLs
    # --------------------------------------------------
    path('project/', views.project, name='project-list'),  # URL for listing projects
    path('project/<int:project_id>/', views.project, name='project'),  # URL for viewing a specific project
    path('create_project/', views.create_project, name='create_project'),
    path('project/<int:project_id>/toggle-status/', views.toggle_project_status, name='toggle_project_status'),
    path('project/<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('project/<int:project_id>/delete/', views.delete_project, name='delete_project'),

    # --------------------------------------------------
    # Comment Management
    # --------------------------------------------------
    path('comment/delete/<int:pk>/', views.delete_comment, name='comment-delete'),  # URL for deleting a comment

    # --------------------------------------------------
    # Profile and User Account
    # --------------------------------------------------
    path('profile/<str:username>/', profile, name='profile'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/upload-banner/', views.upload_banner, name='upload_banner'),
    path('delete-account/', delete_account, name='delete_account'),

    # --------------------------------------------------
    # Network, Search, and Follow/Unfollow
    # --------------------------------------------------
    path('network/', network, name='network'),
    path('search_users/', views.search_users, name='search_users'),
    path('check-username-email/', views.check_username_email, name='check_username_email'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),

    # --------------------------------------------------
    # Messaging and Conversations
    # --------------------------------------------------
    #path('messages/<str:username>/', views.message_thread, name='message_thread'),
    ##path('messages/start/<str:username>/', views.message_thread, name='start_message'),
    #path('message-thread-partial/<str:recipient_username>/', views.message_thread_partial, name='message_thread_partial'),
    #path('conversations/', views.active_conversations, name='active_conversations'),
path('messaging/', views.active_conversations, name='active_conversations'),

    path('messaging/chat/<int:chat_id>/send/', views.send_message, name='send_message'),
    path('conversations/', views.active_conversations, name='active_conversations'),
    path('conversations/<int:chat_id>/messages/', views.load_chat_messages, name='load_chat_messages'),
    path('conversations/<int:chat_id>/send/', views.send_message, name='send_message'),
    path('search_users2/', search_users2, name='search_users2'),
    path('start_chat/', start_chat, name='start_chat'),  # For starting a chat
        path('get_messages/<int:chat_id>/', get_messages, name='get_messages'),
    path('send_message/', send_message, name='send_message'),

    # --------------------------------------------------
    # Notifications
    # --------------------------------------------------
    path('notifications/', views.notifications_view, name='notifications_view'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('notification/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),

    # --------------------------------------------------
    # Help, Settings, and Account Management
    # --------------------------------------------------
    path('help/', help_page, name='help'),
    path('settings/', settings_page, name='settings'),

    # --------------------------------------------------
    # Feed Actions
    # --------------------------------------------------
    path('feed/<int:feed_item_id>/like/', like_feed_item, name='like_feed_item'),
    path('feed/<int:feed_item_id>/comment/', comment_on_feed_item, name='comment_on_feed_item'),

    # --------------------------------------------------
    # Training Module
    # --------------------------------------------------
    path("training/", training, name="training"),
    path("training/add_post/", add_post, name="add_post"),
    path("training/comment/<int:post_id>/", add_comment, name="add_comment"),
    path("training/like/<int:post_id>/", like_post, name="like_post"),
    path('training/delete/<int:post_id>/', delete_training_post, name='delete_training_post'),
    path('training/edit/<int:post_id>/', edit_training_post, name='edit_training_post'),
    

    # --------------------------------------------------
    # Skill Management
    # --------------------------------------------------
    path('profile/<str:username>/add-skill/', add_skill, name='add_skill'),
    path('profile/<str:username>/endorse-skill/', endorse_skill, name='endorse_skill'),
    path("endorse-skill/<str:username>/", endorse_skill, name="endorse_skill"),
    path('fetch-link-metadata/', fetch_link_metadata, name='fetch_link_metadata'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
