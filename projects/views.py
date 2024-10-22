from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from .models import Project, Comment, UserProfile, JoinRequest
from .forms import RatingForm, CustomUserCreationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProjectForm
from .models import Project
from .forms import ProjectForm, UserProfileForm
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import User, Message
from .forms import MessageForm
from .models import Message



# Profile view
def profile(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'projects/profile.html', {'profile_user': user})
# Register view
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)  # Add request.FILES to handle file uploads
        if form.is_valid():
            print("Form is valid")  # Debugging
            user = form.save()  # Save the user to the database

            # Manually update the UserProfile fields after it's created by the signal
            user.userprofile.grade_level = form.cleaned_data.get('grade_level')
            user.userprofile.concentration = form.cleaned_data.get('concentration')
            user.userprofile.linkedin = form.cleaned_data.get('linkedin')
            user.userprofile.github = form.cleaned_data.get('github')
            user.userprofile.bio = form.cleaned_data.get('bio')
           
            user.userprofile.save()  # Save the updated profile information
            # Save the profile picture to the UserProfile model (if the form includes profile picture field)
            profile_picture = request.FILES.get('profile_picture')
            if profile_picture:
                user.userprofile.profile_picture = profile_picture
                user.userprofile.save()

            # Log in the user immediately after registration
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                print("User authenticated successfully")  # Debugging
                login(request, user)
                messages.success(request, f'Account created for {username}! You are now logged in.')
                # Redirect to the user's profile page
                return redirect(reverse('profile', kwargs={'username': user.username}))
            else:
                print("User authentication failed")  # Debugging
        else:
            print(form.errors)  # Print form errors for debugging
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'projects/register.html', {'form': form})


# Project view

from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    comments = project.comments.all().order_by('-created_at')
    join_requests = project.join_requests.filter(status='pending')

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
        'join_requests': join_requests if request.user == project.owner else None,  # Only visible to project owner
    }
    return render(request, 'projects/project.html', context)




def home(request, topic=None):
    # Define topics for the sidebar
    topics = ["Web Development", "AI", "Data Science", "Cybersecurity"]  # Example topics

    # If a topic is passed through the URL, filter projects based on it
    if topic:
        projects = Project.objects.filter(topic__icontains=topic)
    else:
        projects = Project.objects.all().order_by('-created_at')

    # Get the top 3 users based on their points
    top_users = UserProfile.objects.order_by('-points')[:3]

    # Pass the topics and filtered projects to the template
    return render(request, 'projects/home.html', {
        'projects': projects,
        'topics': topics,
        'top_users': top_users,
        'selected_topic': topic,  # This is optional if you want to highlight the selected topic
    })


def network(request):
    users = User.objects.all()  # Fetch all users
    return render(request, 'projects/network.html', {'users': users})


# Delete comment view
@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk, user=request.user)
    project_id = comment.project.id  # Get the associated project ID before deleting the comment
    comment.delete()
    messages.success(request, 'Comment deleted successfully.')
    return redirect('project', project_id=project_id)


@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user  # Assign the logged-in user as the owner of the project
            project.save()
            return redirect('home')  # Redirect to the home page or any other desired page
    else:
        form = ProjectForm()
    return render(request, 'projects/create_project.html', {'form': form})


def project_list(request):
    # Get all unique topics from the projects
    topics = Project.objects.values_list('topic', flat=True).distinct()
    
    projects = Project.objects.all()
    return render(request, 'your_template.html', {'projects': projects, 'topics': topics})

from django.shortcuts import render, get_object_or_404
from .models import Project

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'projects/project_detail.html', {'project': project})


def network(request):
    # Fetch all users and order them by the points field in descending order
    query = request.GET.get('q', '')  # Get the search query from the request
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(userprofile__grade_level__icontains=query) |
            Q(userprofile__concentration__icontains=query)
        )
    else:
        users = User.objects.all()  # Show all users if no search query

    return render(request, 'projects/network.html', {'users': users})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile', username=request.user.username)
    else:
        form = UserProfileForm(instance=request.user.userprofile)

    return render(request, 'projects/edit_profile.html', {'form': form})


@login_required
def message_thread(request, username):
    recipient = get_object_or_404(User, username=username)
    # Fetch messages exchanged between the current user and the recipient
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(recipient=recipient)) | 
        (Q(sender=recipient) & Q(recipient=request.user))
    ).order_by('timestamp')  # Order messages by timestamp (oldest to newest)

    previous_url = request.META.get('HTTP_REFERER')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.sender = request.user
            new_message.recipient = recipient
            new_message.save()
            return redirect('message_thread', username=recipient.username)
    else:
        form = MessageForm()

    return render(request, 'projects/message_thread.html', {
        'messages': messages,
        'recipient': recipient,
        'form': form,
        'previous_url': previous_url
    })


@login_required
def active_conversations(request):
    # Get all unique users the logged-in user has had a conversation with (either as sender or recipient)
    sent_conversations = Message.objects.filter(sender=request.user).values('recipient').distinct()
    received_conversations = Message.objects.filter(recipient=request.user).values('sender').distinct()

    # Get the unique user IDs of people the logged-in user has communicated with
    conversation_user_ids = set(
        user['recipient'] for user in sent_conversations
    ).union(
        user['sender'] for user in received_conversations
    )

    # Get the actual User objects of the conversation partners
    from django.contrib.auth.models import User
    conversation_users = User.objects.filter(id__in=conversation_user_ids)

    return render(request, 'projects/active_conversations.html', {
        'conversation_users': conversation_users
    })