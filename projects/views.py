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

from .forms import RatingForm, CustomUserCreationForm, MessageForm, ProjectForm, UserProfileForm
from .models import Project, Comment, UserProfile, JoinRequest, Message, User, Notification, Update

from cloudinary.uploader import upload
import cloudinary
from django.http import JsonResponse
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm 


# Profile view to display a user's profile
def profile(request, username):
    user = get_object_or_404(User, username=username)  # Fetch the user by username or return 404
    user_profile = get_object_or_404(UserProfile, user=user)  # Fetch the UserProfile object
    skills_list = user_profile.skills.split(",") if user_profile.skills else []
    
    return render(request, 'projects/profile.html', {'profile_user': user, 'skills_list': skills_list})  # Render the profile template



def register(request):
    current_step = request.POST.get('current_step', '1')
    current_step = int(current_step)

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the User model
            user = form.save(commit=False)
            user.save()
            
            # Create and save the UserProfile
            user_profile = UserProfile(user=user)
            
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
    # Define topics for the sidebar
    topics = [choice[0] for choice in Project.TOPIC_CHOICES]  
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

                                # Clean and format skills
            skills = form.cleaned_data.get('skills', '')
            user_profile.skills = ",".join(skill.strip() for skill in skills.split(",") if skill.strip())

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
