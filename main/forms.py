from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User, UserProfile, Post


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={'accept': 'image/*'}),
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['poster', 'text']
        widgets = {
            'poster': forms.FileInput(attrs={'accept': 'image/*'}),
        }
