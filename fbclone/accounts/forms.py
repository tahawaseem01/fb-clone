from django import forms
from .models import Post, Profile
from django.contrib.auth import get_user_model
User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image', 'video']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_pic', 'cover_pic']