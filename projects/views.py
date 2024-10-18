from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from .models import Project, Comment
from .forms import RatingForm
from django.shortcuts import render, get_object_or_404, redirect
from .models import Project, Comment
from .forms import RatingForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Comment
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import DeleteView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Comment
from django.shortcuts import render, get_object_or_404, redirect
from .models import Project, Comment
from .forms import RatingForm
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            messages.success(request, f'Account created for {user.username}! You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'projects/register.html', {'form': form})


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


def home(request):
    projects = Project.objects.all()
    return render(request, 'projects/home.html', {'projects': projects})


def register(request):
    return render(request, 'projects/register.html')


@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk, user=request.user)
    project_id = comment.project.id  # Get the associated project ID before deleting the comment
    comment.delete()
    messages.success(request, 'Comment deleted successfully.')
    return redirect('project', project_id=project_id) 