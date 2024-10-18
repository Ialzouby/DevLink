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

    def __str__(self):
        return f'{self.user.username} Profile'


# Signal to create and save UserProfile when a User is created or updated
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


# Project model
class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    views = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)  # Add a rating field (can store decimal values)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


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
