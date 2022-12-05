from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.forms import ModelForm

from .models import User, Post
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
    class Meta:
        model = Post
        fields = ["title", "slug", "tags", "body"]
