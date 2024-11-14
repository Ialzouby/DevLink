from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST, require_http_methods

from .forms import RatingForm, CustomUserCreationForm, MessageForm, ProjectForm, UserProfileForm
from .models import Project, Comment, UserProfile, JoinRequest, Message, User, Notification

from cloudinary.uploader import upload
import cloudinary
from django.http import JsonResponse
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm 


# Profile view to display a user's profile
def profile(request, username):
    user = get_object_or_404(User, username=username)  # Fetch the user by username or return 404
    return render(request, 'projects/profile.html', {'profile_user': user})  # Render the profile template

def register(request):
    current_step = 1  # Start at step 1 by default

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            print("Form is valid")  # Debugging statement
            user = form.save()

            cloudinary.config(
                cloud_name='dvah1m8du',
                api_key='547583998667598',
                api_secret='-hOXeuzVlg2LrLjnML7Bzm7SnHw'
            )

            if 'profile_picture' in request.FILES:
                try:
                    result = upload(request.FILES['profile_picture'], upload_preset='ml_default')
                    print("Cloudinary upload result:", result)
                    user.userprofile.profile_picture = result['url']
                    user.userprofile.save()
                except Exception as e:
                    print(f"Error uploading to Cloudinary: {e}")

            user.userprofile.grade_level = form.cleaned_data.get('grade_level')
            user.userprofile.concentration = form.cleaned_data.get('concentration')
            user.userprofile.linkedin = form.cleaned_data.get('linkedin')
            user.userprofile.github = form.cleaned_data.get('github')
            user.userprofile.bio = form.cleaned_data.get('bio')
            user.userprofile.save()

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)

            if user is not None:
                print("User authenticated successfully")  # Debugging statement
                login(request, user)
                messages.success(request, f'Account created for {username}! You are now logged in.')
                return redirect(reverse('profile', kwargs={'username': user.username}))
            else:
                print("User authentication failed")  # Debugging statement
        else:
            print(form.errors)  # Print errors for debugging
            
            # Preserve form data and set the current step for error display
            if any(field in form.errors for field in ['first_name', 'last_name', 'username', 'email']):
                current_step = 1
            elif any(field in form.errors for field in ['grade_level', 'concentration']):
                current_step = 2
            elif any(field in form.errors for field in ['linkedin', 'github', 'bio', 'profile_picture', 'password1', 'password2']):
                current_step = 3
            else:
                current_step = 1  # Ensure it stays on the first step if no specific error is found
    else:
        form = CustomUserCreationForm()

    # Don't access form.cleaned_data in GET requests or when the form is not valid
    return render(request, 'projects/register.html', {
        'form': form,
        'current_step': current_step,
        'submitted_data': {} if request.method == 'GET' else request.POST
    })



# View for a single project and handling actions like rating, commenting, and joining
@login_required
def project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)  # Fetch project or return 404
    comments = project.comments.all().order_by('-created_at')  # Get all comments, newest first
    join_requests = project.join_requests.filter(status='pending')  # Get pending join requests

    if request.method == "POST":
        if "rating" in request.POST:  # Handle rating submission
            form = RatingForm(request.POST)
            if form.is_valid():
                rating = int(form.cleaned_data['rating'])
                project.rating = (project.rating + rating) / 2  # Update project rating
                project.save()
                return redirect('project', project_id=project_id)
        elif "comment" in request.POST:  # Handle comment submission
            content = request.POST.get('comment')
            if content:
                Comment.objects.create(project=project, user=request.user, content=content)  # Create comment
                return redirect('project', project_id=project_id)
        elif "join_project" in request.POST:  # Handle join request
            if request.user not in project.members.all():
                JoinRequest.objects.create(user=request.user, project=project)  # Create join request
                messages.success(request, "Join request sent. Awaiting approval.")
                return redirect('project', project_id=project_id)
        elif "approve_request" in request.POST:  # Approve a join request
            join_request_id = request.POST.get('approve_request')
            join_request = get_object_or_404(JoinRequest, pk=join_request_id, project=project)
            join_request.status = 'approved'
            join_request.save()
            project.members.add(join_request.user)  # Add user to project members
            messages.success(request, f"{join_request.user.username} has been added to the project.")
            return redirect('project', project_id=project_id)
        elif "reject_request" in request.POST:  # Reject a join request
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
        'join_requests': join_requests if request.user == project.owner else None,  # Only for project owner
    }
    return render(request, 'projects/project.html', context)

# Home view to display projects and topics
def home(request, topic=None):
    # Define topics for the sidebar
    topics = ["Web Development", "AI", "Data Science", "Cybersecurity"]  # Example topics
    # Get the search query from the URL if it exists
    q = request.GET.get('q', '')
    # If a topic is passed through the URL, filter projects based on it and the search query if present
    if topic:
        projects = Project.objects.filter(topic__icontains=topic)
    else:
        projects = Project.objects.all().order_by('-created_at')
    # Apply search filtering if there is a search query
    if q:
        projects = projects.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q)
        )
    # Get the top 3 users based on their points
    top_users = UserProfile.objects.order_by('-points')[:3]
    # Pass the topics, filtered projects, and search query to the template
    return render(request, 'projects/home.html', {
        'projects': projects,
        'topics': topics,
        'top_users': top_users,
        'selected_topic': topic,  # Optional for highlighting the selected topic
        'search_query': q,        # To retain the search query in the template
    })

# Network view to list all users
def network(request):
    users = User.objects.all()  # Fetch all users
    return render(request, 'projects/network.html', {'users': users})

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
    return render(request, 'projects/network.html', {'users': users})

# View to edit a user's profile
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            user_profile = form.save(commit=False)
            if 'profile_picture' in request.FILES:  # Check for new profile picture
                try:
                    result = upload(request.FILES['profile_picture'], upload_preset='ml_default')
                    print("Cloudinary upload result:", result)
                    user_profile.profile_picture = result['url']
                except Exception as e:
                    print(f"Error uploading to Cloudinary: {e}")
                    messages.error(request, "Issue uploading the profile picture.")
            user_profile.save()  # Save profile updates
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile', username=request.user.username)
    else:
        form = UserProfileForm(instance=request.user.userprofile)
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
        'form': form
    })

# View to render notifications
@login_required
def notifications_view(request):
    return render(request, 'projects/notifications.html')

# Mark a notification as read
@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')  # Redirect to notifications page

# Delete a notification
@login_required
@require_http_methods(["DELETE"])
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    if notification.user == request.user:
        notification.delete()
        return JsonResponse({'success': True})  # Return success response
    return JsonResponse({'error': 'Unauthorized'}, status=403)  # Return error if unauthorized



def check_username_email(request):
    username = request.GET.get('username')
    email = request.GET.get('email')

    username_exists = User.objects.filter(username=username).exists()
    email_exists = User.objects.filter(email=email).exists()

    return JsonResponse({
        'username_exists': username_exists,
        'email_exists': email_exists,
    })
