from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.utils.timesince import timesince
from django.contrib.auth import views as auth_views
from .forms import RatingForm, CustomUserCreationForm, MessageForm, ProjectForm, UserProfileForm
from .models import Project, Comment, UserProfile, JoinRequest, Message, User, Notification, Update
from django.contrib.auth import logout

from cloudinary.uploader import upload
import cloudinary
from django.http import JsonResponse
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm 
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from .models import Follow
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from .forms import UserSettingsForm
from .models import UserProfile

@login_required
def settings_page(request):
    user_profile = request.user.userprofile

    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=user_profile)
        password_form = PasswordChangeForm(request.user, request.POST)

        if "update_settings" in request.POST:
            if form.is_valid():
                form.save()
                messages.success(request, "Your settings have been updated.")
                return redirect('settings')

        elif "change_password" in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Keep user logged in after password change
                messages.success(request, "Your password has been changed successfully.")
                return redirect('settings')
            else:
                messages.error(request, "Please correct the errors below.")

    else:
        form = UserSettingsForm(instance=user_profile)
        password_form = PasswordChangeForm(request.user)

    return render(request, 'projects/settings.html', {
        'form': form,
        'password_form': password_form
    })


from django.contrib.auth import logout

@login_required
def delete_account(request):
    if request.method == 'POST':
        confirm_username = request.POST.get('confirm_username', '').strip().lower()  # Normalize input
        actual_username = request.user.username.strip().lower()  # Normalize stored username
        
        print(f"Entered Username: {confirm_username}")  # Debugging
        print(f"Actual Username: {actual_username}")  # Debugging

        if confirm_username == actual_username:
            user = request.user
            logout(request)  # Log the user out before deletion
            user.delete()
            messages.success(request, "Your account has been deleted successfully.")
            return redirect('home')
        else:
            messages.error(request, "Username does not match. Account deletion failed.")
            return redirect('settings')

    return render(request, 'projects/settings.html')


# Profile view to display a user's profile
def profile(request, username):
    user = get_object_or_404(User, username=username)
    # Ensure UserProfile exists
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    skills_list = user_profile.skills.split(",") if user_profile.skills else []
    # Debugging: Print profile fields
    print(f"Profile Picture: {user_profile.profile_picture}")
    print(f"Google Picture URL: {user_profile.profile_picture_url}")
    return render(request, 'projects/profile.html', {
        'profile_user': user,
        'skills_list': skills_list,
    })

from django.contrib import messages

@login_required
def upload_banner(request, username):
    profile_user = get_object_or_404(UserProfile, user__username=username)
    if request.method == "POST":
        banner_picture = request.FILES.get('banner_picture')
        if banner_picture:
            try:
                # Upload the image to Cloudinary
                result = upload(banner_picture, folder="banner_pics/", overwrite=True)
                # Save the Cloudinary URL to the `banner_picture_url` field
                profile_user.banner_picture_url = result['secure_url']
                profile_user.save()
                messages.success(request, "Banner updated successfully!")
            except Exception as e:
                print(f"Error uploading to Cloudinary: {e}")
                messages.error(request, "There was an issue uploading your banner.")
        return redirect('profile', username=username)
    
# Prevent logged-in users from accessing login and register pages
def custom_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    return auth_views.LoginView.as_view(template_name='projects/login.html')(request)

@login_required
def help_page(request):
    return render(request, 'projects/help.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    current_step = request.POST.get('current_step', '1')
    current_step = int(current_step)

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the User model
            user = form.save(commit=False)
            user.save()

            # Check if a UserProfile already exists
            user_profile, created = UserProfile.objects.get_or_create(user=user)

            # Handle additional fields
            user_profile.grade_level = form.cleaned_data.get('grade_level')
            user_profile.concentration = form.cleaned_data.get('concentration')
            user_profile.linkedin = form.cleaned_data.get('linkedin')
            user_profile.github = form.cleaned_data.get('github')
            user_profile.bio = form.cleaned_data.get('bio')

            # Handle profile picture upload
            if 'profile_picture' in request.FILES:
                try:
                    result = upload(request.FILES['profile_picture'], upload_preset='ml_default')
                    user_profile.profile_picture = result['url']
                except Exception as e:
                    print(f"Error uploading to Cloudinary: {e}")
                    messages.error(request, "Issue uploading the profile picture.")

            # Save the UserProfile instance
            user_profile.save()

            user.backend = 'django.contrib.auth.backends.ModelBackend'

            # Log the user in
            login(request, user)
            return redirect('home')  # Redirect to the home page or any other page
        else:
            # Handle form errors and set the step accordingly
            if any(field in form.errors for field in ['first_name', 'last_name', 'username', 'email']):
                current_step = 1
            elif any(field in form.errors for field in ['grade_level', 'concentration']):
                current_step = 2
            elif any(field in form.errors for field in ['linkedin', 'github', 'bio', 'profile_picture', 'password1', 'password2']):
                current_step = 3
    else:
        form = CustomUserCreationForm()
        current_step = 1

    return render(request, 'projects/register.html', {
        'form': form,
        'current_step': current_step
    })


# View for a single project and handling actions like rating, commenting, and joining
@login_required
def project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    # Increment the view count
    project.views += 1
    project.save()

    comments = project.comments.all().order_by('-created_at')
    join_requests = project.join_requests.filter(status='pending')

    # Collect updates
    updates = list(Update.objects.filter(project=project).values('content', 'created_at'))

    # Add project creation date
    updates.append({
        'content': "Project created",
        'created_at': project.created_at
    })

    # Add user join events
    for member in project.members.all():
        updates.append({
            'content': f"{member.username} joined the project",
            'created_at': member.date_joined  # Assuming you have a date_joined field
        })

    # Sort updates by date
    updates.sort(key=lambda x: x['created_at'], reverse=True)

    if request.method == "POST":
        if "rating" in request.POST:
            form = RatingForm(request.POST)
            if form.is_valid():
                rating = int(form.cleaned_data['rating'])
                project.rating = (project.rating + rating) / 2
                project.save()
                return redirect('project', project_id=project_id)
        elif "comment" in request.POST:
            content = request.POST.get('comment')
            if content:
                Comment.objects.create(project=project, user=request.user, content=content)
                return redirect('project', project_id=project_id)
        elif "join_project" in request.POST:
            if project.completed:
                messages.error(request, "This project is completed and no longer accepting join requests.")
                return redirect('project', project_id=project_id)
            if request.user not in project.members.all():
                JoinRequest.objects.create(user=request.user, project=project)
                messages.success(request, "Join request sent. Awaiting approval.")
                return redirect('project', project_id=project_id)
        elif "approve_request" in request.POST:
            join_request_id = request.POST.get('approve_request')
            join_request = get_object_or_404(JoinRequest, pk=join_request_id, project=project)
            join_request.status = 'approved'
            join_request.save()
            project.members.add(join_request.user)
            
            # Add update for user joining
            Update.objects.create(
                project=project,
                content=f"{join_request.user.username} joined the project"
            )
            
            messages.success(request, f"{join_request.user.username} has been added to the project.")
            return redirect('project', project_id=project_id)
        elif "reject_request" in request.POST:
            join_request_id = request.POST.get('reject_request')
            join_request = get_object_or_404(JoinRequest, pk=join_request_id, project=project)
            join_request.status = 'rejected'
            join_request.save()
            messages.success(request, f"{join_request.user.username}'s join request has been rejected.")
            return redirect('project', project_id=project_id)

    form = RatingForm()
    is_pending_request = JoinRequest.objects.filter(user=request.user, project=project, status='pending').exists()
    context = {
        'project': project,
        'comments': comments,
        'form': form,
        'is_owner': project.members.filter(pk=request.user.pk).exists(),
        'is_pending_request': is_pending_request,
        'join_requests': join_requests if request.user == project.owner else None,
        'updates': updates,  # Add updates to context
    }
    return render(request, 'projects/project.html', context)

# Home view to display projects and topics
def home(request, topic=None):
    topics = [choice[0] for choice in Project.TOPIC_CHOICES]
    q = request.GET.get('q', '')
    date_posted = request.GET.get('date_posted')
    status = request.GET.get('status')
    concentration = request.GET.get('concentration')

    projects = Project.objects.all()

    if topic:
        projects = projects.filter(topic__icontains=topic)

    if q:
        projects = projects.filter(Q(title__icontains=q) | Q(description__icontains=q))

    # Filter by date posted
    if date_posted:
        from datetime import timedelta
        from django.utils.timezone import now
        days = int(date_posted)
        projects = projects.filter(created_at__gte=now() - timedelta(days=days))

    # Filter by status
    if status:
        if status == 'active':
            projects = projects.filter(completed=False)
        elif status == 'closed':
            projects = projects.filter(completed=True)

    # Filter by concentration
    if concentration:
        projects = projects.filter(topic=concentration)

    top_users = UserProfile.objects.order_by('-points')[:3]

    return render(request, 'projects/home.html', {
        'projects': projects,
        'topics': topics,
        'top_users': top_users,
        'selected_topic': topic,
        'search_query': q,
    })

# Network view to list all users
def network(request):
    users = User.objects.all()  # Fetch all users
    return render(request, 'projects/network.html', {'users': users})


@login_required
def toggle_project_status(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    
    if request.method == 'POST':
        project.completed = not project.completed  # Toggle the completed status
        project.save()
        return redirect('project', project_id=project.id)
    

# Delete comment view
@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk, user=request.user)  # Ensure the comment belongs to the user
    project_id = comment.project.id  # Get project ID before deleting
    comment.delete()  # Delete the comment
    messages.success(request, 'Comment deleted successfully.')
    return redirect('project', project_id=project_id)

# View to create a new project
@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user  # Set the owner to the logged-in user
            project.save()
            return redirect('home')  # Redirect to home
    else:
        form = ProjectForm()
    return render(request, 'projects/create_project.html', {'form': form})

# View to display project details
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)  # Fetch project or return 404
    return render(request, 'projects/project_detail.html', {'project': project})

# Network view with search functionality

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User

@login_required
def network(request):
    query = request.GET.get('q', '')  # Get search query
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(userprofile__grade_level__icontains=query) |
            Q(userprofile__concentration__icontains=query)
        ).order_by('-userprofile__points')  # Filter and order users
    else:
        users = User.objects.all().order_by('-userprofile__points')  # Order users by points

    # Split users into groups of 9
    group_size = 9
    groups = [users[i:i + group_size] for i in range(0, len(users), group_size)]

    return render(request, 'projects/network.html', {'groups': groups})


@login_required
def edit_profile(request):
    user_profile = request.user.userprofile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            user_profile = form.save(commit=False)

            # Handle profile picture upload
            if 'profile_picture' in request.FILES:
                try:
                    result = upload(request.FILES['profile_picture'], upload_preset='ml_default')
                    user_profile.profile_picture = result['url']
                except Exception as e:
                    print(f"Error uploading to Cloudinary: {e}")
                    messages.error(request, "There was an issue uploading your profile picture.")

            # Handle banner picture upload
            if 'banner_picture' in request.FILES:
                try:
                    result = upload(request.FILES['banner_picture'], upload_preset='ml_default')
                    user_profile.banner_picture = result['url']
                except Exception as e:
                    print(f"Error uploading banner to Cloudinary: {e}")
                    messages.error(request, "There was an issue uploading your banner picture.")

            # Save skills in comma‐separated format
            skills = form.cleaned_data.get('skills', '')
            user_profile.skills = ",".join(
                skill.strip() for skill in skills.split(",") if skill.strip()
            )

            user_profile.save()

            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile', username=request.user.username)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'projects/edit_profile.html', {'form': form})


# Message thread view for private messaging
from django.shortcuts import get_object_or_404

@login_required
def message_thread(request, username):
    # Fetch the recipient user object based on the username parameter
    recipient = get_object_or_404(User, username=username)

    # Fetch messages between the logged-in user and the recipient
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(recipient=recipient)) |
        (Q(sender=recipient) & Q(recipient=request.user))
    ).order_by('timestamp')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.sender = request.user
            new_message.recipient = recipient
            new_message.save()
            # Redirect to the same URL to avoid form resubmission issues
            return redirect('message_thread', username=recipient.username)
    else:
        form = MessageForm()

    return render(request, 'projects/message_thread.html', {
        'messages': messages,
        'recipient': recipient,
        'form': form
    })


# View to display all active conversations
@login_required
def active_conversations(request):
    sent_conversations = Message.objects.filter(sender=request.user).values('recipient').distinct()
    received_conversations = Message.objects.filter(recipient=request.user).values('sender').distinct()

    conversation_user_ids = set(
        user['recipient'] for user in sent_conversations
    ).union(
        user['sender'] for user in received_conversations
    )

    conversation_users = User.objects.filter(id__in=conversation_user_ids)

    # Handle search functionality
    search_query = request.GET.get('q', '').strip()
    search_results = []
    if search_query:
        search_results = User.objects.filter(
        Q(username__icontains=search_query) |
        Q(first_name__icontains=search_query) |
        Q(last_name__icontains=search_query)
    ).exclude(id=request.user.id)


    recipient_username = request.GET.get('recipient')
    recipient = None
    messages = []
    form = MessageForm()

    if recipient_username:
        recipient = get_object_or_404(User, username=recipient_username)
        messages = Message.objects.filter(
            (Q(sender=request.user) & Q(recipient=recipient)) |
            (Q(sender=recipient) & Q(recipient=request.user))
        ).select_related('sender', 'recipient').order_by('timestamp')[:50]  # Load the last 50 messages

        if request.method == 'POST':
            form = MessageForm(request.POST)
            if form.is_valid():
                new_message = form.save(commit=False)
                new_message.sender = request.user
                new_message.recipient = recipient
                new_message.save()
                return redirect(f'/conversations/?recipient={recipient.username}')

    return render(request, 'projects/active_conversations.html', {
        'conversation_users': conversation_users,
        'recipient': recipient,
        'messages': messages,
        'form': form,
        'search_results': search_results,  # Pass search results to template
    })


# View to render notifications
@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'projects/notifications.html', {'notifications': notifications})


# Mark a notification as read
@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')  # Redirect to notifications page

# Delete a notification
@login_required
@require_http_methods(["POST"])
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    messages.success(request, "Notification deleted successfully.")
    return redirect('notifications_view')  # Redirect to notifications page

def check_username_email(request):
    username = request.GET.get('username')
    email = request.GET.get('email')

    username_exists = User.objects.filter(username=username).exists()
    email_exists = User.objects.filter(email=email).exists()

    return JsonResponse({
        'username_exists': username_exists,
        'email_exists': email_exists,
    })


def landing_page(request):
    # Add any dynamic data to be passed to the template here
    context = {
        'title': 'Welcome to My Website',
        'features': [
            {'title': 'Collaborate easily', 'description': 'Work seamlessly with your team.'},
            {'title': 'Secure code', 'description': 'Your projects are safe with us.'},
            {'title': 'Build together', 'description': 'Join forces to create something amazing.'},
        ]
    }
    return render(request, 'projects/landing.html', context)

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully.')
        return redirect('home')  # Ensure 'home' is the correct name for your home page URL pattern

    return render(request, 'projects/confirm_delete.html', {'project': project})

@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully.')
            return redirect('project', project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'projects/edit_project.html', {'form': form, 'project': project})

def search_users(request):
    query = request.GET.get('q', '').strip()
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        ).distinct()

        results = [
            {
                'username': user.username,
                'full_name': f"{user.first_name} {user.last_name}".strip(),
            }
            for user in users
        ]
        return JsonResponse(results, safe=False)

    return JsonResponse([], safe=False)
def message_thread_partial(request, recipient_username):
    recipient = get_object_or_404(User, username=recipient_username)
    messages = Message.objects.filter(
        Q(sender=request.user, recipient=recipient) |
        Q(sender=recipient, recipient=request.user)
    ).order_by('timestamp')

    return render(request, 'projects/message_thread_partial.html', {
        'messages': messages,
        'recipient': recipient,
    })

# views.py


# --- IMPORTS --- #
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import (
    Project,
    UserProfile,
    Follow,
    FeedItem,
    FeedItemLike,
    FeedItemComment,
)

User = get_user_model()

# ----------------------------------------
# FOLLOW / UNFOLLOW VIEWS
# ----------------------------------------
@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    if user_to_follow != request.user:
        # Create follow relationship if not existing
        Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )
    return redirect('profile', username=username)


@login_required
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    if user_to_unfollow != request.user:
        # Delete the relationship if exists
        Follow.objects.filter(
            follower=request.user,
            following=user_to_unfollow
        ).delete()
    return redirect('profile', username=username)


# ----------------------------------------
# FEED VIEW
# ----------------------------------------
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import FeedItem, Follow, FeedItemLike

@login_required
def feed_view(request):
    """
    Display a feed of events based on either:
      - 'global': all feed items
      - 'following': feed items from the user itself + the users they follow
      - filters by event_type if specified
    Supports infinite scrolling with AJAX pagination.
    """
    filter_mode = request.GET.get('filter_mode', 'global')  # Default to 'global'
    event_type_filter = request.GET.get('event_type', '')  # e.g. 'project_joined', 'comment_added'

    # Base QuerySet (all feed items)
    feed_queryset = FeedItem.objects.all().order_by('-created_at')

    # 1) **Filter by 'global' or 'following' mode**
    if filter_mode == 'following':
        # Get users the current user follows
        following_user_ids = Follow.objects.filter(
            follower=request.user
        ).values_list('following_id', flat=True)

        # Include the logged-in user's own posts
        user_ids = list(following_user_ids) + [request.user.id]
        feed_queryset = feed_queryset.filter(user__id__in=user_ids)

    # 2) **Filter by event type if specified**
    if event_type_filter:
        feed_queryset = feed_queryset.filter(event_type=event_type_filter)

    # 3) **Pagination for infinite scrolling**
    page_number = request.GET.get('page', 1)
    paginator = Paginator(feed_queryset, 10)  # Show 10 feed items per page
    page_obj = paginator.get_page(page_number)

        # ✅ Fetch Recommended Users (Top 3 by points)
    top_users = (
        UserProfile.objects.all()
        .order_by("-points")[:3]  # Ensure we get only top 3 users
    )

    # ✅ Fetch Recommended Projects (if applicable)
    recommended_projects = Project.objects.filter(completed=False)[:3]


    # 4) **Precompute user-like status to fix template issue**
    for item in page_obj:
        item.user_liked = item.likes.filter(user=request.user).exists()

    # 5) **Handle AJAX requests for infinite scroll**
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        feed_data = []
        for item in page_obj:
            feed_data.append({
                'id': item.id,
                'user': item.user.username,
                'event_type': item.event_type,
                'content': item.content,
                'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'project_title': item.project.title if item.project else None,
                'likes_count': item.likes.count(),
                'comments_count': item.feed_comments.count(),
                'user_liked': item.user_liked,  # Send user-like status to frontend
            })
        return JsonResponse({
            'feed_items': feed_data,
            'has_next': page_obj.has_next(),
        })

    # 6) **Render the full template for normal page load**
    # 6) **Render the full template for normal page load**
    context = {
        'page_obj': page_obj,
        'filter_mode': filter_mode,
        'event_type_filter': event_type_filter,
        'top_users': top_users,  # ✅ Pass recommended users to the template
        'recommended_projects': recommended_projects,  # ✅ Pass recommended projects to the template
    }

    return render(request, 'projects/feeds.html', context)



# ----------------------------------------
# FEED-ITEM LIKES & COMMENTS
# ----------------------------------------
@login_required
def like_feed_item(request, feed_item_id):
    """
    Toggle like on a feed item for the logged-in user.
    If already liked, unlike it; else like it.
    """
    if request.method == 'POST':
        feed_item = get_object_or_404(FeedItem, id=feed_item_id)
        existing_like = feed_item.likes.filter(user=request.user).first()
        if existing_like:
            existing_like.delete()  # user unlikes
        else:
            feed_item.likes.create(user=request.user)
        return redirect('feed')  # or redirect back to next URL
    return HttpResponseForbidden("Invalid request")


@login_required
def comment_on_feed_item(request, feed_item_id):
    """
    Post a comment on a feed item.
    """
    if request.method == 'POST':
        feed_item = get_object_or_404(FeedItem, id=feed_item_id)
        content = request.POST.get('content', '').strip()
        if content:
            feed_item.feed_comments.create(user=request.user, content=content)
        return redirect('feed')  # or wherever you want to go after
    return HttpResponseForbidden("Invalid request")

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Competition, TrainingRegistration
from django.contrib.auth.decorators import login_required

@login_required
def competitions(request):
    competitions = Competition.objects.all().order_by("-date")
    return render(request, "projects/competitions.html", {"competitions": competitions})

@login_required
def training(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        training_type = request.POST.get("training_type")

        # Save training registration
        TrainingRegistration.objects.create(
            user=request.user,
            full_name=full_name,
            email=email,
            training_type=training_type,
        )

        messages.success(request, "You have successfully registered for the training.")
        return redirect("training")

    return render(request, "projects/training.html")
