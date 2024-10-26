from django.db import models
from django.contrib.auth.models import User  # For user relationships
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from cloudinary.models import CloudinaryField
from django.utils import timezone

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
    birthdate = models.DateField(null=True, blank=True)
    


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
    birthdate = models.DateField(null=True, blank=True)




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


class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Message from {self.sender} to {self.recipient} at {self.timestamp}"
    



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who receives the notification
    related_message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True)  # Message related to the notification
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)
    content = models.TextField(blank=True)

    def __str__(self):
        if self.related_message:
            return f"Notification for {self.user.username}: {self.related_message.content}"
        return f"Notification for {self.user.username}"


    def get_message_thread_url(self):
        if self.related_message:
            # Ensure the username is passed correctly from related_message's sender
            return reverse('message_thread', kwargs={'username': self.related_message.sender.username})
        return reverse('active_conversations')  # Redirect to conversations page if no message is associated

