from django import forms
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

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

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'grade_level',
            'concentration', 'linkedin', 'github', 'bio', 'password1', 'password2'
        )


class RatingForm(forms.Form):
    rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],  # Rating from 1 to 5
        label="Rate this project",
        widget=forms.RadioSelect
    )