from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from .models import Project, Comment
from .forms import RatingForm
from django.shortcuts import render, get_object_or_404, redirect
from .models import Project, Comment
from .forms import RatingForm


from django.shortcuts import render, get_object_or_404, redirect
from .models import Project, Comment
from .forms import RatingForm

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
    return render(request, 'projects/home.html')

def register(request):
    return render(request, 'projects/register.html')
