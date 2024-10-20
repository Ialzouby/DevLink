from django.db import models
from django.contrib.auth.models import User  # For user relationships
from django.db.models.signals import post_save
from django.dispatch import receiver

# UserProfile model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    grade_level = models.CharField(max_length=50)
    concentration = models.CharField(max_length=100)
    linkedin = models.URLField(max_length=200, blank=True, null=True)
    github = models.URLField(max_length=200, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)  # New field for profile image
    points = models.IntegerField(default=0)
    


    def __str__(self):
        return f'{self.user.username} Profile'



# Project model
class Project(models.Model):

    TOPIC_CHOICES = [
        ('Web Development', 'Web Development'),
        ('AI', 'AI'),
        ('Data Science', 'Data Science'),
        ('Cybersecurity', 'Cybersecurity'),
        # Add more topics as needed
    ]
        
    title = models.CharField(max_length=200)
    description = models.TextField()
    views = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)  # Add a rating field (can store decimal values)
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(User, related_name='joined_projects', blank=True)
    owner = models.ForeignKey(User, related_name='owned_projects', on_delete=models.CASCADE)  # New field for project owner
    skills_gained = models.CharField(max_length=200)
    skill_requirements = models.CharField(max_length=200)
    github_link = models.URLField(max_length=200)
    topic = models.CharField(max_length=100, choices=TOPIC_CHOICES) 
    



    def __str__(self):
        return self.title
    

class JoinRequest(models.Model):
    project = models.ForeignKey(Project, related_name='join_requests', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='join_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"JoinRequest by {self.user.username} for {self.project.title}"


# Comment model
class Comment(models.Model):
    project = models.ForeignKey(Project, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Use Django's default User model
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username}'


# Update model
class Update(models.Model):
    project = models.ForeignKey(Project, related_name='updates', on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Update on {self.project.title}'
