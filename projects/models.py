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
    GRADE_LEVEL_CHOICES = [
        ('Freshman', 'Freshman'),
        ('Sophomore', 'Sophomore'),
        ('Junior', 'Junior'),
        ('Senior', 'Senior'),
        ('Graduate', 'Graduate'),
    ]

    CONCENTRATION_CHOICES = [
        ('Computer Science', 'Computer Science'),
        ('Information Technology', 'Information Technology'),
        ('Data Science', 'Data Science'),
        ('Cybersecurity', 'Cybersecurity'),
        ('Software Engineering', 'Software Engineering'),
        ('Robotics', 'Robotics'),
        ('Artificial Intelligence', 'Artificial Intelligence'),
    ]

    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    grade_level = models.CharField(max_length=50, choices=GRADE_LEVEL_CHOICES)
    concentration = models.CharField(max_length=200, choices=CONCENTRATION_CHOICES)
    linkedin = models.CharField(max_length=500, blank=True, null=True)
    github = models.CharField(max_length=500, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', max_length=255, blank=True, null=True)
    profile_picture_url = models.URLField(blank=True, null=True)
    points = models.IntegerField(default=0)
    birthdate = models.DateField(null=True, blank=True)
    skills = models.CharField(max_length=255, blank=True, null=True) 
    banner_picture = models.ImageField(
        upload_to='banner_pics/', 
        max_length=255, 
        blank=True, 
        null=True
    )
    banner_picture_url = models.URLField(blank=True, null=True)
    def is_complete(self):
        required_fields = [

            self.grade_level,
            self.concentration,
            self.bio,
        ]
        profile_picture_exists = self.profile_picture or self.profile_picture_url

    # Return True only if all required fields are filled and a profile picture exists
        return all(required_fields) and profile_picture_exists



    def __str__(self):
        return f'{self.user.username} Profile'


from django.db import models
from django.contrib.auth.models import User

class Competition(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()

    def __str__(self):
        return self.title

class TrainingRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    training_type = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.full_name} - {self.training_type}"


# Project model
class Project(models.Model):

    TOPIC_CHOICES = [
        ('Web Development', 'Web Development'),
        ('Software Engineering', 'Software Engineering'),
        ('Artificial Intelligence', 'Artificial Intelligence'),
        ('Data Science', 'Data Science'),
        ('Cybersecurity', 'Cybersecurity'),
        ('Robotics', 'Robotics'),
        ('Game Development', 'Game Development'),
        # Add more topics as need
    ]
        
    title = models.CharField(max_length=200)
    description = models.TextField()
    views = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)  
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(User, related_name='joined_projects', blank=True)
    owner = models.ForeignKey(User, related_name='owned_projects', on_delete=models.CASCADE)  # New field for project owner
    skills_gained = models.CharField(max_length=200)
    skill_requirements = models.CharField(max_length=200)
    github_link = models.URLField(max_length=200)
    topic = models.CharField(max_length=100, choices=TOPIC_CHOICES) 
    birthdate = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)  # New field to track project completion
    views = models.IntegerField(default=0)




    def __str__(self):
        return self.title
    
# JoinRequest model
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

# Message model
class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Message from {self.sender} to {self.recipient} at {self.timestamp}"
    
# Notification model
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


# models.py

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')  # Prevent duplicates

    def __str__(self):
        return f"{self.follower.username} -> {self.following.username}"


EVENT_TYPE_CHOICES = (
    ('project_created', 'Project Created'),
    ('project_joined', 'Project Joined'),
    ('project_completed', 'Project Completed'),
    ('comment_added', 'Comment Added'),
    ('followed_user', 'Followed a User'),
    # Add more event types if needed
)

class FeedItem(models.Model):
    """
    Represents one activity in the feed. 
    For example:
     - A user created a project
     - A user joined a project
     - A user completed a project
     - A user commented on a project
     - A user followed another user
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='feed_items'
    )
    event_type = models.CharField(
        max_length=50, choices=EVENT_TYPE_CHOICES
    )
    # Link to a project if the event is project-related
    project = models.ForeignKey(
        Project, null=True, blank=True, on_delete=models.SET_NULL
    )
    # Optionally store additional text describing the feed event
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"FeedItem: {self.event_type} by {self.user.username} at {self.created_at}"
    


class FeedItemLike(models.Model):
    feed_item = models.ForeignKey(
        FeedItem, on_delete=models.CASCADE, related_name='likes'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='feed_likes'
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('feed_item', 'user')  # Prevent double-liking

    def __str__(self):
        return f"{self.user.username} liked feed item #{self.feed_item.id}"
    



class FeedItemComment(models.Model):
    feed_item = models.ForeignKey(
        FeedItem, on_delete=models.CASCADE, related_name='feed_comments'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='feed_item_comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user.username} on feed item #{self.feed_item.id}"
