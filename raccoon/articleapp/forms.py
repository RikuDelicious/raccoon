from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.forms import ModelForm

from .models import Post, User
from .widgets import ClearableFileInput


class UserCreationForm(BaseUserCreationForm):
    class Meta(BaseUserCreationForm.Meta):
        model = User


class ProfileUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ["display_name", "profile_image"]
        widgets = {
            "profile_image": ClearableFileInput(),
        }


class AccountUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ["username"]


class PostForm(ModelForm):
    tags_text = forms.CharField(max_length=200, required=False, label="タグ")

    class Meta:
        model = Post
        fields = ["title", "slug", "tags", "body", "user"]
