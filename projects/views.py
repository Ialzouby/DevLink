from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from .models import Project, Comment, UserProfile
from .forms import RatingForm, CustomUserCreationForm


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
def project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    comments = project.comments.all().order_by('-created_at')  # Get all comments for the project
    
    if request.method == "POST":
        if "rating" in request.POST:
            form = RatingForm(request.POST)
            if form.is_valid():
                rating = int(form.cleaned_data['rating'])
                project.rating = (project.rating + rating) / 2
                project.save()
                return redirect('project', project_id=project_id)  # Redirect to the same project page
        else:
            content = request.POST.get('comment')
            if content:
                comment = Comment.objects.create(project=project, user=request.user, content=content)
                return redirect('project', project_id=project_id)  # Redirect to refresh the page

    form = RatingForm()
    context = {
        'project': project,
        'comments': comments,
        'form': form,
    }
    return render(request, 'projects/project.html', context)


# Home view
def home(request):
    projects = Project.objects.all()
    return render(request, 'projects/home.html', {'projects': projects})

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
