from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Project, UserProfile
from django import forms
from .models import Message


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name',
            'style': 'width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; background-color: #333; color: #f1f1f1;'
        }),
        max_length=30,
        required=True
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name',
            'style': 'width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; background-color: #333; color: #f1f1f1;'
        }),
        max_length=30,
        required=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
            'style': 'width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; background-color: #333; color: #f1f1f1;'
        }),
        max_length=254,
        required=True
    )
    grade_level = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Grade Level',
            'style': 'width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; background-color: #333; color: #f1f1f1;'
        }),
        max_length=50,
        required=True
    )
    concentration = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Concentration',
            'style': 'width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; background-color: #333; color: #f1f1f1;'
        }),
        max_length=100,
        required=True
    )
    linkedin = forms.URLField(
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'LinkedIn URL (Optional)',
            'style': 'width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; background-color: #333; color: #f1f1f1;'
        }),
        required=False
    )
    github = forms.URLField(
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'GitHub URL (Optional)',
            'style': 'width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; background-color: #333; color: #f1f1f1;'
        }),
        required=False
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Short Bio (Optional)',
            'rows': 3,
            'style': 'width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; background-color: #333; color: #f1f1f1;'
        }),
        required=False
    )
    #Make profile_picture a required field to fix profile picture bugs
    profile_picture = forms.ImageField(required=True)
    

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'grade_level', 'concentration', 'linkedin', 'github', 'bio', 'password1', 'password2', 'profile_picture'
        )

    #validation that user uploaded required profile picture
    #def clean_profile_picture(self):
        #profile_picture = self.cleaned_data.get('profile_picture')
        #if not profile_picture:
            #raise forms.ValidationError("Please upload a profile picture.")
        #return profile_picture


class RatingForm(forms.Form):
    rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],  # Rating from 1 to 5
        label="Rate this project",
        widget=forms.RadioSelect
    )

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'topic', 'skills_gained', 'skill_requirements', 'github_link']  # Specify the fields you want in the form

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Project Description', 'rows': 4}),
            'topic': forms.Select(attrs={'class': 'form-control'}),
            'skills_gained': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Skills that can be gained'}),
            'skill_requirements': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Skill requirements'}),
            'github_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'GitHub Repository Link'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['grade_level', 'concentration', 'linkedin', 'github', 'bio', 'profile_picture']


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']  # Only content, sender and recipient are set programmatically
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type your message...'}),
        }
