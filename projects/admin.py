from django.contrib import admin
from .models import Project, Comment, Update
from django.contrib import admin
from .models import UserProfile
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
from .models import Notification

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class UserAdmin(admin.ModelAdmin):
    inlines = (UserProfileInline,)

# Unregister the default User model and register the customized UserAdmin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'views', 'created_at')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'content', 'created_at')

@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):
    list_display = ('project', 'content', 'created_at')

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'timestamp')
    search_fields = ('user__username', 'message')
    list_filter = ('is_read', 'timestamp')